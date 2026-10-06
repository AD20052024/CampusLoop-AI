import pandas as pd

df = pd.read_csv("data/sample/campus_resource_data.csv")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nStatistics:")
print(df.describe())

print("\nMeals:")
print(df["meal"].value_counts())

print("\nEvents:")
print(df["event_type"].value_counts())

print("\nTotal waste:", round(df["waste_quantity"].sum(), 2))
print("\nAverage waste:", round(df["waste_quantity"].mean(), 2))

print("\nChecks:")
print("Missing values:", df.isnull().sum().sum())
print("Negative waste:", (df["waste_quantity"] < 0).sum())
print("Consumption above preparation:",
      (df["consumption_quantity"] > df["preparation_quantity"]).sum())
