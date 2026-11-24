import pandas as pd
from feature_extractor import FEATURE_NAMES

DATA_PATH = r"C:\Users\GANESAN\Documents\PROJECT\Phising detection system\dataset\PhiUSIIL_Phishing_URL_Dataset.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

print()
print("ALL DATASET COLUMNS:")
print(list(df.columns))

print()
print("MODEL FEATURES:")
print(FEATURE_NAMES)

print()
print("FEATURE COUNT:", len(FEATURE_NAMES))

missing = [x for x in FEATURE_NAMES if x not in df.columns]

print()
print("MISSING FEATURES:")
print(missing)

print()
print("=" * 70)
print("LABEL DISTRIBUTION")
print("=" * 70)

print(df["label"].value_counts())

print()
print("=" * 70)
print("FIRST 10 URLS")
print("=" * 70)

print(df[["URL", "label"]].head(10).to_string(index=False))