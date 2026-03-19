import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config - Using "light" as a preference
st.set_page_config(page_title="Global Crisis Monitor", layout="wide")

# CSS to ensure a clean white look
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stSelectbox, .stButton { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# 3. Sidebar Legend & Navigation
st.sidebar.title("🗺️ Dashboard Controls")

# Legend (Helps explain the icons/colors)
st.sidebar.subheader("Disaster Legend")
st.sidebar.markdown("""
- 🔵 **Blue**: Arctic/Volcanic
- 🔴 **Red**: Japan Earthquake
- 🟠 **Orange**: US South Storms
- 🟢 **Cyan**: Floods/Social
- 🟣 **Purple**: Tornado/Hail
""")

if st.sidebar.button("🌍 Reset to Global View"):
    st.session_state.view = 'Global'
    st.session_state.selected_country = None

# Initialize Session State
if 'view' not in st.session_state: st.session_state.view = 'Global'

# 4. Color Mapping Logic
color_lookup = {
    "Arctic Storms & Volcanic Activity": [100, 100, 255],
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0],
    "Regional Meteorological Alerts (US South)": [255, 165, 0],
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255],
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128]
}
df['color'] = df['Disaster_Category'].map(color_lookup)

# --- GLOBAL VIEW ---
if st.session_state.view == 'Global':
    st.title("🌍 Global Real-Time Disaster Map")
    
    # LIGHT THEMED MAP (mapbox://styles/mapbox/light-v9)
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.5, pitch=0)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=200000, # Large radius so they look like big icons
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9", # WHITE THEME
        layers=[layer], 
        initial_view_state=view_state,
        tooltip={"text": "Location: {location}\nCategory: {Disaster_Category}"}
    ))
    
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
        # Standard Streamlit map is light-themed by default
        st.map(country_df, color='#FF0000') 
    
    with col2:
        st.subheader("Incident Reports")
        for _, row in country_df.iterrows():
            st.info(f"**{row['Disaster_Category']}**\n\n{row['Tweet_Text']}")
