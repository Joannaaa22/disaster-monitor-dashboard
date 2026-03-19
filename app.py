import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config
st.set_page_config(page_title="DisasterMonitor AI", layout="wide", initial_sidebar_state="collapsed")

# 2. SESSION STATE INITIALIZATION
if 'view' not in st.session_state: 
    st.session_state.view = 'Global'
if 'selected_country' not in st.session_state: 
    st.session_state.selected_country = None

# 3. THEME & STYLING
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    
    /* Main background remains white */
    .stApp { background-color: #FFFFFF; }
    
    /* Global Text Color set to #0E1117 */
    h1, h2, h3, p, span, label, .stSelectbox label { 
        color: #0E1117 !important; 
    }
    
    h1 { 
        font-weight: 800 !important;
    }
    
    /* Legend Box Styling */
    .legend-box {
        padding: 15px;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        background-color: #F9F9F9;
    }
    
    /* Custom Reset Button Styling */
    div.stButton > button {
        background-color: #FFFFFF;
        color: #0E1117;
        border: 1px solid #D0D0D0;
        border-radius: 6px;
        width: 100%;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# --- 5. CENTRAL CONFIGURATION ---
DISASTER_CONFIG = {
    "Severe Meteorological (Tornado/Hail)": {
        "label": "Storms & Tornadoes",
        "color": [128, 0, 128, 180]  # Purple
    },
    "Geological (Japan Earthquake/Tsunami)": {
        "label": "Earthquakes & Tsunamis",
        "color": [255, 0, 0, 180]    # Red
    },
    "Arctic Storms & Volcanic Activity": {
        "label": "Extreme Cold & Volcanic",
        "color": [100, 100, 255, 180] # Blue
    },
    "Hydrological (Flash Floods) & Social Reports": {
        "label": "Floods & Local Alerts",
        "color": [0, 255, 255, 180]  # Cyan
    },
    "Regional Meteorological Alerts (US South)": {
        "label": "Regional Weather Alerts",
        "color": [255, 165, 0, 180]  # Orange
    }
}

# Apply logic to DataFrame
df['color'] = df['Disaster_Category'].apply(lambda x: DISASTER_CONFIG.get(x, {"color": [150, 150, 150, 180]})['color'])
df['display_label'] = df['Disaster_Category'].apply(lambda x: DISASTER_CONFIG.get(x, {"label": x})['label'])

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

# --- APP LOGIC ---
view_mode = st.session_state.get('view', 'Global')

if view_mode == 'Global':
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
        
        # RESTORED MAP OUTLINE: map_style='mapbox://styles/mapbox/light-v10'
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10', 
            layers=[layer], 
            initial_view_state=view_state,
            tooltip={"text": "{location}\nCategory: {display_label}"}
        ))

    with col_ctrl:
        st.subheader("Incident Legend")
        
        # Build HTML content safely for the legend
        legend_items_html = ""
        for key, info in DISASTER_CONFIG.items():
            rgb = f"rgb({info['color'][0]}, {info['color'][1]}, {info['color'][2]})"
            legend_items_html += f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 15px; height: 15px; background-color: {rgb}; border-radius: 50%; margin-right: 12px;"></div>
                    <span style="font-size: 14px; color: #0E1117; font-weight: 500;">{info['label']}</span>
                </div>
            """
        
        # Render legend box
        st.markdown(f'<div class="legend-box">{legend_items_html}</div>', unsafe_allow_html=True)
        
        st.write("") 
        st.subheader("Investigate Hotspot")
        locations = sorted(list(df['location'].unique()))
        selected = st.selectbox("Search Locations:", ["Select..."] + locations)
        
        if selected != "Select...":
            st.session_state.view = 'Detail'
            st.session_state.selected_country = selected
            st.rerun()

elif view_mode == 'Detail':
    country = st.session_state.get('selected_country')
    st.subheader(f"Detailed Analysis: {country}")
    
    country_df = df[df['location'] == country]
    d_map, d_list = st.columns([2, 1])
    
    with d_map:
        detail_view = pdk.ViewState(
            latitude=country_df['lat'].mean(), longitude=country_df['lon'].mean(), 
            zoom=4, pitch=0
        )
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10',
            layers=[pdk.Layer("ScatterplotLayer", country_df, get_position=["lon", "lat"], 
                               get_color="color", get_radius=50000, pickable=True)],
            initial_view_state=detail_view,
            tooltip={"text": "{display_label}"}
        ))
    
    with d_list:
        st.write(f"Showing {len(country_df)} incidents")
        for _, row in country_df.iterrows():
            st.info(f"**{row['display_label']}**\n\n{row['Tweet_Text']}")
