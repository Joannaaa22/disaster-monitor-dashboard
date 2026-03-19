import streamlit as st
import pandas as pd
import pydeck as pdk

# ... (Previous Page Config & CSS remain the same) ...

# 3. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# --- 4. CONFIGURATION (Source of Truth) ---
# This dictionary maps the messy CSV names to Clean Labels and RGB Colors
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

# Apply colors and clean labels to the dataframe
df['color'] = df['Disaster_Category'].map(lambda x: DISASTER_CONFIG.get(x, {"color": [150, 150, 150, 180]})['color'])
df['display_label'] = df['Disaster_Category'].map(lambda x: DISASTER_CONFIG.get(x, {"label": x})['label'])

# --- TOP NAVIGATION BAR ---
# (Keep your existing Navigation Bar code here)

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
            tooltip={"text": "{location}\n{display_label}"} # Using the clean label
        ))

    with col_ctrl:
        # --- IMPROVED DYNAMIC LEGEND ---
        legend_html = '<div class="legend-box"><h3 style="margin-top:0; font-size: 1.1rem;">Incident Types</h3>'
        
        for cat, info in DISASTER_CONFIG.items():
            # Convert [R, G, B, A] to rgb string for HTML
            rgb_color = f"rgb({info['color'][0]}, {info['color'][1]}, {info['color'][2]})"
            
            legend_html += f'''
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 16px; height: 16px; background-color: {rgb_color}; 
                                border-radius: 50%; margin-right: 12px; border: 1px solid rgba(0,0,0,0.1);"></div>
                    <span style="font-size: 13px; color: #333; font-weight: 500;">{info['label']}</span>
                </div>
            '''
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)
        
        st.write("") 
        st.subheader("Investigate Hotspot")
        selected = st.selectbox("Search Locations:", ["Select..."] + list(df['location'].unique()))
        
        if selected != "Select...":
            st.session_state.view = 'Detail'
            st.session_state.selected_country = selected
            st.rerun()

# --- DETAIL VIEW ---
# (Apply the same 'display_label' logic to your Tooltip in Detail View as well)
