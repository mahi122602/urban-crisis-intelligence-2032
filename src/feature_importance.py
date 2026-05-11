import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt

df = pd.read_csv("data/simulated/brisbane_2032_crisis_data.csv")

model = joblib.load("models/crisis_risk_model.pkl")

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

importance = model.feature_importances_

importance_df = pd.DataFrame({
    "feature": features,
    "importance": importance
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

os.makedirs("reports", exist_ok=True)

importance_df.to_csv(
    "reports/model_feature_importance.csv",
    index=False
)

plt.figure(figsize=(10, 6))
plt.barh(
    importance_df["feature"],
    importance_df["importance"]
)
plt.gca().invert_yaxis()
plt.title("AI Model Feature Importance")
plt.xlabel("Importance Score")
plt.tight_layout()

plt.savefig("reports/model_feature_importance.png")

print("Feature importance report created.")
print(importance_df)