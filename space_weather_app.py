import streamlit as st  # Streamlit for UI
import requests  # For API calls
import pandas as pd  # For data handling
from datetime import datetime, timedelta
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
Agnirvaapi_key = os.getenv("API_KEY")  # Fetch API key from .env

# Event descriptions
Agnirvaevent_descriptions = {
    "CME": "Coronal Mass Ejection (CME): A massive burst of solar wind and magnetic fields rising above the solar corona.",
    "GST": "Geomagnetic Storm (GST): Disturbances in Earth's magnetosphere caused by solar wind shocks.",
    "FLR": "Solar Flare (FLR): A sudden flash of increased brightness on the Sun, usually observed near its surface.",
    "SEP": "Solar Energetic Particle (SEP): High-energy particles emitted by the Sun, often associated with solar flares and CMEs.",
    "IPS": "Interplanetary Shock (IPS): Shock waves traveling through space, often caused by CMEs or solar wind variations.",
    "RBE": "Radiation Belt Enhancement (RBE): An increase in the density of charged particles in Earth's radiation belts.",
    "MPC": "Magnetopause Crossing (MPC): When solar wind plasma crosses Earth's magnetopause, the boundary of the magnetosphere.",
    "HSS": "High Speed Stream (HSS): Streams of fast-moving solar wind emanating from coronal holes on the Sun.",
    "notifications": "Notifications: General alerts and updates related to various space weather events."
}

# CSS for dark space theme
Agnirvaspace_theme_css = """
<style>
body {
    background-color: #0e1117;
    color: #FAFAFA;
    font-family: 'Arial', sans-serif;
}
.sidebar .sidebar-content {
    background-color: #262730;
    color: #FAFAFA;
}
.css-1d391kg {
    background-color: #0e1117;
}
.css-1v3fvcr {
    color: #FAFAFA;
}
.css-1adrfps.edgvbvh3 {
    background-color: #262730;
}
.streamlit-expanderHeader {
    color: #1f77b4;
}
</style>
"""
st.markdown(Agnirvaspace_theme_css, unsafe_allow_html=True)

# App title and description
st.title("🌌 Space Weather Visualizer")
st.markdown("""
This application visualizes space weather trends using NASA's DONKI API. 
Explore events like Coronal Mass Ejections (CME), Geomagnetic Storms (GST), Solar Flares (FLR), and more.
""")

# Sidebar
st.sidebar.header("Configuration")
Agnirvaevent_types = {
    "CME (Coronal Mass Ejection)": "CME",
    "GST (Geomagnetic Storm)": "GST",
    "FLR (Solar Flare)": "FLR",
    "SEP (Solar Energetic Particle)": "SEP",
    "IPS (Interplanetary Shock)": "IPS",
    "RBE (Radiation Belt Enhancement)": "RBE",
    "MPC (Magnetopause Crossing)": "MPC",
    "HSS (High Speed Stream)": "HSS",
    "Notifications": "notifications"
}

Agnirvaselected_event_display = st.sidebar.selectbox(
    "Select Space Weather Event Type:",
    list(Agnirvaevent_types.keys()),
    format_func=lambda x: x
)
Agnirvaapi_endpoint = Agnirvaevent_types[Agnirvaselected_event_display]

st.sidebar.markdown("### Date Range")
Agnirvadefault_end_date = datetime.utcnow().date()
Agnirvadefault_start_date = Agnirvadefault_end_date - timedelta(days=30)

Agnirvastart_date = st.sidebar.date_input("Start Date:", Agnirvadefault_start_date)
Agnirvaend_date = st.sidebar.date_input("End Date:", Agnirvadefault_end_date)

if Agnirvastart_date > Agnirvaend_date:
    st.sidebar.error("Error: End date must fall after start date.")

Agnirvafetch_button = st.sidebar.button("Fetch Data")

# Event info
st.sidebar.markdown("### Event Information")
with st.sidebar.expander("ℹ️ What is this event?"):
    st.write(Agnirvaevent_descriptions.get(Agnirvaapi_endpoint, "No description available."))

# Glossary
st.sidebar.markdown("### Glossary")
with st.sidebar.expander("📖 View Glossary"):
    for term, description in Agnirvaevent_descriptions.items():
        st.markdown(f"**{term}**: {description}")

# Help
st.sidebar.markdown("### Help")
with st.sidebar.expander("❓ How to Use This App"):
    st.write("""
    1. **API Key**: Stored in .env file, automatically loaded.
    2. **Select Event Type**.
    3. **Set Date Range**.
    4. **Fetch Data**.
    5. **View Details & Explore Plots**.
    """)

# Fetch function
@st.cache_data(ttl=3600)
def Agnirvafetch_space_weather(Agnirvaevent, Agnirvastart, Agnirvaend, Agnirvakey):
    Agnirvabase_url = f"https://api.nasa.gov/DONKI/{Agnirvaevent}"
    Agnirvaparms = {
        "startDate": Agnirvastart.strftime("%Y-%m-%d"),
        "endDate": Agnirvaend.strftime("%Y-%m-%d"),
        "api_key": Agnirvakey
    }
    if Agnirvaevent == "CME":
        Agnirvaparms.update({
            "mostAccurateOnly": "true",
            "completeEntryOnly": "true",
            "speed": 500,
            "halfAngle": 30,
            "catalog": "ALL"
        })
    elif Agnirvaevent == "notifications":
        Agnirvaparms.update({"type": "all"})
    
    Agnirvaresponse = requests.get(Agnirvabase_url, params=Agnirvaparms)
    if Agnirvaresponse.status_code == 200:
        return Agnirvaresponse.json()
    else:
        st.error(f"Error fetching data: {Agnirvaresponse.status_code} - {Agnirvaresponse.text}")
        return None

# Main
if Agnirvafetch_button:
    if not Agnirvaapi_key:
        st.error("API key not found. Please add it to your .env file.")
    else:
        with st.spinner("Fetching data..."):
            Agnirvadata = Agnirvafetch_space_weather(Agnirvaapi_endpoint, Agnirvastart_date, Agnirvaend_date, Agnirvaapi_key)
        
        if Agnirvadata:
            st.success("Data fetched successfully!")
            with st.expander("Show Raw JSON Data for Debugging"):
                st.json(Agnirvadata)

            if isinstance(Agnirvadata, list):
                Agnirvadf = pd.json_normalize(Agnirvadata)
                Agnirvadf['date'] = pd.to_datetime(Agnirvadf.get('startTime') or Agnirvadf.get('beginTime') or Agnirvadf.get('eventTime'), errors='coerce').dt.date

                Agnirvadf_grouped = Agnirvadf.groupby('date').size().reset_index(name='count')
                st.subheader(f"{Agnirvaselected_event_display} from {Agnirvastart_date} to {Agnirvaend_date}")
                Agnirvafig = px.bar(Agnirvadf_grouped, x='date', y='count', labels={"date": "Date", "count": "Count"}, template="plotly_dark")
                st.plotly_chart(Agnirvafig, use_container_width=True)

                with st.expander("Show Raw Data"):
                    st.write(Agnirvadf)
        else:
            st.write("No data available for the selected parameters.")
