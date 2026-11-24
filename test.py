import joblib
from feature_extractor import extract_features, FEATURE_NAMES

MODEL_PATH = "model/phishing_model.pkl"

model = joblib.load(MODEL_PATH)

url = "https://www.uni-mainz.de"

print("=" * 70)
print("MODEL TEST")
print("=" * 70)

print("URL:", url)
print("MODEL:", type(model))
print("MODEL CLASSES:", model.classes_)

features = extract_features(url)

print()
print("FEATURE COUNT:", len(features.columns))
print("FEATURE ORDER OK:",
      list(features.columns) == list(model.feature_names_in_))

prediction = model.predict(features)[0]

print()
print("RAW PREDICTION:", prediction)

if hasattr(model, "predict_proba"):
    probabilities = model.predict_proba(features)[0]

    index = list(model.classes_).index(prediction)
    confidence = probabilities[index] * 100

    print("PROBABILITIES:", probabilities)
    print(f"CONFIDENCE: {confidence:.2f}%")

print("=" * 70)