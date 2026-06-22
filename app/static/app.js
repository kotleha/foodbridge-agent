const stateValue = document.querySelector("#state-value");
const safetyValue = document.querySelector("#safety-value");
const approvalValue = document.querySelector("#approval-value");
const safetyBadge = document.querySelector("#safety-badge");
const candidateCount = document.querySelector("#candidate-count");
const reasonList = document.querySelector("#reason-list");
const injectionBox = document.querySelector("#injection-box");
const questionBox = document.querySelector("#question-box");
const recipientList = document.querySelector("#recipient-list");
const draftMessage = document.querySelector("#draft-message");
const toolList = document.querySelector("#tool-list");
const traceList = document.querySelector("#trace-list");
const serviceStatus = document.querySelector("#service-status");
const donationForm = document.querySelector("#donation-form");
const approveButton = document.querySelector("#approve-button");
const denyButton = document.querySelector("#deny-button");
const scenarioButtons = Array.from(document.querySelectorAll(".scenario-button"));

let activeApprovalId = null;
let activePersisted = false;

async function boot() {
  try {
    const response = await fetch("/health");
    if (!response.ok) {
      throw new Error("API unavailable");
    }
    serviceStatus.textContent = "API ready";
    serviceStatus.classList.add("ok");
    await runScenario("happy_path");
  } catch (error) {
    serviceStatus.textContent = error.message;
  }
}

async function runScenario(scenario) {
  setActiveScenario(scenario);
  setBusy(true);
  try {
    const response = await fetch(`/api/demo/${scenario}?persist=true`, { method: "POST" });
    const payload = await readJson(response);
    renderWorkflow(payload);
  } catch (error) {
    renderError(error.message);
  } finally {
    setBusy(false);
  }
}

