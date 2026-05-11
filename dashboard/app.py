import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import joblib
import requests
import os

st.set_page_config(
    page_title="Brisbane 2032 Urban Crisis Intelligence",
    layout="wide"
)

# -----------------------------
# LOAD CUSTOM CSS
# -----------------------------

css_file = os.path.join("dashboard", "assets", "style.css")

with open(css_file) as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )
# -----------------------------
# LIVE WEATHER FUNCTION
# -----------------------------

def get_brisbane_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=-27.4698"
        "&longitude=153.0251"
        "&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m"
        "&timezone=Australia%2FBrisbane"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        current = data["current"]

        return {
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "rain": current["rain"],
            "wind_speed": current["wind_speed_10m"]
        }

    except Exception:
        return None


# -----------------------------
# LOAD DATA AND MODEL
# -----------------------------

df = pd.read_csv("data/simulated/brisbane_2032_crisis_data.csv")

model = joblib.load("models/crisis_risk_model.pkl")
label_encoder = joblib.load("models/risk_label_encoder.pkl")

# -----------------------------
# VENUE COORDINATES
# -----------------------------

venue_coordinates = {
    "Suncorp Stadium": [-27.4648, 152.9973],
    "The Gabba": [-27.4850, 153.0381],
    "Brisbane Convention Centre": [-27.4778, 153.0175],
    "South Bank Parklands": [-27.4810, 153.0234],
    "Victoria Park": [-27.4510, 153.0251],
    "Brisbane Entertainment Centre": [-27.3493, 153.0695],
    "Queensland Tennis Centre": [-27.5300, 153.0170],
    "RNA Showgrounds": [-27.4524, 153.0360]
}

# -----------------------------
# HEADER
# -----------------------------

st.title("AI-Powered Urban Crisis Intelligence System")
st.subheader("Brisbane 2032 Olympic & Paralympic Command Centre")

st.markdown(
    """
    This dashboard simulates and predicts city-level crisis risks for Brisbane 2032,
    including crowd pressure, transport delay, climate risk, accessibility pressure,
    and emergency response needs.
    """
)

st.markdown("---")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.header("Dashboard Filters")

selected_venue = st.sidebar.selectbox(
    "Select Venue",
    ["All"] + sorted(df["venue_name"].unique())
)

selected_risk = st.sidebar.selectbox(
    "Select Risk Level",
    ["All"] + sorted(df["risk_level"].unique())
)

filtered_df = df.copy()

if selected_venue != "All":
    filtered_df = filtered_df[filtered_df["venue_name"] == selected_venue]

if selected_risk != "All":
    filtered_df = filtered_df[filtered_df["risk_level"] == selected_risk]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# -----------------------------
# LIVE BRISBANE WEATHER
# -----------------------------

st.markdown("## Live Brisbane Weather Intelligence")

weather = get_brisbane_weather()

if weather is not None:
    w1, w2, w3, w4 = st.columns(4)

    w1.metric("Live Temperature", f"{weather['temperature']} °C")
    w2.metric("Live Humidity", f"{weather['humidity']} %")
    w3.metric("Live Rain", f"{weather['rain']} mm")
    w4.metric("Wind Speed", f"{weather['wind_speed']} km/h")

    if weather["temperature"] >= 35:
        st.error("Climate Alert: Extreme heat conditions detected.")
    elif weather["temperature"] >= 30:
        st.warning("Climate Warning: Elevated heat risk for outdoor crowd movement.")
    else:
        st.success("Climate Status: No immediate heat alert detected.")
else:
    st.warning("Live weather data is currently unavailable.")

# -----------------------------
# EXECUTIVE METRICS
# -----------------------------

st.markdown("## Executive Risk Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Scenarios", len(filtered_df))
col2.metric("Average Risk Score", round(filtered_df["final_crisis_risk_score"].mean(), 2))
col3.metric("Critical Scenarios", len(filtered_df[filtered_df["risk_level"] == "Critical"]))
col4.metric("Average Attendance", int(filtered_df["expected_attendance"].mean()))

st.markdown("---")

# -----------------------------
# CHARTS
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Risk Level Distribution")

    risk_chart = px.histogram(
        filtered_df,
        x="risk_level",
        color="risk_level",
        title="Risk Level Distribution"
    )

    st.plotly_chart(risk_chart, use_container_width=True)

with col2:
    st.markdown("### Venue Risk Scores")

    venue_chart = px.box(
        filtered_df,
        x="venue_name",
        y="final_crisis_risk_score",
        color="venue_name",
        title="Venue Risk Score Spread"
    )

    st.plotly_chart(venue_chart, use_container_width=True)

# -----------------------------
# CLIMATE AND CROWD ANALYTICS
# -----------------------------

st.markdown("### Climate & Crowd Intelligence")

heat_chart = px.scatter(
    filtered_df,
    x="temperature",
    y="crowd_density_score",
    color="risk_level",
    size="expected_attendance",
    hover_data=["venue_name", "event_type", "final_crisis_risk_score"],
    title="Temperature vs Crowd Density Risk"
)

st.plotly_chart(heat_chart, use_container_width=True)

# -----------------------------
# AI MODEL EXPLANATION
# -----------------------------

st.markdown("### AI Model Explanation")

importance_df = pd.read_csv("reports/model_feature_importance.csv")

importance_chart = px.bar(
    importance_df.sort_values("importance", ascending=True),
    x="importance",
    y="feature",
    orientation="h",
    title="Most Important Factors Influencing Crisis Risk"
)

