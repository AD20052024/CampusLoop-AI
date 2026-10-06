import pandas as pd

df = pd.read_csv('data/processed/campus_resource_data_clean.csv')

print('Rows:', len(df))
print('Average expected attendance:', round(df['expected_attendance'].mean(), 2))
print('Average actual attendance:', round(df['actual_attendance'].mean(), 2))
print('Average preparation:', round(df['preparation_quantity'].mean(), 2))
print('Average consumption:', round(df['consumption_quantity'].mean(), 2))
print('Average surplus:', round(df['surplus_quantity'].mean(), 2))
print('Average waste:', round(df['waste_quantity'].mean(), 2))

print('\nWaste by meal:')
print(df.groupby('meal')['waste_quantity'].mean().round(2))

print('\nWaste by weather:')
print(df.groupby('weather_condition')['waste_quantity'].mean().round(2))

print('\nWaste by event:')
print(df.groupby('event_type')['waste_quantity'].mean().round(2))

print('\nWaste during exam period:')
print(df.groupby('exam_period')['waste_quantity'].mean().round(2))

print('\nWaste during holidays:')
print(df.groupby('holiday')['waste_quantity'].mean().round(2))