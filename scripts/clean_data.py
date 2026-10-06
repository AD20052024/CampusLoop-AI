import pandas as pd

input_file = 'data/sample/campus_resource_data.csv'
output_file = 'data/processed/campus_resource_data_clean.csv'

df = pd.read_csv(input_file)

df['date'] = pd.to_datetime(df['date'])

numeric_columns = [
    'expected_attendance',
    'actual_attendance',
    'preparation_quantity',
    'consumption_quantity',
    'surplus_quantity',
    'waste_quantity'
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors='coerce')

df = df.drop_duplicates()

df[numeric_columns] = df[numeric_columns].fillna(0)

df = df[df['expected_attendance'] >= 0]
df = df[df['actual_attendance'] >= 0]
df = df[df['preparation_quantity'] >= 0]
df = df[df['consumption_quantity'] >= 0]
df = df[df['surplus_quantity'] >= 0]
df = df[df['waste_quantity'] >= 0]

df['surplus_quantity'] = (
    df['preparation_quantity'] - df['consumption_quantity']
).clip(lower=0)

df['waste_quantity'] = (
    df['waste_quantity'].clip(
        upper=df['surplus_quantity']
    )
)

df = df.sort_values('date')

df.to_csv(output_file, index=False)

print('Cleaned rows:', len(df))
print('Saved:', output_file)
