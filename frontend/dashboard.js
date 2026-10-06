const form = document.getElementById("prediction-form");
const forecastButton = document.getElementById("forecast-button");
const buttonLabel = document.getElementById("button-label");
const formMessage = document.getElementById("form-message");
const forecastEmpty = document.getElementById("forecast-empty");
const forecastContent = document.getElementById("forecast-content");
const connectionStatus = document.getElementById("connection-status");
const connectionLabel = document.getElementById("connection-label");
const historyList = document.getElementById("history-list");
const outcomeForm = document.getElementById("outcome-form");
const outcomeMessage = document.getElementById("outcome-message");
const outcomeSummary = document.getElementById("outcome-summary");
const actionMessage = document.getElementById("action-message");

let selectedPredictionId = null;
let selectedInterventionId = null;
let selectedPredictionLabel = "";

const dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const riskCopy = {
  Low: "Routine monitoring is recommended for this service.",
  Medium: "Keep a closer watch on preparation and attendance.",
  High: "Review preparation plans before service begins."
};

function setDateDefaults() {
  const today = new Date();
  document.getElementById("day_number").value = String((today.getDay() + 6) % 7);
  document.getElementById("month").value = String(today.getMonth() + 1);
}

function formatNumber(value, digits = 1) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: digits }).format(Number(value) || 0);
}

async function checkConnection() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Health check failed");
    connectionStatus.classList.add("is-online");
    connectionLabel.textContent = "System online";
  } catch {
    connectionStatus.classList.remove("is-online");
    connectionLabel.textContent = "System unavailable";
  }
}

function displayForecast(data) {
  const risk = data.risk_level || "Low";
  const meal = document.getElementById("meal").value;
  const day = dayNames[Number(document.getElementById("day_number").value)];
  const impact = data.impact || {};
  const riskPill = document.getElementById("risk-pill");

  document.getElementById("result-title").textContent = `${meal} service`;
  document.getElementById("service-label").textContent = `${meal} · ${day}`;
  document.getElementById("predicted-waste").textContent = formatNumber(data.predicted_waste, 2);
  riskPill.textContent = `${risk} risk`;
  riskPill.dataset.risk = risk;
  document.getElementById("risk-explanation").textContent = riskCopy[risk] || riskCopy.Low;
  document.getElementById("recommended-action").textContent = data.recommended_action;
  document.getElementById("impact-prevented").textContent = `${formatNumber(impact.estimated_waste_prevented, 2)} kg`;
  document.getElementById("impact-carbon").textContent = formatNumber(impact.co2e_prevented_kg, 2);
  document.getElementById("impact-water").textContent = formatNumber(impact.water_saved_liters, 0);

  forecastEmpty.hidden = true;
  forecastContent.hidden = false;
  selectedPredictionId = data.prediction_id;
  selectedInterventionId = data.intervention?.id || null;
  setSelectedPrediction(data.prediction_id, `${meal} · ${day}`, false);
  showStaffAction(data.intervention);
  outcomeSummary.hidden = true;
  refreshHistory();
}

function setSelectedPrediction(predictionId, label, hasOutcome) {
  selectedPredictionId = predictionId;
  selectedPredictionLabel = label;
  document.getElementById("selected-prediction").textContent =
    `${label}${hasOutcome ? " · Results already recorded" : " · Ready for measured results"}`;
  outcomeForm.querySelectorAll("input, button").forEach((control) => {
    control.disabled = hasOutcome;
  });
}

function showStaffAction(intervention) {
  const staffAction = document.getElementById("staff-action");
  staffAction.hidden = !intervention;
  if (!intervention) return;

  selectedInterventionId = intervention.id;
  const status = document.getElementById("intervention-status");
  const approvalRequired = intervention.requires_human_approval;
  status.textContent = approvalRequired
    ? `Status: ${intervention.status || "RECOMMENDED"}`
    : "Staff review suggested · formal approval not required";
  document.getElementById("approve-action").hidden = !approvalRequired || ["APPROVED", "EXECUTED"].includes(intervention.status);
  document.getElementById("execute-action").hidden = intervention.status === "EXECUTED";
}