async function runCustomDonation(event) {
  event.preventDefault();
  setBusy(true);
  try {
    const payload = buildDonationPayload();
    const response = await fetch("/api/donations?persist=true", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderWorkflow(await readJson(response));
    setActiveScenario(null);
  } catch (error) {
    renderError(error.message);
  } finally {
    setBusy(false);
  }
}

async function resolveApproval(status) {
  if (!activeApprovalId || !activePersisted) {
    return;
  }
  setBusy(true);
  try {
    const response = await fetch(`/api/approvals/${activeApprovalId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, approved_by: "demo_operator" }),
    });
    const payload = await readJson(response);
    renderSnapshot(payload.snapshot, status);
  } catch (error) {
    renderError(error.message);
  } finally {
    setBusy(false);
  }
}

function buildDonationPayload() {
  const donationId = `don_ui_${Date.now()}`;
  return {
    donation_id: donationId,
    donor_name: valueOf("donor-name"),
    donor_contact: valueOf("donor-contact"),
    pickup_address: valueOf("pickup-address"),
    food_items: [
      {
        name: valueOf("food-name"),
        quantity: Number(valueOf("quantity")),
        category: valueOf("category"),
        sealed: document.querySelector("#sealed").checked,
      },
    ],
    prepared_at: toApiDateTime(valueOf("prepared-at")),
    available_until: toApiDateTime(valueOf("available-until")),
    storage: valueOf("storage"),
    notes: valueOf("notes"),
  };
}

function renderWorkflow(payload) {
  const result = payload.result;
  activeApprovalId = result.approval_id;
  activePersisted = Boolean(payload.persisted);

  stateValue.textContent = formatState(result.final_state);
  safetyValue.textContent = result.safety_status ? formatState(result.safety_status) : "None";
  approvalValue.textContent = result.approval_id || "None";

  setSafetyBadge(result);
  renderList(reasonList, result.reasons, "No reasons recorded.");
  renderSignals(result.prompt_injection_signals);
  renderQuestions(result.questions);
  renderCandidates(result.ranked_candidates);
  draftMessage.textContent = result.draft_message || "No draft yet.";
  renderList(toolList, result.tool_calls, "No tool calls recorded.");
  renderList(traceList, result.trace_events, "No trace events recorded.");
  updateApprovalButtons(result.final_state);
}

function renderSnapshot(snapshot, status) {
  activeApprovalId = null;
  activePersisted = false;

  const state = snapshot.donation.state;
  stateValue.textContent = formatState(state);
  approvalValue.textContent = status;
  safetyBadge.textContent = formatState(state);
  safetyBadge.className = `badge ${state.toLowerCase()}`;

  if (snapshot.dispatch && snapshot.dispatch.draft_message) {
    draftMessage.textContent = snapshot.dispatch.draft_message;
  }

  const traces = snapshot.trace_events.map((event) => event.summary);
  renderList(traceList, traces, "No trace events recorded.");
  updateApprovalButtons(state);
}

function setSafetyBadge(result) {
  const status = result.safety_status || result.final_state || "idle";
  safetyBadge.textContent = formatState(status);
  safetyBadge.className = `badge ${status}`;
}

function renderSignals(signals) {
  if (!signals || signals.length === 0) {
    injectionBox.classList.add("hidden");
    injectionBox.textContent = "";
    return;
  }
  injectionBox.classList.remove("hidden");
  injectionBox.textContent = `Prompt injection signals: ${signals.join(", ")}`;
}

function renderQuestions(questions) {
  if (!questions || questions.length === 0) {
    questionBox.classList.add("hidden");
    questionBox.textContent = "";
    return;
  }
  questionBox.classList.remove("hidden");
  questionBox.textContent = `Questions: ${questions.join(" ")}`;
}

function renderCandidates(candidates) {
  recipientList.textContent = "";
  candidateCount.textContent = `${candidates.length} ${candidates.length === 1 ? "candidate" : "candidates"}`;

  if (!candidates.length) {
    const empty = document.createElement("div");
    empty.className = "recipient-card";
    empty.textContent = "No ranked recipient match.";
    recipientList.append(empty);
    return;
  }

  for (const candidate of candidates) {
    const card = document.createElement("article");
    card.className = "recipient-card";

    const header = document.createElement("header");
    const title = document.createElement("h3");
    title.textContent = candidate.name;
    const score = document.createElement("span");
    score.className = "badge neutral";
    score.textContent = `Score ${candidate.score}`;
    header.append(title, score);

    const meta = document.createElement("div");
    meta.className = "recipient-meta";
    meta.textContent = `${formatState(candidate.recipient_type)} | ${candidate.distance_miles_demo} mi | capacity ${candidate.capacity_meals}`;

    const reasons = document.createElement("ul");
    for (const reason of candidate.reasons) {
      const item = document.createElement("li");
      item.textContent = reason;
      reasons.append(item);
    }

    card.append(header, meta, reasons);
    recipientList.append(card);
  }
}

function renderList(node, items, emptyText) {
  node.textContent = "";
  const values = items && items.length ? items : [emptyText];
  for (const value of values) {
    const item = document.createElement("li");
    item.textContent = value;
    node.append(item);
  }
}

function renderError(message) {
  stateValue.textContent = "Error";
  safetyValue.textContent = "Review";
  approvalValue.textContent = "None";
  safetyBadge.textContent = "error";
  safetyBadge.className = "badge rejected";
  renderList(reasonList, [message], "No reasons recorded.");
  recipientList.textContent = "";
  draftMessage.textContent = "No draft yet.";
  renderList(toolList, [], "No tool calls recorded.");
  renderList(traceList, [], "No trace events recorded.");
  updateApprovalButtons("ERROR");
}

function updateApprovalButtons(finalState) {
  const enabled = activePersisted && activeApprovalId && finalState === "APPROVAL_PENDING";
  approveButton.disabled = !enabled;
  denyButton.disabled = !enabled;
}

function setBusy(isBusy) {
  for (const button of [...scenarioButtons, approveButton, denyButton]) {
    button.disabled = isBusy || (button === approveButton || button === denyButton ? button.disabled : false);
  }
  donationForm.querySelector(".primary-action").disabled = isBusy;
}

function setActiveScenario(scenario) {
  for (const button of scenarioButtons) {
    button.classList.toggle("active", button.dataset.scenario === scenario);
  }
}

async function readJson(response) {
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Request failed");
  }
  return payload;
}

function valueOf(id) {
  return document.querySelector(`#${id}`).value;
}

function toApiDateTime(value) {
  return value ? value.replace("T", "T") : null;
}

function formatState(value) {
  return String(value).replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

for (const button of scenarioButtons) {
  button.addEventListener("click", () => runScenario(button.dataset.scenario));
}

donationForm.addEventListener("submit", runCustomDonation);
approveButton.addEventListener("click", () => resolveApproval("approved"));
denyButton.addEventListener("click", () => resolveApproval("denied"));

boot();
