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
    
    /* Custom Circle Swatch for Legend */
    .legend-circle {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 12px;
        display: inline-block;
        border: 1px solid rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    # Ensure the CSV is in the same directory
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# Session State Initialization
if 'view' not in st.session_state: 
    st.session_state.view = 'Global'
if 'selected_country' not in st.session_state: 
    st.session_state.selected_country = None

# --- 4. CONFIGURATION (Source of Truth) ---
# Maps the CSV category names to "Clean Labels" and "RGB Colors"
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
        "label": "Arctic & Volcanic Activity",
        "color": [100, 100, 255, 180] # Blue
    },
    "Hydrological (Flash Floods) & Social Reports": {
        "label": "Floods & Social Alerts",
        "color": [0, 255, 255, 180]  # Cyan
    },
    "Regional Meteorological Alerts (US South)": {
        "label": "Regional Weather",
        "color": [255, 165, 0, 180]  # Orange
    }
}

# Map the colors and friendly labels back to the dataframe
df['color'] = df['Disaster_Category'].map(lambda x: DISASTER_CONFIG.get(x, {"color": [150, 150, 150, 180]})['color'])
df['display_label'] = df['Disaster_Category'].map(lambda x: DISASTER_CONFIG.get(x, {"label": x})['label'])

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
            tooltip={"text": "{location}\nCategory: {display_label}"}
        ))

    with col_ctrl:
        # --- DYNAMIC LEGEND ---
        legend_html = '<div class="legend-box"><h3 style="margin-top:0; font-size: 1.1rem;">Incident Legend</h3>'
        for cat, info in DISASTER_CONFIG.items():
            rgb = f"rgb({info['color'][0]}, {info['color'][1]}, {info['color'][2]})"
            legend_html += f'''
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div class="legend-circle" style="background-color: {rgb};"></div>
                    <span style="font-size: 13px; font-weight: 500;">{info['label']}</span>
                </div>
            '''
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)
        
        st.write("") 
        st.subheader("Investigate Hotspot")
        selected = st.selectbox("Search Locations:", ["Select..."] + sorted(list(df['location'].unique())))
        
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
            tooltip={"text": "Category: {display_label}"}
        ))
    
    with d_list:
        st.write(f"Showing {len(country_df)} incidents")
        for _, row in country_df.iterrows():
            st.info(f"**{row['display_label']}**\n\n{row['Tweet_Text']}")
