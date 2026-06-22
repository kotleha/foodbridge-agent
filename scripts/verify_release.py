"""Release readiness checks for the FoodBridge capstone package."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONCEPTS = {
    "ADK agent system": {
        "files": [
            "foodbridge_agent/adk_agent.py",
            "foodbridge_agent/tools.py",
        ],
        "tests": [
            "tests/test_adk_agent.py",
            "tests/test_tools.py",
        ],
    },
    "MCP Server": {
        "files": [
            "mcp_servers/recipient_directory/server.py",
        ],
        "tests": [
            "tests/test_mcp_server.py",
        ],
    },
    "Security features": {
        "files": [
            "foodbridge_agent/safety.py",
            "foodbridge_agent/state_machine.py",
            "foodbridge_agent/storage.py",
            "evals/fixtures/prompt_injection_donor_notes.json",
            "evals/fixtures/unsafe_food_rejection.json",
            "evals/fixtures/resume_approval_pending.json",
        ],
        "tests": [
            "tests/test_safety.py",
            "tests/test_workflow.py",
            "tests/test_storage.py",
            "tests/test_eval_fixtures.py",
        ],
    },
    "Agent Skill": {
        "files": [
            "skills/food-safety/SKILL.md",
            "skills/food-safety/references/mvp-rules.md",
            "skills/food-safety/references/handling-templates.md",
        ],
        "tests": [
            "tests/test_agent_skill.py",
        ],
    },
}

REQUIRED_DOCS = [
    "README.md",
    "ROADMAP.md",
    "docs/architecture.md",
    "docs/course-concepts.md",
    "docs/kaggle-writeup.md",
    "docs/judge-walkthrough.md",
    "docs/release-checklist.md",
    "docs/setup.md",
    "specs/mvp.md",
    "specs/state-machine.md",
]

REQUIRED_ASSETS = [
    "docs/assets/foodbridge-cover.svg",
    "docs/assets/foodbridge-cover.png",
    "docs/assets/dashboard-happy-path.png",
    "docs/assets/dashboard-injection-probe.png",
    "docs/assets/dashboard-mobile.png",
]

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"sk-[0-9A-Za-z]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
]

SKIP_DIRS = {
    ".codex-local",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "venv",
}

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".svg",
    ".yaml",
    ".yml",
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: list[str]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify FoodBridge release readiness.")
    parser.add_argument(
        "--skip-runtime",
        action="store_true",
        help="Skip pytest/evals/compileall and only run static release checks.",
    )
    args = parser.parse_args()

    results = [
        check_course_concepts(),
        check_required_docs(),
        check_required_assets(),
        check_writeup_word_count(),
        check_runtime_artifacts(),
        check_secret_candidates(),
    ]

    if not args.skip_runtime:
        results.extend(
            [
                run_command("pytest", [sys.executable, "-m", "pytest", "-q"]),
                run_command("evals", [sys.executable, "-m", "foodbridge_agent.evals"]),
                run_command(
                    "compileall",
                    [
                        sys.executable,
                        "-m",
                        "compileall",
                        "-q",
                        "foodbridge_agent",
                        "mcp_servers",
                        "app",
                        "tests",
                    ],
                ),
            ]
        )

    print_summary(results)
    return 0 if all(result.passed for result in results) else 1


def check_course_concepts() -> CheckResult:
    details: list[str] = []
    missing: list[str] = []
    covered = 0

    for concept, evidence in CONCEPTS.items():
        concept_missing = [
            path for path in evidence["files"] + evidence["tests"] if not (ROOT / path).exists()
        ]
        if concept_missing:
            missing.extend(f"{concept}: {path}" for path in concept_missing)
            details.append(f"{concept}: missing evidence")
        else:
            covered += 1
            details.append(f"{concept}: files and tests present")

    if covered < 3:
        missing.append(f"Only {covered} course concepts covered; at least 3 are required.")

    return CheckResult("course concepts", not missing, details + missing)


def check_required_docs() -> CheckResult:
    missing = [path for path in REQUIRED_DOCS if not (ROOT / path).exists()]
    return CheckResult(
        "required docs",
        not missing,
        [f"missing: {path}" for path in missing] or [f"{len(REQUIRED_DOCS)} docs present"],
    )


def check_required_assets() -> CheckResult:
    missing = [path for path in REQUIRED_ASSETS if not (ROOT / path).exists()]
    return CheckResult(
        "required assets",
        not missing,
        [f"missing: {path}" for path in missing] or [f"{len(REQUIRED_ASSETS)} assets present"],
    )


def check_writeup_word_count() -> CheckResult:
    path = ROOT / "docs" / "kaggle-writeup.md"
    if not path.exists():
        return CheckResult("writeup word count", False, ["docs/kaggle-writeup.md is missing"])

    text = path.read_text(encoding="utf-8")
    words = re.findall(r"\b[\w'-]+\b", text)
    count = len(words)
    return CheckResult(
        "writeup word count",
        count <= 2500,
        [f"docs/kaggle-writeup.md has {count} words; limit is 2500"],
    )


def check_runtime_artifacts() -> CheckResult:
    forbidden: list[str] = []

    for path in ROOT.rglob("*"):
        if should_skip_path(path):
            continue
        if path.is_dir() and path.name in {"__pycache__", ".pytest_cache"}:
            forbidden.append(rel(path))
        if path.is_file() and path.suffix in {".sqlite", ".sqlite3", ".db", ".pyc"}:
            forbidden.append(rel(path))
        if path.is_file() and path.name.startswith(".env"):
            forbidden.append(rel(path))

    return CheckResult(
        "runtime artifacts",
        not forbidden,
        [f"forbidden runtime artifact: {path}" for path in forbidden]
        or ["no runtime artifacts found outside local ignored workspace"],
    )


def check_secret_candidates() -> CheckResult:
    findings: list[str] = []

    for path in ROOT.rglob("*"):
        if should_skip_path(path) or not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"possible secret in {rel(path)}")
                break

    return CheckResult(
        "secret scan",
        not findings,
        findings or ["no secret-like values found in release text files"],
    )


def run_command(name: str, command: list[str]) -> CheckResult:
    env = os.environ.copy()
    if name == "pytest":
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = completed.stdout.strip().splitlines()
    tail = output[-8:] if output else ["no output"]
    return CheckResult(name, completed.returncode == 0, tail)


def print_summary(results: list[CheckResult]) -> None:
    print("FoodBridge release verification")
    print("=" * 33)

    for result in results:
        marker = "PASS" if result.passed else "FAIL"
        print(f"\n[{marker}] {result.name}")
        for detail in result.details:
            print(f"  - {detail}")


def should_skip_path(path: Path) -> bool:
    try:
        relative_parts = path.relative_to(ROOT).parts
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in relative_parts)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
