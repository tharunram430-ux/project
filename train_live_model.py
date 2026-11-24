import os
import joblib
import pandas as pd

from feature_extractor import extract_features, FEATURE_NAMES

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from xgboost import XGBClassifier


# ============================================================
# SETTINGS
# ============================================================

DATA_PATH = r"C:\Users\GANESAN\Documents\PROJECT\Phising detection system\dataset\PhiUSIIL_Phishing_URL_Dataset.csv"

MODEL_DIR = "model"

OUTPUT_MODEL = os.path.join(
    MODEL_DIR,
    "phishing_model_live.pkl"
)

# Start with 100 per class for testing
SAMPLES_PER_CLASS = 100


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("LOADING DATASET")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print("Dataset:", df.shape)

print()
print("LABEL DISTRIBUTION:")
print(df["label"].value_counts())


# ============================================================
# SELECT BALANCED DATA
# ============================================================

phishing = df[df["label"] == 0].sample(
    n=SAMPLES_PER_CLASS,
    random_state=42
)

legitimate = df[df["label"] == 1].sample(
    n=SAMPLES_PER_CLASS,
    random_state=42
)

sample = pd.concat(
    [phishing, legitimate],
    ignore_index=True
)

sample = sample.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


print()
print("=" * 70)
print("SELECTED DATA")
print("=" * 70)

print("Total URLs:", len(sample))

print()
print(sample["label"].value_counts())


# ============================================================
# LIVE FEATURE EXTRACTION
# ============================================================

X_list = []
y_list = []

success = 0
failed = 0


print()
print("=" * 70)
print("LIVE FEATURE EXTRACTION")
print("=" * 70)


for index, row in sample.iterrows():

    url = str(row["URL"]).strip()

    label = int(row["label"])

    print()
    print(
        f"[{index + 1}/{len(sample)}] "
        f"Label={label} URL={url}"
    )

    try:

        # ----------------------------------------------------
        # EXTRACT FEATURES
        # ----------------------------------------------------

        result = extract_features(
            url,
            return_diagnostics=True
        )

        # ----------------------------------------------------
        # HANDLE BOTH POSSIBLE RETURN FORMATS
        # ----------------------------------------------------

        if isinstance(result, tuple):

            features = result[0]

            diagnostics = result[1]

        else:

            features = result

            diagnostics = {}


        # ----------------------------------------------------
        # CHECK HTML FETCH
        # ----------------------------------------------------

        html_ok = diagnostics.get(
            "html_fetch_ok",
            True
        )

        html_error = diagnostics.get(
            "html_fetch_error",
            ""
        )


        if not html_ok:

            print(
                "SKIPPED - HTML FETCH FAILED"
            )

            if html_error:

                print(
                    "Reason:",
                    html_error
                )

            failed += 1

            continue


        # ----------------------------------------------------
        # EXACT FEATURE ORDER
        # ----------------------------------------------------

        features = features[
            FEATURE_NAMES
        ]


        # ----------------------------------------------------
        # NUMERIC CONVERSION
        # ----------------------------------------------------

        features = features.astype(float)


        # ----------------------------------------------------
        # CHECK FEATURE COUNT
        # ----------------------------------------------------

        if len(features.columns) != 41:

            print(
                "SKIPPED - WRONG FEATURE COUNT:",
                len(features.columns)
            )

            failed += 1

            continue


        # ----------------------------------------------------
        # SAVE FEATURES
        # ----------------------------------------------------

        X_list.append(
            features.iloc[0].values
        )

        y_list.append(
            label
        )

        success += 1

        print("SUCCESS")


    except Exception as e:

        print(
            "SKIPPED - ERROR:",
            str(e)
        )

        failed += 1


# ============================================================
# EXTRACTION SUMMARY
# ============================================================

print()
print("=" * 70)
print("EXTRACTION SUMMARY")
print("=" * 70)

print(
    "Successful:",
    success
)

print(
    "Failed:",
    failed
)


# ============================================================
# CHECK SUCCESSFUL DATA
# ============================================================

if success < 50:

    raise RuntimeError(
        "Too few successful URLs. "
        "Increase SAMPLES_PER_CLASS or check the extractor."
    )


# ============================================================
# CREATE TRAINING DATA
# ============================================================

X = pd.DataFrame(
    X_list,
    columns=FEATURE_NAMES
)

y = pd.Series(
    y_list,
    name="label"
)


print()
print("=" * 70)
print("TRAINING DATA")
print("=" * 70)

print(
    "X shape:",
    X.shape
)

print(
    "y shape:",
    y.shape
)

print()
print("LABELS:")

print(
    y.value_counts()
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print()
print("=" * 70)
print("TRAINING XGBOOST")
print("=" * 70)


# ============================================================
# MODEL
# ============================================================

model = XGBClassifier(

    n_estimators=200,

    max_depth=6,

    learning_rate=0.05,

    subsample=0.8,

    colsample_bytree=0.8,

    objective="binary:logistic",

    eval_metric="logloss",

    random_state=42,

    n_jobs=-1
)


# ============================================================
# FIT
# ============================================================

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(
    X_test
)


# ============================================================
# ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)


print()
print("=" * 70)
print("MODEL RESULTS")
print("=" * 70)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print()

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "PHISHING",
            "LEGITIMATE"
        ]
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    OUTPUT_MODEL
)


print()
print("=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(
    "MODEL:",
    OUTPUT_MODEL
)

print(
    "FEATURE COUNT:",
    len(model.feature_names_in_)
)


# ============================================================
# VERIFY FEATURES
# ============================================================

print()
print("MODEL FEATURES:")

for i, feature in enumerate(
    model.feature_names_in_,
    start=1
):

    print(
        i,
        feature
    )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)