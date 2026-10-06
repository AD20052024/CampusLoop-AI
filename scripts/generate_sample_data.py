import random
from datetime import date, timedelta

import pandas as pd


random.seed(42)

start_date = date(2025, 1, 1)
number_of_days = 365

meals = ["Breakfast", "Lunch", "Dinner"]
weather_conditions = ["Clear", "Cloudy", "Rainy"]
event_types = ["Normal", "Event", "Festival"]

rows = []

for i in range(number_of_days):
    current_date = start_date + timedelta(days=i)

    for meal in meals:

        # Basic expected attendance for each meal
        if meal == "Breakfast":
            expected = 180
        elif meal == "Lunch":
            expected = 260
        else:
            expected = 220

        # Weekend adjustment
        if current_date.weekday() >= 5:
            expected -= 30

        # Small natural variation
        expected += random.randint(-15, 15)

        actual = expected + random.randint(-20, 20)
        actual = max(actual, 30)

        # Amount prepared
        preparation = actual * random.uniform(0.35, 0.45)

        # Amount consumed
        consumption = actual * random.uniform(0.30, 0.40)
        consumption = min(consumption, preparation)

        # Remaining food
        surplus = preparation - consumption

        # Some of the surplus becomes waste
        waste = surplus * random.uniform(0.20, 0.50)

        weather = random.choice(weather_conditions)
        event = random.choice(event_types)

        holiday = random.choice([0, 0, 0, 0, 1])

        exam_period = 1 if current_date.month in [4, 5, 11, 12] else 0

        intervention = "None"

        if surplus > 25:
            intervention = random.choice(
                ["Reduced Preparation", "Redistribution", "Donation"]
            )

        rows.append({
            "date": current_date,
            "day_of_week": current_date.strftime("%A"),
            "meal": meal,
            "expected_attendance": expected,
            "actual_attendance": actual,
            "preparation_quantity": round(preparation, 2),
            "consumption_quantity": round(consumption, 2),
            "surplus_quantity": round(surplus, 2),
            "waste_quantity": round(waste, 2),
            "event_type": event,
            "holiday": holiday,
            "exam_period": exam_period,
            "weather_condition": weather,
            "intervention": intervention
        })


df = pd.DataFrame(rows)

output_file = "data/sample/campus_resource_data.csv"
df.to_csv(output_file, index=False)

print("CampusLoop AI sample dataset created successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("File:", output_file)
print("\nFirst five records:")
print(df.head())
