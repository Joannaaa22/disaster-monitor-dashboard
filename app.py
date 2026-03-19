import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config
st.set_page_config(page_title="DisasterMonitor AI", layout="wide", initial_sidebar_state="collapsed")

# 2. THEME & STYLING
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
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
    
    /* Text Colors */
    h1, h2, h3, p, span { color: #1C1C1C !important; }
    
    /* Legend Box Styling */
    .legend-box {
        padding: 15px;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        background-color: #FDFDFD;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }

    .legend-circle {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 12px;
        border: 1px solid rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    data = pd.read_csv('final_dashboard_ready_data.csv')
    return data

df = load_data()

# Session State Initialization
if 'view' not in st.session_state: 
    st.session_state.view = 'Global'
if 'selected_country' not in st.session_state: 
    st.session_state.selected_country = None

# --- 4. CONFIGURATION (Source of Truth) ---
DISASTER_CONFIG = {
    "Severe Meteorological (Tornado/Hail)": {
        "label": "Storms & Tornadoes",
        "color": [128, 0, 128, 200]  # Purple
    },
    "Geological (Japan Earthquake/Tsunami)": {
        "label": "Earthquakes & Tsunamis",
        "color": [255, 0, 0, 200]    # Red
    },
    "Arctic Storms & Volcanic Activity": {
        "label": "Arctic & Volcanic Activity",
        "color": [100, 100, 255, 200] # Blue
    },
    "Hydrological (Flash Floods) & Social Reports": {
        "label": "Floods & Social Alerts",
        "color": [0, 200, 200, 200]  # Darker Cyan for visibility
    },
    "Regional Meteorological Alerts (US South)": {
        "label": "Regional Weather",
        "color": [255, 165, 0, 200]  # Orange
    }
}

# --- 5. DATA PREPARATION ---
# Explicitly map colors and labels to ensure Pydeck can read the lists correctly
def get_color(cat):
    return DISASTER_CONFIG.get(cat, {"color": [150, 150, 150, 200]})["color"]

def get_label(cat):
    return DISASTER_CONFIG.get(cat, {"label": cat})["label"]

df['color'] = df['Disaster_Category'].apply(get_color)
df['display_label'] = df['Disaster_Category'].apply(get_label)

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
        
        # We use a ScatterplotLayer with explicit color handling
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            get_color="color", # This looks at the 'color' column which is a list [R, G, B, A]
            get_radius=220000,
            pickable=True,
            filled=True,
        )
        
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10', 
            layers=[layer], 
            initial_view_state=view_state,
            tooltip={"text": "{location}\nCategory: {display_label}"}
        ))

    with col_ctrl:
        # --- DYNAMIC LEGEND ---
        legend_html = '<div class="legend-box"><h3 style="margin-top:0; font-size: 1.1rem; margin-bottom:15px;">Incident Legend</h3>'
        for cat, info in DISASTER_CONFIG.items():
            # Convert RGB list to string for CSS
            c = info['color']
            rgb_str = f"rgb({c[0]}, {c[1]}, {c[2]})"
            
            legend_html += f'''
                <div class="legend-item">
                    <div class="legend-circle" style="background-color: {rgb_str};"></div>
                    <span style="font-size: 13px; font-weight: 500; color: #333;">{info['label']}</span>
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
            get_radius=40000,
            pickable=True,
        )
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10',
            layers=[detail_layer],
            initial_view_state=detail_view,
            tooltip={"text": "Category: {display_label}"}
        ))
    
    with d_list:
        st.write(f"Showing {len(country_df)} incidents")
        for _, row in country_df.iterrows():
            # Use the cleaner label in the info box too
            st.info(f"**{row['display_label']}**\n\n{row['Tweet_Text']}")
