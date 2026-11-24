import joblib

model = joblib.load("model/phishing_model_live.pkl")

print(type(model))
print(model.n_features_in_)