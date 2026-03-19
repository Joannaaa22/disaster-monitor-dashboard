import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

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
        padding: 15px;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        background-color: #FDFDFD;
        margin-top: 20px;
    }
    
    /* Scrollable list for filtered locations */
    .location-list {
        max-height: 200px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #F0F2F6;
        border-radius: 5px;
        background-color: #FAFAFA;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper function to render the legend
def render_legend(vertical=False):
    # Adjust layout based on where it is placed
    layout_style = "display: flex; flex-direction: column; gap: 10px;" if vertical else "display: flex; flex-wrap: wrap; gap: 20px;"
    
    st.markdown(f'''
        <div class="legend-box">
            <h3 style="margin-top:0; font-size: 1.1rem; color: #1C1C1C;">Incident Legend</h3>
            <div style="{layout_style} line-height: 1.5;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 14px; height: 14px; background-color: rgb(128, 0, 128); border: 1.5px solid rgba(80, 80, 80, 0.5); border-radius: 50%; margin-right: 8px; flex-shrink: 0;"></div>
                    <span style="font-size: 13px;">Storms & Tornadoes</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 14px; height: 14px; background-color: rgb(255, 0, 0); border: 1.5px solid rgba(80, 80, 80, 0.5); border-radius: 50%; margin-right: 8px; flex-shrink: 0;"></div>
                    <span style="font-size: 13px;">Earthquakes & Tsunamis</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 14px; height: 14px; background-color: rgb(100, 100, 255); border: 1.5px solid rgba(80, 80, 80, 0.5); border-radius: 50%; margin-right: 8px; flex-shrink: 0;"></div>
                    <span style="font-size: 13px;">Extreme Cold & Volcanic</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 14px; height: 14px; background-color: rgb(0, 255, 255); border: 1.5px solid rgba(80, 80, 80, 0.5); border-radius: 50%; margin-right: 8px; flex-shrink: 0;"></div>
                    <span style="font-size: 13px;">Floods & Local Alerts</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 14px; height: 14px; background-color: rgb(255, 165, 0); border: 1.5px solid rgba(80, 80, 80, 0.5); border-radius: 50%; margin-right: 8px; flex-shrink: 0;"></div>
                    <span style="font-size: 13px;">Regional Weather Alerts</span>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# 3. Load Data with Jittering
@st.cache_data
def load_data():
    df = pd.read_csv('final_dashboard_ready_data.csv')
    df = df.dropna(subset=['lat', 'lon'])
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

# 4. COLOR MAPPING & DISASTER LABELS
color_lookup = {
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128, 160],      
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0, 160],       
    "Arctic Storms & Volcanic Activity": [100, 100, 255, 160],       
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255, 160], 
    "Regional Meteorological Alerts (US South)": [255, 165, 0, 160]   
}

# Mapping messy CSV names to the clean legend names
clean_name_lookup = {
    "Severe Meteorological (Tornado/Hail)": "Storms & Tornadoes",
    "Geological (Japan Earthquake/Tsunami)": "Earthquakes & Tsunamis",
    "Arctic Storms & Volcanic Activity": "Extreme Cold & Volcanic",
    "Hydrological (Flash Floods) & Social Reports": "Floods & Local Alerts",
    "Regional Meteorological Alerts (US South)": "Regional Weather Alerts"
}

df['color'] = df['Disaster_Category'].map(color_lookup)
df['Clean_Category'] = df['Disaster_Category'].map(clean_name_lookup)

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
    
    with col_ctrl:
        st.subheader("1. Investigate Hotspot")
        selected_loc = st.selectbox("Search by Location:", ["Select..."] + sorted(list(df['location'].unique())), key="loc_filter")
        
        if selected_loc != "Select...":
            st.session_state.view = 'Detail'
            st.session_state.selected_country = selected_loc
            st.rerun()

        st.write("---")
        st.subheader("2. Filter by Disaster")
        selected_cat = st.selectbox("Select Category:", ["All Incidents"] + list(clean_name_lookup.values()), key="cat_filter")
        
        # Filtering logic for the map
        if selected_cat == "All Incidents":
            filtered_df = df
        else:
            filtered_df = df[df['Clean_Category'] == selected_cat]
            # List regions where this disaster exists
            regions = sorted(filtered_df['location'].unique())
            st.write(f"**Locations with {selected_cat}:**")
            st.markdown(f'<div class="location-list">{" • ".join(regions)}</div>', unsafe_allow_html=True)

        # Legend at the bottom of the right column
        render_legend(vertical=True)

    with col_map:
        view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.4, pitch=0)
        layer = pdk.Layer(
            "ScatterplotLayer",
            filtered_df, # Use the filtered dataframe
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=180000,
            pickable=True,
            stroked=True,
            filled=True,
            radius_min_pixels=5,
            line_width_min_pixels=1,
            get_line_color=[80, 80, 80, 120] 
        )
        st.pydeck_chart(pdk.Deck(
            map_style='light', 
            layers=[layer], 
            initial_view_state=view_state,
            tooltip={"text": "{location}\nCategory: {Clean_Category}"}
        ))

# --- DETAIL VIEW ---
elif st.session_state.view == 'Detail':
    country = st.session_state.selected_country
    st.subheader(f"Detailed Analysis: {country}")
    
    country_df = df[df['location'] == country]
    d_map, d_list = st.columns([2, 1])
    
    with d_map:
        if not country_df.empty:
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
                stroked=True,
                filled=True,
                radius_min_pixels=5,
                line_width_min_pixels=1,
                get_line_color=[80, 80, 80, 120] 
            )
            
            st.pydeck_chart(pdk.Deck(
                map_style='light',
                layers=[detail_layer],
                initial_view_state=detail_view,
                tooltip={"text": "{Clean_Category}"}
            ))
        else:
            st.warning("No data found for this location.")
            
        # Legend under map in Detail View
        render_legend(vertical=False)
    
    with d_list:
        st.write(f"Showing {len(country_df)} incidents")
        for _, row in country_df.iterrows():
            st.info(f"**{row['Clean_Category']}**\n\n{row['Tweet_Text']}")
