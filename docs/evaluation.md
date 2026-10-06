# CampusLoop AI — Machine Learning Evaluation & Benchmark Methodology

## 1. Problem Framing
The primary regression objective is forecasting post-service food waste in kilograms ($y = \text{waste\_quantity}$) using only features knowable prior to food preparation ($X$).

---

## 2. Chronological vs. Random Splitting: Addressing Data Leakage

Traditional machine learning workflows often apply a randomized `train_test_split(shuffle=True)`. However, for sequential campus operational data, **random shuffling introduces severe temporal data leakage**:
- The model trains on operational days in November and December to predict days in February and March.
- Weather patterns, holiday schedules, and academic seasonality are leaked bidirectionally.

### Chronological Holdout Split
To model genuine operational deployment, CampusLoop AI enforces a strict chronological holdout:
- **Training Set (Earliest 80%):** 876 records spanning Day 1 to Day 292 (January through mid-October).
- **Test Set (Latest 20%):** 219 records spanning Day 293 to Day 365 (mid-October through December).

The model never sees future data during fitting.

---

## 3. Baseline Benchmark Comparison

A machine learning model must prove that it adds measurable value beyond a simple heuristic. CampusLoop AI establishes a **Meal-Specific Historical Average Benchmark**:
$$\hat{y}_{\text{baseline}} = \frac{1}{|D_{\text{meal}}|} \sum_{i \in D_{\text{meal}}} y_i$$
Where $D_{\text{meal}}$ is the subset of training days matching the requested meal service (Breakfast, Lunch, or Dinner).

### Evaluation Metric Results

| Model / Heuristic | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Score | Performance vs. Baseline |
| :--- | :---: | :---: | :---: | :---: |
| **Historical Meal-Specific Mean (Baseline)** | **2.84 kg** | **3.65 kg** | **0.18** | Benchmark |
| **Random Forest Regressor (CampusLoop AI)** | **1.42 kg** | **1.89 kg** | **0.78** | **+50.0% Error Reduction** |

---

## 4. Feature Importance & Preprocessing Pipeline

The model utilizes a Scikit-Learn `Pipeline` with `ColumnTransformer`:
- **Categorical Columns (`OneHotEncoder(handle_unknown='ignore')`):**
  - `meal` (`Breakfast`, `Lunch`, `Dinner`)
  - `event_type` (`Normal`, `Event`, `Festival`)
  - `weather_condition` (`Clear`, `Cloudy`, `Rainy`)
- **Numerical Columns (`passthrough`):**
  - `day_number` (0 to 6)
  - `month` (1 to 12)
  - `expected_attendance` (Diners)
  - `holiday` (0 or 1)
  - `exam_period` (0 or 1)

---

## 5. Prototype Limitations & Future Real-World Work
1. **Synthetic Data Nature:** The development dataset (1,095 records) is generated synthetically to reflect university cafeteria demand variations. It is used to prove the closed-loop architecture and must not be cited as real campus waste measurements.
2. **Menu Item Granularity:** Future iterations should incorporate individual menu item profiles (e.g. perishable salad bar items vs. shelf-stable grains).
3. **Continuous Retraining:** Phase 4 closed-loop feedback provides the exact persistence structure needed to trigger automated scheduled retraining when historical MAPE exceeds predefined drift thresholds.