st.plotly_chart(importance_chart, use_container_width=True)

st.info(
    "The model identifies crowd density, temperature, hospital distance, transport delay, "
    "and social media risk as the strongest contributors to crisis prediction."
)

# -----------------------------
# BRISBANE RISK MAP
# -----------------------------

st.markdown("### Brisbane Olympic Risk Intelligence Map")

brisbane_map = folium.Map(
    location=[-27.4698, 153.0251],
    zoom_start=11
)

for venue, coords in venue_coordinates.items():
    venue_data = filtered_df[filtered_df["venue_name"] == venue]

    if len(venue_data) > 0:
        avg_risk = venue_data["final_crisis_risk_score"].mean()
        critical_count = len(venue_data[venue_data["risk_level"] == "Critical"])

        if avg_risk < 55:
            color = "green"
            risk_status = "Low"
        elif avg_risk < 75:
            color = "orange"
            risk_status = "Medium"
        elif avg_risk < 95:
            color = "red"
            risk_status = "High"
        else:
            color = "darkred"
            risk_status = "Critical"

        folium.CircleMarker(
            location=coords,
            radius=14,
            popup=f"""
            <b>{venue}</b><br>
            Average Risk Score: {avg_risk:.2f}<br>
            Risk Status: {risk_status}<br>
            Critical Scenarios: {critical_count}
            """,
            tooltip=f"{venue} - {risk_status}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75
        ).add_to(brisbane_map)

st_folium(
    brisbane_map,
    width=1200,
    height=500
)

# -----------------------------
# DATA TABLE
# -----------------------------

st.markdown("### Detailed Scenario Data")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# AI PREDICTION SECTION
# -----------------------------

st.markdown("---")
# -----------------------------
# LIVE ALERT ENGINE
# -----------------------------

st.markdown("## Real-Time Crisis Alerts")

alerts = []

# Heat alerts
if weather is not None:
    if weather["temperature"] >= 35:
        alerts.append("Extreme Heat Alert: Dangerous outdoor conditions detected.")

    elif weather["temperature"] >= 30:
        alerts.append("Heat Warning: Elevated temperature may affect crowd movement.")

# Crowd alerts
high_crowd = filtered_df[
    filtered_df["crowd_density_score"] >= 80
]

if len(high_crowd) > 0:
    alerts.append(
        f"Crowd Congestion Risk: {len(high_crowd)} high-density scenarios detected."
    )

# Transport alerts
high_transport = filtered_df[
    filtered_df["transport_delay_score"] >= 75
]

if len(high_transport) > 0:
    alerts.append(
        f"Transport Delay Risk: {len(high_transport)} scenarios showing severe delays."
    )

# Critical crisis alerts
critical_cases = filtered_df[
    filtered_df["risk_level"] == "Critical"
]

if len(critical_cases) > 50:
    alerts.append(
        f"Critical Risk Escalation: {len(critical_cases)} critical crisis scenarios identified."
    )

# Accessibility alerts
low_accessibility = filtered_df[
    filtered_df["accessibility_score"] <= 50
]

if len(low_accessibility) > 0:
    alerts.append(
        f"Accessibility Warning: {len(low_accessibility)} scenarios have poor accessibility conditions."
    )

# Display alerts
if alerts:
    for alert in alerts:
        st.error(alert)
else:
    st.success("No major operational alerts detected.")
st.markdown("## AI Crisis Prediction Engine")

col1, col2 = st.columns(2)

with col1:
    expected_attendance = st.slider("Expected Attendance", 5000, 85000, 40000)

    use_live_weather = st.checkbox("Use Live Brisbane Weather for Prediction")

    if use_live_weather and weather is not None:
        temperature = weather["temperature"]
        humidity = weather["humidity"]
        rainfall = weather["rain"]

        st.info(
            f"Using live weather: {temperature}°C, {humidity}% humidity, {rainfall} mm rain"
        )
    else:
        temperature = st.slider("Temperature", 18.0, 40.0, 30.0)
        humidity = st.slider("Humidity", 30.0, 95.0, 65.0)
        rainfall = st.slider("Rainfall", 0.0, 40.0, 5.0)

    transport_delay_score = st.slider("Transport Delay Score", 0, 100, 50)
    road_congestion_score = st.slider("Road Congestion Score", 0, 100, 50)

with col2:
    crowd_density_score = st.slider("Crowd Density Score", 0, 100, 50)
    hospital_distance_km = st.slider("Hospital Distance KM", 0.5, 15.0, 5.0)
    police_station_distance_km = st.slider("Police Station Distance KM", 0.5, 10.0, 3.0)
    accessibility_score = st.slider("Accessibility Score", 40, 100, 75)
    social_media_risk_score = st.slider("Social Media Risk Score", 0, 100, 40)

input_data = pd.DataFrame([[
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
    social_media_risk_score
]], columns=[
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
])

if st.button("Predict Crisis Risk"):
    prediction = model.predict(input_data)
    predicted_label = label_encoder.inverse_transform(prediction)[0]

    st.success(f"Predicted Risk Level: {predicted_label}")

    if predicted_label == "Low":
        st.info("Recommended Action: Continue normal monitoring.")
    elif predicted_label == "Medium":
        st.warning("Recommended Action: Increase monitoring and prepare support teams.")
    elif predicted_label == "High":
        st.error("Recommended Action: Deploy additional transport, security, and medical support.")
    else:
        st.error("Recommended Action: Activate emergency response plan and redirect crowd movement.")