import pandas as pd

df = pd.read_csv('data/processed/campus_resource_data_clean.csv')

df['date'] = pd.to_datetime(df['date'])

df['day_number'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month

features = [
    'day_number',
    'month',
    'meal',
    'expected_attendance',
    'event_type',
    'holiday',
    'exam_period',
    'weather_condition'
]

target = 'waste_quantity'

ml_data = df[features + [target]]

ml_data.to_csv(
    'data/processed/ml_dataset.csv',
    index=False
)

print('ML dataset created')
print('Rows:', len(ml_data))
print('Features:', features)
print('Target:', target)
