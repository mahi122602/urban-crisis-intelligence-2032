import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("data/simulated/brisbane_2032_crisis_data.csv")

features = [
    "expected_attendance",
    "temperature",
    "humidity",
    "rainfall",
    "transport_delay_score",
    "road_congestion_score",
    "crowd_density_score",
    "hospital_distance_km",
    "police_station_distance_km",
    "accessibility_score",
    "social_media_risk_score"
]

X = df[features]
y = df["risk_level"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model training completed.")
print("Accuracy:", round(accuracy, 4))
print()
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/crisis_risk_model.pkl")
joblib.dump(label_encoder, "models/risk_label_encoder.pkl")

print()
print("Model saved in models/crisis_risk_model.pkl")
print("Label encoder saved in models/risk_label_encoder.pkl")