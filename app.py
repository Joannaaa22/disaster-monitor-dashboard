import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# 1. Page Config
st.set_page_config(page_title="DisasterMonitor AI", layout="wide", initial_sidebar_state="collapsed")

# 2. THEME & STYLING
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #FFFFFF; }
    div.stButton > button {
        background-color: #FFFFFF;
        color: #1C1C1C;
        border: 1px solid #D0D0D0;
        border-radius: 6px;
        width: 100%;
        font-weight: 500;
    }
    h1, h2, h3, p, span { color: #1C1C1C !important; }
    .legend-box {
        padding: 20px;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        background-color: #FDFDFD;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data with "Smart Jitter"
@st.cache_data
def load_data():
    df = pd.read_csv('final_dashboard_ready_data.csv')
    
    # We use a smaller jitter (1.0) but rely on TRANSPARENCY 
    # so overlapping points create a darker 'glow'
    np.random.seed(42) 
    df['lat'] = df['lat'] + np.random.uniform(-1.0, 1.0, len(df))
    df['lon'] = df['lon'] + np.random.uniform(-1.0, 1.0, len(df))
    
    return df

df = load_data()

# Session State Initialization
if 'view' not in st.session_state: 
    st.session_state.view = 'Global'
if 'selected_country' not in st.session_state: 
    st.session_state.selected_country = None

# 4. COLOR MAPPING (Reduced Alpha to 140 for better overlapping visibility)
color_lookup = {
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128, 140],      
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0, 140],       
    "Arctic Storms & Volcanic Activity": [100, 100, 255, 140],       
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255, 140], 
    "Regional Meteorological Alerts (US South)": [255, 165, 0, 140]   
}

df['color'] = df['Disaster_Category'].map(color_lookup)

# --- TOP NAVIGATION BAR ---
t1, t2 = st.columns([7, 1])
with t1:
    st.title("Global Real-Time Disaster Monitor")
with t2:
    if st.button("Reset View"):
        st.session_state.view = 'Global'
        st.session_state.selected_country = None
        st.rerun()

st.divider()

# --- GLOBAL VIEW ---
if st.session_state.view == 'Global':
    col_map, col_ctrl = st.columns([3, 1])
    
    with col_map:
        view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.4, pitch=0)
        
        # PRO TIP: Adding 'stroked=True' makes dots easier to distinguish when they touch
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=180000, # Slightly smaller radius so they don't bloat the map
            pickable=True,
            stroked=True,
            filled=True,
            radius_min_pixels=5,
            line_width_min_pixels=1,
            get_line_color=[255, 255, 255] # White border around dots
        )
        
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10', 
            layers=[layer], 
            initial_view_state=view_state,
            tooltip={"text": "{location}\n{Disaster_Category}"}
        ))

    with col_ctrl:
        st.markdown('''
            <div class="legend-box">
                <h3 style="margin-top:0; font-size: 1.2rem;">Incident Legend</h3>
                <div style="line-height: 2.2;">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 14px; height: 14px; background-color: rgb(128, 0, 128); border-radius: 50%; margin-right: 12px; flex-shrink: 0;"></div>
                        <span style="font-size: 14px;">Storms & Tornadoes</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 14px; height: 14px; background-color: rgb(255, 0, 0); border-radius: 50%; margin-right: 12px; flex-shrink: 0;"></div>
                        <span style="font-size: 14px;">Earthquakes & Tsunamis</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 14px; height: 14px; background-color: rgb(100, 100, 255); border-radius: 50%; margin-right: 12px; flex-shrink: 0;"></div>
                        <span style="font-size: 14px;">Extreme Cold & Volcanic</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 14px; height: 14px; background-color: rgb(0, 255, 255); border-radius: 50%; margin-right: 12px; flex-shrink: 0;"></div>
                        <span style="font-size: 14px;">Floods & Local Alerts</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 14px; height: 14px; background-color: rgb(255, 165, 0); border-radius: 50%; margin-right: 12px; flex-shrink: 0;"></div>
                        <span style="font-size: 14px;">Regional Weather Alerts</span>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.write("") 
        st.subheader("Investigate Hotspot")
        selected = st.selectbox("Search Locations:", ["Select..."] + list(df['location'].unique()))
        
        if selected != "Select...":
            st.session_state.view = 'Detail'
            st.session_state.selected_country = selected
            st.rerun()

# --- DETAIL VIEW ---
elif st.session_state.view == 'Detail':
    country = st.session_state.selected_country
    st.subheader(f"Detailed Analysis: {country}")
    
    country_df = df[df['location'] == country]
    d_map, d_list = st.columns([2, 1])
    
    with d_map:
        detail_view = pdk.ViewState(latitude=country_df['lat'].mean(), longitude=country_df['lon'].mean(), zoom=4)
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10',
            layers=[pdk.Layer("ScatterplotLayer", country_df, get_position=["lon", "lat"], get_color="color", get_radius=50000, pickable=True)],
            initial_view_state=detail_view,
            tooltip={"text": "{Disaster_Category}"}
        ))
    
    with d_list:
        st.write(f"Showing {len(country_df)} incidents")
        for _, row in country_df.iterrows():
            st.info(f"**{row['Disaster_Category']}**\n\n{row['Tweet_Text']}")
