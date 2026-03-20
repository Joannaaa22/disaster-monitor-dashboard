import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# 1. Page Config
st.set_page_config(page_title="ResQlytics", layout="wide", initial_sidebar_state="collapsed")

# 2. THEME & STYLING
st.markdown("""
    <style>
    /* Hide Sidebar */
    [data-testid="stSidebar"] { display: none; }
    
    /* Main background */
    .stApp { background-color: #FFFFFF; }

    /* REDUCE TOP SPACING: Removes padding between header and map */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* LOGO & TEXT INJECTION INTO TOP BAR */
    header[data-testid="stHeader"] {
        background-color: #262730 !important;
    }

    header[data-testid="stHeader"]::before {
        content: "";
        background-image: url('https://img.icons8.com/ios-filled/50/FFC107/pulse.png');
        background-size: contain;
        background-repeat: no-repeat;
        position: absolute;
        left: 20px;
        top: 12px;
        width: 30px;
        height: 30px;
    }
    
    header[data-testid="stHeader"]::after {
        content: "ResQlytics";
        position: absolute;
        left: 60px;
        top: 14px;
        color: #FFFFFF;
        font-weight: 800;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 1.25rem;
        letter-spacing: -0.5px;
    }

    /* Standardized Text Colors */
    h1, h2, h3, .stSubheader, b, strong, p, span, label { 
        color: #262730 !important; 
    }
    
    .secondary-text {
        color: #8C8C8C !important;
        font-size: 0.85rem;
    }

    hr { border-top: 1px solid #E6E6E6 !important; margin: 10px 0 !important; }
    
    /* OVERLAY LEGEND STYLING */
    .map-container { position: relative; }
    
    .legend-overlay {
        position: absolute;
        bottom: 25px;
        left: 25px;
        z-index: 1000;
        padding: 15px;
        border: 1px solid #E6E6E6;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        pointer-events: none;
    }

    .location-list {
        max-height: 120px;
        overflow-y: auto;
        padding: 8px;
        border: 1px solid #E6E6E6;
        border-radius: 5px;
        background-color: #FAFAF8;
        font-size: 0.82rem;
        color: #8C8C8C !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Overlay Legend Function
def render_map_legend():
    st.markdown('''
        <div class="legend-overlay">
            <b style="font-size: 0.9rem; margin-bottom: 8px; display: block; color: #262730;">Incident Legend</b>
            <div style="display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: rgb(128, 0, 128); border: 1px solid rgba(80,80,80,0.5); border-radius: 50%; margin-right: 8px;"></div>
                    <span style="font-size: 11px; color: #262730;">Storms & Tornadoes</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: rgb(255, 0, 0); border: 1px solid rgba(80,80,80,0.5); border-radius: 50%; margin-right: 8px;"></div>
                    <span style="font-size: 11px; color: #262730;">Earthquakes & Tsunamis</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: rgb(100, 100, 255); border: 1px solid rgba(80,80,80,0.5); border-radius: 50%; margin-right: 8px;"></div>
                    <span style="font-size: 11px; color: #262730;">Extreme Cold & Volcanic</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: rgb(0, 255, 255); border: 1px solid rgba(80,80,80,0.5); border-radius: 50%; margin-right: 8px;"></div>
                    <span style="font-size: 11px; color: #262730;">Floods & Local Alerts</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: rgb(255, 165, 0); border: 1px solid rgba(80,80,80,0.5); border-radius: 50%; margin-right: 8px;"></div>
                    <span style="font-size: 11px; color: #262730;">Regional Weather Alerts</span>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('final_dashboard_ready_data.csv').dropna(subset=['lat', 'lon'])
    np.random.seed(42) 
    df['lat'] = df['lat'] + np.random.uniform(-1.0, 1.0, len(df))
    df['lon'] = df['lon'] + np.random.uniform(-1.0, 1.0, len(df))
    return df

df = load_data()

# Logic / Mappings
if 'view' not in st.session_state: st.session_state.view = 'Global'
if 'selected_country' not in st.session_state: st.session_state.selected_country = None

color_lookup = {
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128, 160],      
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0, 160],       
    "Arctic Storms & Volcanic Activity": [100, 100, 255, 160],       
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255, 160], 
    "Regional Meteorological Alerts (US South)": [255, 165, 0, 160]   
}
clean_name_lookup = {
    "Severe Meteorological (Tornado/Hail)": "Storms & Tornadoes",
    "Geological (Japan Earthquake/Tsunami)": "Earthquakes & Tsunamis",
    "Arctic Storms & Volcanic Activity": "Extreme Cold & Volcanic",
    "Hydrological (Flash Floods) & Social Reports": "Floods & Local Alerts",
    "Regional Meteorological Alerts (US South)": "Regional Weather Alerts"
}
df['color'] = df['Disaster_Category'].map(color_lookup)
df['Clean_Category'] = df['Disaster_Category'].map(clean_name_lookup)

# --- MAIN APP LOGIC ---
if st.session_state.view == 'Global':
    # Side-by-side layout: Map (3/4) and Controls (1/4)
    col_map, col_ctrl = st.columns([3, 1])
    
    with col_ctrl:
        st.subheader("1. Investigate Hotspot")
        selected_loc = st.selectbox("Search by Location:", ["Select..."] + sorted(list(df['location'].unique())), key="loc_filter")
        if selected_loc != "Select...":
            st.session_state.view = 'Detail'; st.session_state.selected_country = selected_loc; st.rerun()

        st.divider()
        st.subheader("2. Filter by Disaster")
        selected_cat = st.selectbox("Select Category:", ["All Incidents"] + list(clean_name_lookup.values()), key="cat_filter")
        
        filtered_df = df if selected_cat == "All Incidents" else df[df['Clean_Category'] == selected_cat]
        if selected_cat != "All Incidents":
            regions = sorted(filtered_df['location'].unique())
            st.markdown(f'<span class="secondary-text">Active in:</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="location-list">{" • ".join(regions)}</div>', unsafe_allow_html=True)

    with col_map:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.4, pitch=0)
        layer = pdk.Layer(
            "ScatterplotLayer", filtered_df, get_position=["lon", "lat"],
            get_color="color", get_radius=180000, pickable=True, stroked=True, filled=True,
            radius_min_pixels=5, line_width_min_pixels=1, get_line_color=[80, 80, 80, 120]
        )
        st.pydeck_chart(pdk.Deck(
            map_style='light', 
            layers=[layer], 
            initial_view_state=view_state, 
            tooltip={"text": "{location}\nCategory: {Clean_Category}"},
            height=650 # Keeps map compact within the screen view
        ))
        render_map_legend()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == 'Detail':
    # Keeping Reset button only on Detail page to allow returning to home
    if st.button("← Back to Global View"):
        st.session_state.view = 'Global'
        st.session_state.selected_country = None
        st.rerun()

    country = st.session_state.selected_country
    st.subheader(f"Detailed Analysis: {country}")
    country_df = df[df['location'] == country]
    d_map, d_list = st.columns([2, 1])
    
    with d_map:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        dv = pdk.ViewState(latitude=country_df['lat'].mean(), longitude=country_df['lon'].mean(), zoom=4)
        dl = pdk.Layer("ScatterplotLayer", country_df, get_position=["lon", "lat"], get_color="color", get_radius=50000, pickable=True, stroked=True, get_line_color=[80, 80, 80, 120])
        st.pydeck_chart(pdk.Deck(map_style='light', layers=[dl], initial_view_state=dv, height=500))
        render_map_legend()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with d_list:
        st.markdown(f'<span class="secondary-text">Showing {len(country_df)} incidents</span>', unsafe_allow_html=True)
        for _, row in country_df.iterrows():
            st.info(f"**{row['Clean_Category']}**\n\n{row['Tweet_Text']}")
