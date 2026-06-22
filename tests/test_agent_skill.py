from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "food-safety"
SKILL_FILE = SKILL_DIR / "SKILL.md"


def test_food_safety_skill_has_required_frontmatter():
    text = SKILL_FILE.read_text(encoding="utf-8")

    assert text.startswith("---\n")
    assert "name: food-safety" in text
    assert "description: Use this skill when" in text


def test_food_safety_skill_references_are_present():
    text = SKILL_FILE.read_text(encoding="utf-8")

    for reference in ["references/mvp-rules.md", "references/handling-templates.md"]:
        assert reference in text
        assert (SKILL_DIR / reference).exists()


def test_food_safety_skill_preserves_security_boundaries():
    text = SKILL_FILE.read_text(encoding="utf-8").lower()
    rules = (SKILL_DIR / "references" / "mvp-rules.md").read_text(encoding="utf-8").lower()

    assert "untrusted data" in text
    assert "never skip approval" in text
    assert "prompt-injection signals do not automatically reject" in rules
