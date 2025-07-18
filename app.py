import pandas as pd
from collections import defaultdict
import streamlit as st
import requests
from datetime import datetime

# ---- CONFIG ----
API_KEY = "8bc7a9ebeeaadf8a90787ba53a16885f"
CURRENT_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# ---- APP UI ----
st.set_page_config(page_title="🌤️ Weather App", layout="centered")
st.title("🌦️ Real-Time Weather App")

city = st.text_input("Enter a city name", "Bangalore")
unit = st.radio("Choose unit", ("Celsius", "Fahrenheit"))
units = "metric" if unit == "Celsius" else "imperial"

# ---- API: 5-Day Forecast Function ----
def get_forecast(city, units):
    params = {"q": city, "appid": API_KEY, "units": units}
    response = requests.get(FORECAST_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# ---- MAIN ACTION ----
if st.button("Get Weather"):
    # --- Current Weather ---
    params = {"q": city, "appid": API_KEY, "units": units}
    response = requests.get(CURRENT_URL, params=params)

    if response.status_code == 200:
        data = response.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
        sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

        st.markdown(f"### 🌍 {city.title()} - {desc}")
        st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png")
        st.write(f"**🌡️ Temperature:** {temp} °{unit[0]}")
        st.write(f"**💧 Humidity:** {humidity}%")
        st.write(f"**🌅 Sunrise:** {sunrise}")
        st.write(f"**🌇 Sunset:** {sunset}")

        # --- 5-Day Forecast ---
        st.markdown("## 📅 5-Day Forecast")
        forecast_data = get_forecast(city, units)

        if forecast_data:
            daily_avg = defaultdict(list)
            for entry in forecast_data["list"]:
                date = entry["dt_txt"].split(" ")[0]
                temp = entry["main"]["temp"]
                daily_avg[date].append(temp)

            forecast_df = pd.DataFrame({
                "Date": list(daily_avg.keys()),
                "Avg Temp": [round(sum(vals)/len(vals), 2) for vals in daily_avg.values()]
            })

            st.line_chart(forecast_df.set_index("Date"))
        else:
            st.warning("⚠️ Could not load forecast data.")

    else:
        st.error("City not found or error with API.")
