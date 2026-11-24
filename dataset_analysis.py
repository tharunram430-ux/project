import pandas as pd

# Load the dataset
df = pd.read_csv(r"C:\Users\GANESAN\Documents\PROJECT\Phising detection system\dataset\PhiUSIIL_Phishing_URL_Dataset.csv")

print("========== DATASET INFORMATION ==========\n")

# Number of rows and columns
print("Shape of Dataset:")
print(df.shape)

# Column names
print("\nColumn Names:")
print(df.columns)

# Data types
print("\nData Types:")
print(df.dtypes)

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Duplicate rows
print("\nDuplicate Rows:")
print(df.duplicated().sum())

# Label distribution
print("\nLabel Distribution:")
print(df['label'].value_counts())