// CampusLoop AI Dashboard Client

const API_BASE = "/api";

let currentPredictionId = null;
let currentInterventionId = null;

// DOM Elements
const systemStatusBadge = document.getElementById("system-status-badge");
const systemStatusText = document.getElementById("system-status-text");

const kpiWaste = document.getElementById("kpi-waste");
const kpiCo2 = document.getElementById("kpi-co2");
const kpiWater = document.getElementById("kpi-water");
const kpiMeals = document.getElementById("kpi-meals");
const kpiMae = document.getElementById("kpi-mae");

const predictionForm = document.getElementById("prediction-form");
const predictionResultBox = document.getElementById("prediction-result");
const resWaste = document.getElementById("res-waste");
const resRiskBadge = document.getElementById("res-risk-badge");
const resRiskReason = document.getElementById("res-risk-reason");
const resPredictionId = document.getElementById("res-prediction-id");
const resCo2 = document.getElementById("res-co2");
const resWater = document.getElementById("res-water");
const resSalvagedMeals = document.getElementById("res-salvaged-meals");
const resSavings = document.getElementById("res-savings");

const interventionEmpty = document.getElementById("intervention-empty");
const interventionContent = document.getElementById("intervention-content");
const intActionType = document.getElementById("int-action-type");
const intPriority = document.getElementById("int-priority");
const intRecommendation = document.getElementById("int-recommendation");
const intStatus = document.getElementById("int-status");
const btnApprove = document.getElementById("btn-approve-intervention");
const btnExecute = document.getElementById("btn-execute-intervention");

const outcomeForm = document.getElementById("outcome-form");
const outcomeResultBox = document.getElementById("outcome-result-box");
const resErrorKg = document.getElementById("res-error-kg");
const resAbsErrorKg = document.getElementById("res-abs-error-kg");
const resPercentError = document.getElementById("res-percent-error");

const historyTbody = document.getElementById("history-tbody");
const btnRefreshHistory = document.getElementById("btn-refresh-history");

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  refreshAnalytics();
  refreshHistory();
});

// 1. Health Probe
async function checkBackendHealth() {
  try {
    const res = await fetch("/health");
    if (res.ok) {
      const data = await res.json();
      systemStatusText.textContent = `Backend Online | Model: ${data.model_loaded ? "Ready" : "Waiting"}`;
      systemStatusBadge.style.background = "#ecfdf5";
      systemStatusBadge.style.color = "#059669";
    }
  } catch (err) {
    systemStatusText.textContent = "Backend Disconnected";
    systemStatusBadge.style.background = "#fee2e2";
    systemStatusBadge.style.color = "#dc2626";
  }
}

// 2. Prediction Form Submit (PREDICT & ASSESS)
predictionForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    day_number: parseInt(document.getElementById("day_number").value),
    month: parseInt(document.getElementById("month").value),
    meal: document.getElementById("meal").value,
    expected_attendance: parseInt(document.getElementById("expected_attendance").value),
    event_type: document.getElementById("event_type").value,
    holiday: parseInt(document.getElementById("holiday").value),
    exam_period: parseInt(document.getElementById("exam_period").value),
    weather_condition: document.getElementById("weather_condition").value,
  };

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`Prediction failed: ${JSON.stringify(err.detail || err)}`);
      return;
    }

    const data = await res.json();

    // Store IDs for closed-loop operations
    currentPredictionId = data.prediction_id;
    currentInterventionId = data.intervention ? data.intervention.id : null;

    // Display prediction results
    resWaste.textContent = `${data.predicted_waste} kg`;
    resRiskBadge.textContent = `${data.risk_level} Risk`;
    resRiskBadge.className = `risk-badge ${data.risk_level}`;
    resRiskReason.textContent = `Reason: ${data.risk.reason}`;
    resPredictionId.textContent = data.prediction_id || "Ephemeral";

    // Display SDG 12 Impact
    resCo2.textContent = `${data.impact.co2e_prevented_kg} kg`;
    resWater.textContent = `${data.impact.water_saved_liters} L`;
    resSalvagedMeals.textContent = `${data.impact.meals_salvaged}`;
    resSavings.textContent = `$${data.impact.financial_savings_estimated}`;

    predictionResultBox.classList.add("active");

    // Display Step 2 Intervention
    if (data.intervention) {
      intActionType.textContent = data.intervention.action_type;
      intPriority.textContent = `Priority: ${data.intervention.priority}`;
      intRecommendation.textContent = data.intervention.recommendation;
      intStatus.textContent = data.intervention.status;

      interventionEmpty.style.display = "none";
      interventionContent.style.display = "block";
    }

    // Refresh history ledger
    refreshAnalytics();
    refreshHistory();

  } catch (err) {
    alert(`Network Error: ${err.message}`);
  }
});

