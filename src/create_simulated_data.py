import pandas as pd
import numpy as np
import os

np.random.seed(42)

venues = [
    "Suncorp Stadium",
    "The Gabba",
    "Brisbane Convention Centre",
    "South Bank Parklands",
    "Victoria Park",
    "Brisbane Entertainment Centre",
    "Queensland Tennis Centre",
    "RNA Showgrounds"
]

event_types = [
    "Opening Ceremony",
    "Athletics",
    "Swimming",
    "Basketball",
    "Cycling",
    "Tennis",
    "Paralympic Event",
    "Closing Ceremony"
]

rows = []

for i in range(1000):
    venue_name = np.random.choice(venues)
    event_type = np.random.choice(event_types)

    expected_attendance = np.random.randint(5000, 85000)
    temperature = round(np.random.uniform(18, 38), 2)
    humidity = round(np.random.uniform(35, 90), 2)
    rainfall = round(np.random.uniform(0, 30), 2)

    transport_delay_score = np.random.randint(0, 101)
    road_congestion_score = np.random.randint(0, 101)
    crowd_density_score = np.random.randint(0, 101)
    hospital_distance_km = round(np.random.uniform(0.5, 15), 2)
    police_station_distance_km = round(np.random.uniform(0.5, 10), 2)
    accessibility_score = np.random.randint(40, 101)
    social_media_risk_score = np.random.randint(0, 101)

    final_crisis_risk_score = (
        crowd_density_score * 0.25 +
        transport_delay_score * 0.20 +
        road_congestion_score * 0.15 +
        social_media_risk_score * 0.15 +
        temperature * 1.20 +
        humidity * 0.15 +
        hospital_distance_km * 1.50 -
        accessibility_score * 0.10
    )

    final_crisis_risk_score = round(final_crisis_risk_score, 2)

    if final_crisis_risk_score < 55:
        risk_level = "Low"
    elif final_crisis_risk_score < 75:
        risk_level = "Medium"
    elif final_crisis_risk_score < 95:
        risk_level = "High"
    else:
        risk_level = "Critical"

    if risk_level == "Low":
        recommended_action = "Continue normal monitoring."
    elif risk_level == "Medium":
        recommended_action = "Increase monitoring and prepare support teams."
    elif risk_level == "High":
        recommended_action = "Deploy additional transport, security, and medical support."
    else:
        recommended_action = "Activate emergency response plan and redirect crowd movement."

    rows.append([
        venue_name,
        event_type,
        expected_attendance,
        temperature,
        humidity,
        rainfall,
        transport_delay_score,
        road_congestion_score,
        crowd_density_score,
        hospital_distance_km,
        police_station_distance_km,
        accessibility_score,
        social_media_risk_score,
        final_crisis_risk_score,
        risk_level,
        recommended_action
    ])

df = pd.DataFrame(rows, columns=[
    "venue_name",
    "event_type",
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
    "social_media_risk_score",
    "final_crisis_risk_score",
    "risk_level",
    "recommended_action"
])

os.makedirs("data/simulated", exist_ok=True)

df.to_csv("data/simulated/brisbane_2032_crisis_data.csv", index=False)

print("Dataset created successfully.")
print("Shape:", df.shape)
print()
print(df.head())
print()
print("Risk level distribution:")
print(df["risk_level"].value_counts())