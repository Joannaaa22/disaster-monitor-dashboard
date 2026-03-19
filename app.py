import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Config
st.set_page_config(page_title="Global Crisis Monitor", layout="wide")

# 2. THEME & BUTTON STYLING (Clean & Minimalist)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E0E0E0;
        padding-top: 20px;
    }
    /* FIX FOR RESET BUTTON: Light background, Dark text */
    div.stButton > button {
        background-color: #FFFFFF;
        color: #1C1C1C;
        border: 1px solid #D0D0D0;
        border-radius: 8px;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #E0E0E0;
        border-color: #1C1C1C;
        color: #000000;
    }
    h1, h2, h3, p { color: #1C1C1C !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    return pd.read_csv('final_dashboard_ready_data.csv')

df = load_data()

# Initialize Session State
if 'view' not in st.session_state: st.session_state.view = 'Global'

# 4. SIDEBAR (First thing is Legend, then Button)
st.sidebar.subheader("Disaster Legend")
st.sidebar.markdown("""
<div style="line-height: 2.2; margin-bottom: 20px;">
    <span style="color: rgb(100, 100, 255); font-size: 20px;">●</span> Arctic/Volcanic<br>
    <span style="color: rgb(255, 0, 0); font-size: 20px;">●</span> Japan Earthquake<br>
    <span style="color: rgb(255, 165, 0); font-size: 20px;">●</span> US South Storms<br>
    <span style="color: rgb(0, 255, 255); font-size: 20px;">●</span> Floods/Social<br>
    <span style="color: rgb(128, 0, 128); font-size: 20px;">●</span> Tornado/Hail
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Reset to Global View"):
    st.session_state.view = 'Global'
    st.session_state.selected_country = None
    st.rerun()

# 5. Color Mapping Logic
color_lookup = {
    "Arctic Storms & Volcanic Activity": [100, 100, 255, 160],
    "Geological (Japan Earthquake/Tsunami)": [255, 0, 0, 160],
    "Regional Meteorological Alerts (US South)": [255, 165, 0, 160],
    "Hydrological (Flash Floods) & Social Reports": [0, 255, 255, 160],
    "Severe Meteorological (Tornado/Hail)": [128, 0, 128, 160]
}
df['color'] = df['Disaster_Category'].map(color_lookup)

# --- GLOBAL VIEW ---
if st.session_state.view == 'Global':
    st.title("Global Real-Time Disaster Map")
    
    # Zoom set to 2.0 to ensure outlines are visible
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=2.0, pitch=0)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=180000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style='light', 
        layers=[layer], 
        initial_view_state=view_state,
        tooltip={"text": "Location: {location}\nCategory: {Disaster_Category}"}
    ))
    
    st.divider()
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
        st.map(country_df) 
    
    with col2:
        st.subheader("Incident Reports")
        for _, row in country_df.iterrows():
            st.info(f"**{row['Disaster_Category']}**\n\n{row['Tweet_Text']}")
