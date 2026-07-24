from loaders.speedcoach_loader import SpeedCoachLoader

loader = SpeedCoachLoader("data/practice.csv")

df = loader.load()

print("\nColumn Types\n")
print(df.dtypes)

print("\nColumns\n")
print(df.columns.tolist())

print("\nFirst Five Rows\n")
print(df.head())