async function updateIntervention(nextStatus) {
  const staffName = document.getElementById("staff-name").value.trim();
  if (!selectedPredictionId || !selectedInterventionId) {
    actionMessage.textContent = "Generate a forecast before updating an action.";
    actionMessage.hidden = false;
    return;
  }
  if (!staffName) {
    actionMessage.textContent = "Enter the staff member’s name to record this action.";
    actionMessage.hidden = false;
    document.getElementById("staff-name").focus();
    return;
  }

  actionMessage.hidden = true;
  try {
    const response = await fetch(`/api/predictions/${selectedPredictionId}/interventions/${selectedInterventionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: nextStatus, approved_by: staffName })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not update this action.");
    document.getElementById("intervention-status").textContent = `Status: ${data.new_status} · ${data.approved_by}`;
    document.getElementById("approve-action").hidden = ["APPROVED", "EXECUTED"].includes(data.new_status);
    document.getElementById("execute-action").hidden = data.new_status === "EXECUTED";
    refreshHistory();
  } catch (error) {
    actionMessage.textContent = error.message;
    actionMessage.hidden = false;
  }
}

async function selectHistoryPrediction(item) {
  const response = await fetch(`/api/predictions/${item.prediction_id}`);
  const detail = await response.json();
  if (!response.ok) throw new Error(detail.detail || "Could not load this forecast.");
  setSelectedPrediction(detail.prediction_id, `${detail.meal} · ${new Date(detail.created_at).toLocaleString()}`, Boolean(detail.outcome));
  selectedInterventionId = detail.interventions[0]?.id || null;
  if (!detail.outcome && detail.interventions.length) showStaffAction(detail.interventions[0]);
  else document.getElementById("staff-action").hidden = true;
}

async function refreshHistory() {
  try {
    const response = await fetch("/api/predictions?limit=8");
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not load recent forecasts.");
    historyList.replaceChildren();
    if (!data.items.length) {
      const empty = document.createElement("p");
      empty.className = "history-empty";
      empty.textContent = "No forecasts recorded yet.";
      historyList.append(empty);
      return;
    }

    data.items.forEach((item) => {
      const row = document.createElement("article");
      row.className = "history-item";
      const details = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = item.meal;
      const meta = document.createElement("span");
      meta.textContent = `${new Date(item.created_at).toLocaleString()} · ${formatNumber(item.predicted_waste, 2)} kg forecast`;
      details.append(title, meta);
      const status = document.createElement("span");
      status.className = `history-status${item.outcome ? " is-recorded" : ""}`;
      status.textContent = item.outcome ? "Recorded" : "Pending";
      const select = document.createElement("button");
      select.className = "history-select";
      select.type = "button";
      select.textContent = "Select";
      select.addEventListener("click", async () => {
        try {
          await selectHistoryPrediction(item);
        } catch (error) {
          outcomeMessage.textContent = error.message;
          outcomeMessage.hidden = false;
        }
      });
      row.append(details, status, select);
      historyList.append(row);
    });
  } catch (error) {
    historyList.replaceChildren();
    const message = document.createElement("p");
    message.className = "history-empty";
    message.textContent = error.message;
    historyList.append(message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.hidden = true;
  forecastButton.disabled = true;
  buttonLabel.textContent = "Calculating forecast…";

  const payload = {
    meal: document.getElementById("meal").value,
    expected_attendance: Number(document.getElementById("expected_attendance").value),
    day_number: Number(document.getElementById("day_number").value),
    month: Number(document.getElementById("month").value),
    event_type: document.getElementById("event_type").value,
    weather_condition: document.getElementById("weather_condition").value,
    holiday: Number(document.getElementById("holiday").checked),
    exam_period: Number(document.getElementById("exam_period").checked)
  };

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((issue) => issue.msg).join(" ")
        : data.detail;
      throw new Error(detail || "The forecast could not be generated.");
    }
    displayForecast(data);
  } catch (error) {
    formMessage.textContent = error.message || "Could not connect to the forecast service. Try again.";
    formMessage.hidden = false;
  } finally {
    forecastButton.disabled = false;
    buttonLabel.textContent = "Generate forecast";
  }
});

outcomeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  outcomeMessage.hidden = true;
  outcomeSummary.hidden = true;
  if (!selectedPredictionId) {
    outcomeMessage.textContent = "Generate a forecast or select one from recent history first.";
    outcomeMessage.hidden = false;
    return;
  }

  const payload = {
    actual_attendance: Number(document.getElementById("out-attendance").value),
    actual_preparation: Number(document.getElementById("out-preparation").value),
    actual_consumption: Number(document.getElementById("out-consumption").value),
    actual_waste: Number(document.getElementById("out-waste").value)
  };

  try {
    const response = await fetch(`/api/predictions/${selectedPredictionId}/outcomes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not save measured results.");
    outcomeSummary.textContent = `Forecast error: ${formatNumber(data.prediction_error, 2)} kg · Absolute error: ${formatNumber(data.absolute_error, 2)} kg`;
    outcomeSummary.hidden = false;
    setSelectedPrediction(selectedPredictionId, selectedPredictionLabel, true);
    refreshHistory();
  } catch (error) {
    outcomeMessage.textContent = error.message;
    outcomeMessage.hidden = false;
  }
});

document.getElementById("approve-action").addEventListener("click", () => updateIntervention("APPROVED"));
document.getElementById("execute-action").addEventListener("click", () => updateIntervention("EXECUTED"));
document.getElementById("refresh-history").addEventListener("click", refreshHistory);

setDateDefaults();
checkConnection();
refreshHistory();