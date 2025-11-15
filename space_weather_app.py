import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("NASA_API_KEY")

# Check if API key is present
if not API_KEY:
    st.error("Please set your NASA API Key in a .env file as NASA_API_KEY.")
    st.stop()

# Function to fetch NASA Space Weather data
def fetch_event_data(event_type):
    base_url = f"https://api.nasa.gov/DONKI/{event_type}"
    params = {
        "startDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "endDate": datetime.now().strftime("%Y-%m-%d"),
        "api_key": API_KEY
    }
    return requests.get(base_url, params=params).json()

# Streamlit App UI
st.title("☀ NASA Space Weather Visualizer")
st.write("Get real-time solar activity and space weather updates from NASA.")

# Event selection
event_type = st.selectbox(
    "Select Space Weather Event Type",
    ["FLR", "GST", "CME"]
)

event_names = {
    "FLR": "Solar Flares",
    "GST": "Geomagnetic Storms",
    "CME": "Coronal Mass Ejections"
}

st.subheader(f"{event_names[event_type]} Over the Last 30 Days")

# Fetch data
data = fetch_event_data(event_type)
if not data:
    st.warning("No data available for the selected event type.")
else:
    # DataFrame conversion
    df = pd.DataFrame(data)
    
    # Format for display
    date_col = "beginTime" if "beginTime" in df.columns else "startTime"
    df["date"] = pd.to_datetime(df[date_col]).dt.date
    
    # Show table
    st.dataframe(df)
    
    # Plotting occurrences over time
    chart_data = df.groupby("date").size().reset_index(name="event_count")
    fig = px.line(chart_data, x="date", y="event_count", title=f"{event_names[event_type]} Occurrence Trend")
    st.plotly_chart(fig)
