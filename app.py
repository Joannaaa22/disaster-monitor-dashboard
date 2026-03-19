import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config
st.set_page_config(page_title="Global Crisis Monitor", layout="wide")

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('final_dashboard_ready_data.csv')
    return df

df = load_data()

# Initialize "View State" - starts at Global
if 'view' not in st.session_state:
    st.session_state.view = 'Global'
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🗺️ Navigation")
if st.sidebar.button("🌍 Reset to Global View"):
    st.session_state.view = 'Global'
    st.session_state.selected_country = None

# --- GLOBAL VIEW ---
if st.session_state.view == 'Global':
    st.title("Global Real-Time Disaster Map")
    st.info("Click a location on the sidebar or map to drill down into country specifics.")
    
    # Define colors for the 5 categories
    color_lookup = {
        "Arctic Storms & Volcanic Activity": [100, 100, 255], # Blue
        "Geological (Japan Earthquake/Tsunami)": [255, 0, 0],   # Red
        "Regional Meteorological Alerts (US South)": [255, 165, 0], # Orange
        "Hydrological (Flash Floods) & Social Reports": [0, 255, 255], # Cyan
        "Severe Meteorological (Tornado/Hail)": [128, 0, 128]  # Purple
    }
    
    df['color'] = df['Disaster_Category'].map(color_lookup)

    # The Global Map with Icons (Scatterplot)
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1, pitch=40)
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=150000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        tooltip={"text": "Location: {location}\nCategory: {Disaster_Category}\nCluster: {cluster}"}
    ))
    
    # Manual Country Selection for Drill-down
    st.subheader("Select a Hotspot to Investigate")
    countries = df['location'].unique()
    selected = st.selectbox("Search Locations:", ["Select..."] + list(countries))
    
    if selected != "Select...":
        st.session_state.view = 'Detail'
        st.session_state.selected_country = selected
        st.rerun()

# --- COUNTRY DETAIL VIEW ---
elif st.session_state.view == 'Detail':
    country = st.session_state.selected_country
    st.title(f"Detailed Analysis: {country}")
    
    country_df = df[df['location'] == country]
    
    col1, col2 = st.columns([1, 1]) # Left for Map, Right for Tweets
    
    with col1:
        st.subheader("Affected Area Map")
        # Zoomed in map for the specific country
        st.map(country_df)
    
    with col2:
        st.subheader(f"Latest Reports from {country}")
        for _, row in country_df.iterrows():
            with st.chat_message("user"):
                st.write(f"**Category:** {row['Disaster_Category']}")
                st.write(row['Tweet_Text'])
                st.caption(f"Cluster ID: {row['cluster']}")
