import joblib

MODEL_PATH = "model/phishing_model.pkl"

model = joblib.load(MODEL_PATH)

print("=" * 70)
print("MODEL INFORMATION")
print("=" * 70)

print("Model type:")
print(type(model))

print()
print("Classes:")
print(model.classes_)

print()
print("Number of features:")

if hasattr(model, "n_features_in_"):
    print(model.n_features_in_)
else:
    print("Not available")

print()
print("Feature names:")

if hasattr(model, "feature_names_in_"):
    for i, name in enumerate(model.feature_names_in_, start=1):
        print(i, name)
else:
    print("Model does not contain feature names")

print()
print("=" * 70)