import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config
st.set_page_config(page_title="Global Crisis Monitor", layout="wide")

# 2. FORCE TOTAL WHITE THEME (Main & Sidebar)
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #FFFFFF;
    }
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E0E0E0;
    }
    /* Titles and Text */
    h1, h2, h3, p {
        color: #1C1C1C !important;
    }
    /* Info boxes - making them look cleaner */
    .stAlert {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# Initialize Session State
if 'view' not in st.session_state: st.session_state.view = 'Global'

# 4. Sidebar Content
st.sidebar.title("🗺️ Controls")

# Legend with small colored circles
st.sidebar.subheader("Disaster Legend")
st.sidebar.write("🔵 Arctic/Volcanic")
st.sidebar.write("🔴 Japan Earthquake")
st.sidebar.write("🟠 US South Storms")
st.sidebar.write("🟢 Floods/Social")
st.sidebar.write("🟣 Tornado/Hail")

if st.sidebar.button("🌍 Reset to Global View"):
    st.session_state.view = 'Global'
    st.session_state.selected_country = None
    st.rerun()

# 5. Color Mapping
color_lookup = {
    "Arctic Storms & Volcanic Activity": [100, 100, 255, 160],
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0, 160],
    "Regional Meteorological Alerts (US South)": [255, 165, 0, 160],
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255, 160],
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128, 160]
}
df['color'] = df['Disaster_Category'].map(color_lookup)

# --- GLOBAL VIEW ---
if st.session_state.view == 'Global':
    st.title("Global Real-Time Disaster Map")
    
    # This view state centers the map and sets zoom
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=0)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=180000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        # Light-v10 provides the grey outlines on white land
        map_style="mapbox://styles/mapbox/light-v10", 
        layers=[layer], 
        initial_view_state=view_state,
        tooltip={"text": "Location: {location}\nCategory: {Disaster_Category}"}
    ))
    
    st.divider()
    st.subheader("Select a Hotspot to Investigate")
    selected = st.selectbox("Search Locations:", ["Select..."] + list(df['location'].unique()))
    
    if selected != "Select...":
        st.session_state.view = 'Detail'
        st.session_state.selected_country = selected
        st.rerun()

# --- DETAIL VIEW ---
elif st.session_state.view == 'Detail':
    country = st.session_state.selected_country
    st.title(f"📍 Detailed Analysis: {country}")
    
    country_df = df[df['location'] == country]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Regional Coverage")
        # For the detail map, using a simple scatter to show exact points
        st.map(country_df) 
    
    with col2:
        st.subheader("Incident Reports")
        for _, row in country_df.iterrows():
            st.info(f"**{row['Disaster_Category']}**\n\n{row['Tweet_Text']}")
