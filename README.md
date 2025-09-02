# Vacation-Recommender
# 🏝️ Vacation Recommendation & Cost Optimization (API-Driven)

An **end-to-end data science project** that recommends vacation destinations based on **budget, weather, travel time, and activity preferences**.  

This project uses **real-world APIs** (Amadeus, OpenWeather, Yelp) to fetch live travel data, applies **feature engineering + scoring**, and presents results through an **interactive Streamlit web app** and a **CLI pipeline**.

---

## ✨ Features

- 🔑 **API Integration**  
  - ✈️ Flights & Hotels → [Amadeus API](https://developers.amadeus.com/)  
  - 🌤 Weather Forecast → [OpenWeather API](https://openweathermap.org/api)  
  - 🎭 Activities & Points of Interest → [Yelp Fusion API](https://www.yelp.com/developers/documentation/v3)  

- 🧮 **Feature Engineering**  
  - Flight cost + average hotel cost  
  - Weather suitability score (temperature & rainfall match)  
  - Activity density (POIs per category)  
  - Travel time estimation (distance + overhead)

- 📊 **Transparent Scoring Model**
  ```text
  score = w_cost * (1 - norm_total_cost)
        + w_weather * weather_score
  attachments/assets/8a809cb7-3ddb-4c01-89eb-7e8bf1e67229" />
     + w_activity * activity_score
        + w_travel * (1 - norm_travel_time)
Streamlit Visualization: 
<img width="1440" height="855" alt="Screenshot 2025-09-01 at 8 43 09 PM" src="https://github.com/user-attachments/assets/4dbcaa4b-cadf-4111-b927-d2aab45c7228" />
