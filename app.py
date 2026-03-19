import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config
st.set_page_config(page_title="DisasterMonitor AI", layout="wide", initial_sidebar_state="collapsed")

# 2. THEME & STYLING
st.markdown("""
    <style>
    /* Hide Sidebar */
    [data-testid="stSidebar"] { display: none; }
    
    /* Main background */
    .stApp { background-color: #FFFFFF; }
    
    /* Custom Reset Button Styling */
    div.stButton > button {
        background-color: #FFFFFF;
        color: #1C1C1C;
        border: 1px solid #D0D0D0;
        border-radius: 6px;
        width: 100%;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #F0F2F6;
        border-color: #1C1C1C;
    }
    
    /* Text Colors */
    h1, h2, h3, p, span { color: #1C1C1C !important; }
    
    /* Legend Box Styling */
    .legend-box {
        padding: 20px;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        background-color: #FDFDFD;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# Session State Initialization
if 'view' not in st.session_state: 
    st.session_state.view = 'Global'
if 'selected_country' not in st.session_state: 
    st.session_state.selected_country = None

# 4. COLOR MAPPING (Source of Truth for Map)
color_lookup = {
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128, 180],      # Purple
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0, 180],       # Red
    "Arctic Storms & Volcanic Activity": [100, 100, 255, 180],       # Blue
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255, 180], # Cyan
    "Regional Meteorological Alerts (US South)": [255, 165, 0, 180]   # Orange
}

df['color'] = df['Disaster_Category'].map(color_lookup)

# --- TOP NAVIGATION BAR ---
t1, t2 = st.columns([7, 1])
with t1:
    st.title("Global Real-Time Disaster Monitor") # EMOJI REMOVED
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
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=220000,
            pickable=True,
        )
        st.pydeck_chart(pdk.Deck(
            map_style='light', 
            layers=[layer], 
            initial_view_state=view_state,
            tooltip={"text": "{location}\n{Disaster_Category}"}
        ))

    with col_ctrl:
        # ✅ UPDATED LEGEND (CSS CIRCLES + CLEAN NAMES)
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
    st.subheader(f"Detailed Analysis: {country}") # PIN EMOJI REMOVED
    
    country_df = df[df['location'] == country]
    
    d_map, d_list = st.columns([2, 1])
    
    with d_map:
        detail_view = pdk.ViewState(
            latitude=country_df['lat'].mean(), 
            longitude=country_df['lon'].mean(), 
            zoom=4, 
            pitch=0
        )
        detail_layer = pdk.Layer(
            "ScatterplotLayer",
            country_df,
            get_position=["lon", "lat"],
            get_color="color", 
            get_radius=50000,
            pickable=True,
        )
        st.pydeck_chart(pdk.Deck(
            map_style='light',
            layers=[detail_layer],
            initial_view_state=detail_view,
            tooltip={"text": "{Disaster_Category}"}
        ))
    
    with d_list:
        st.write(f"Showing {len(country_df)} incidents")
        for _, row in country_df.iterrows():
            st.info(f"**{row['Disaster_Category']}**\n\n{row['Tweet_Text']}")