// 3. Human Intervention Approval (INTERVENE)
btnApprove.addEventListener("click", async () => {
  if (!currentPredictionId || !currentInterventionId) {
    alert("Please run a prediction first.");
    return;
  }

  try {
    const res = await fetch(
      `${API_BASE}/predictions/${currentPredictionId}/interventions/${currentInterventionId}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "APPROVED",
          approved_by: "Dining Manager",
        }),
      }
    );

    if (res.ok) {
      intStatus.textContent = "APPROVED (by Dining Manager)";
      intStatus.style.color = "#059669";
      refreshHistory();
    }
  } catch (err) {
    alert(`Approval failed: ${err.message}`);
  }
});

// Mark Intervention Executed
btnExecute.addEventListener("click", async () => {
  if (!currentPredictionId || !currentInterventionId) {
    alert("Please run a prediction first.");
    return;
  }

  try {
    const res = await fetch(
      `${API_BASE}/predictions/${currentPredictionId}/interventions/${currentInterventionId}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "EXECUTED",
          approved_by: "Head Chef",
        }),
      }
    );

    if (res.ok) {
      intStatus.textContent = "EXECUTED";
      intStatus.style.color = "#059669";
      refreshHistory();
    }
  } catch (err) {
    alert(`Execution update failed: ${err.message}`);
  }
});

// 4. Outcome Form Submit (MEASURE & LEARN)
outcomeForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!currentPredictionId) {
    alert("Please generate or select a prediction first before submitting actual post-service outcomes.");
    return;
  }

  const payload = {
    actual_attendance: parseInt(document.getElementById("out_attendance").value),
    actual_preparation: parseFloat(document.getElementById("out_prep").value),
    actual_consumption: parseFloat(document.getElementById("out_cons").value),
    actual_waste: parseFloat(document.getElementById("out_waste").value),
  };

  try {
    const res = await fetch(`${API_BASE}/predictions/${currentPredictionId}/outcomes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`Outcome logging failed: ${JSON.stringify(err.detail || err)}`);
      return;
    }

    const data = await res.json();

    resErrorKg.textContent = `${data.prediction_error} kg`;
    resAbsErrorKg.textContent = `${data.absolute_error} kg`;
    resPercentError.textContent = `${data.percent_error}%`;
    outcomeResultBox.classList.add("active");

    refreshAnalytics();
    refreshHistory();

    alert("Outcome recorded! Feedback loop closed and accuracy metrics updated.");
  } catch (err) {
    alert(`Network Error: ${err.message}`);
  }
});

// 5. Analytics & KPI Fetch
async function refreshAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/feedback/analytics`);
    if (!res.ok) return;

    const data = await res.json();
    kpiWaste.textContent = `${data.cumulative_impact.waste_prevented_kg} kg`;
    kpiCo2.textContent = `${data.cumulative_impact.co2e_prevented_kg} kg CO₂e`;
    kpiWater.textContent = `${data.cumulative_impact.water_saved_liters.toLocaleString()} L`;
    kpiMeals.textContent = `${data.cumulative_impact.meals_salvaged}`;
    if (data.mean_absolute_error_historical > 0) {
      kpiMae.textContent = `${data.mean_absolute_error_historical} kg`;
    }
  } catch (err) {
    console.error("Failed to load analytics:", err);
  }
}

// 6. History Table Fetch
async function refreshHistory() {
  try {
    const res = await fetch(`${API_BASE}/predictions?limit=15`);
    if (!res.ok) return;

    const data = await res.json();
    const items = data.items || [];

    if (items.length === 0) {
      historyTbody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 18px;">
            No predictions logged yet. Submit a prediction in Step 1 to begin recording.
          </td>
        </tr>
      `;
      return;
    }

    historyTbody.innerHTML = items
      .map((item) => {
        const timestamp = item.created_at ? new Date(item.created_at).toLocaleTimeString() : "--";
        const actualWaste = item.outcome ? `${item.outcome.actual_waste} kg` : `<span style="color:#94a3b8;">Pending</span>`;
        const predError = item.outcome ? `${item.outcome.prediction_error} kg` : `<span style="color:#94a3b8;">--</span>`;
        const reduction = item.outcome ? `${item.outcome.waste_reduction_achieved} kg saved` : `<span style="color:#94a3b8;">--</span>`;

        return `
          <tr>
            <td>${timestamp}</td>
            <td><strong>${item.meal}</strong></td>
            <td>${item.expected_attendance}</td>
            <td>${item.predicted_waste} kg</td>
            <td><span class="risk-badge ${item.risk_level}" style="font-size:11px; padding:3px 8px;">${item.risk_level}</span></td>
            <td><code>${item.status}</code></td>
            <td>${actualWaste}</td>
            <td>${predError}</td>
            <td>${reduction}</td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    console.error("Failed to load history ledger:", err);
  }
}

btnRefreshHistory.addEventListener("click", () => {
  refreshHistory();
  refreshAnalytics();
});
