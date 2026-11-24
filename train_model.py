import pandas as pd
from feature_extractor import extract_features, FEATURE_NAMES

DATA_PATH = r"C:\Users\GANESAN\Documents\PROJECT\Phising detection system\dataset\PhiUSIIL_Phishing_URL_Dataset.csv"

# ============================================================
# LOAD DATASET
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset:", df.shape)

# ============================================================
# TARGET URL
# ============================================================

target = "https://www.uni-mainz.de"

# ============================================================
# FIND URL IN DATASET
# ============================================================

rows = df[
    df["URL"].astype(str).str.strip() == target
]

print()
print("=" * 70)
print("DATASET ROW")
print("=" * 70)

if rows.empty:

    print("Exact URL not found in dataset.")

else:

    row = rows.iloc[0]

    print("URL:", row["URL"])
    print("LABEL:", row["label"])

    print()
    print("DATASET FEATURES:")

    for feature in FEATURE_NAMES:
        print(
            f"{feature}: {row[feature]}"
        )

# ============================================================
# LIVE FEATURE EXTRACTION
# ============================================================

print()
print("=" * 70)
print("LIVE FEATURES")
print("=" * 70)

live = extract_features(target)

for feature in FEATURE_NAMES:

    print(
        f"{feature}: {live.iloc[0][feature]}"
    )

# ============================================================
# COMPARE FEATURES
# ============================================================

print()
print("=" * 70)
print("DIFFERENCES")
print("=" * 70)

if not rows.empty:

    differences = []

    row = rows.iloc[0]

    for feature in FEATURE_NAMES:

        dataset_value = float(row[feature])
        live_value = float(live.iloc[0][feature])

        if abs(dataset_value - live_value) > 0.000001:

            differences.append(
                (
                    feature,
                    dataset_value,
                    live_value
                )
            )

    print(
        "Different features:",
        len(differences)
    )

    for feature, dataset_value, live_value in differences:

        print()
        print(feature)
        print("Dataset:", dataset_value)
        print("Live   :", live_value)

# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("TEST FINISHED")
print("=" * 70)