import os
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="Lead Intelligence Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_dotenv()
MAPPLS_CLIENT_ID = os.getenv("MAPPLS_CLIENT_ID")
MAPPLS_CLIENT_SECRET = os.getenv("MAPPLS_CLIENT_SECRET")

# Custom CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Global */
        * {
            font-family: 'Poppins', -apple-system, sans-serif;
        }
        
        .stApp {
            background: #fefefe;
        }
        
        #MainMenu, footer, .stDeployButton, header {
            visibility: hidden;
            display: none;
        }
        
        /* Remove Streamlit spacing */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        
        .element-container {
            margin-bottom: 0;
        }
        
        /* Header with shimmer */
        .main-header {
            background: linear-gradient(135deg, #005eac 0%, #0077cc 100%);
            padding: 2.5rem 3rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0, 94, 172, 0.15);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.2),
                transparent
            );
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        .main-header h1 {
            color: #ffffff !important;
            margin: 0;
            font-size: 2.2rem;
            font-weight: 600;
            position: relative;
            z-index: 1;
        }
        
        .main-header p {
            color: #ffffff !important;
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            font-weight: 400;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }
        
        /* Status text */
        .status-text {
            color: #005eac;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
            margin-right: 2rem;
        }
        
        /* Search section - remove extra spacing */
        .search-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 0 !important;
        }
        
        .stTextInput {
            flex: 1;
            margin-bottom: 0 !important;
        }
        
        .stTextInput > div {
            margin-bottom: 0 !important;
        }
        
        .stTextInput > div > div {
            background: #ffffff !important;
            margin-bottom: 0 !important;
        }
        
        .stTextInput input {
            background: #ffffff !important;
            border: 2px solid #eef0f2 !important;
            border-radius: 12px !important;
            padding: 0.9rem 1.3rem !important;
            font-size: 1rem !important;
            color: #2d3748 !important;
            font-weight: 500 !important;
        }
        
        .stTextInput input::placeholder {
            color: #9ca3af !important;
            font-weight: 400 !important;
        }
        
        .stTextInput input:focus {
            border-color: #005eac !important;
            box-shadow: 0 0 0 3px rgba(0, 94, 172, 0.1) !important;
        }
        
        /* Button */
        .stButton > button {
            background: linear-gradient(135deg, #005eac 0%, #0077cc 100%) !important;
            color: #ffffff !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(0, 94, 172, 0.2) !important;
            width: 80%;
            height: 50%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 94, 172, 0.3) !important;
        }
        
        /* 3D Cards */
        .card-3d {
            background: #ffffff;
            padding: 1.75rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 
                        0 1px 3px rgba(0, 0, 0, 0.06);
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .card-3d:hover {
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1), 
                        0 6px 12px rgba(0, 0, 0, 0.06);
            transform: translateY(-4px);
        }
        
        /* Metric cards */
        .metric-box {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 1.5rem;
            border-radius: 14px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            transition: box-shadow 0.3s ease, border-color 0.3s ease;
            border: 1px solid #f1f5f9;

            /* 🔑 important */
            overflow: hidden;
            height: 100%;
        }

        

        /* Chart title INSIDE card */
        .chart-title {
            font-size: 0.95rem;
            font-weight: 800;
            color: #005eac;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            text-align: left;
        }

        /* Number */
        .metric-number {
            font-size: 2rem;
            font-weight: 700;
            color: #005eac;
            margin-bottom: 0.4rem;
            animation: countUp 0.8s ease-out;
            transition: transform 0.3s ease;
        }

        /* Text */
        .metric-text {
            font-size: 0.8rem;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;

            /* 🔑 prevents text overflow */
            word-wrap: break-word;
        }

        /* Count animation */
        @keyframes countUp {
            from { opacity: 0; transform: scale(0.5); }
            to { opacity: 1; transform: scale(1); }
        }

        
        /* Section headers - single line only */
        .section-header {
            font-size: 1.4rem;
            font-weight: 600;
            color: #2d3748;
            margin: 2rem 0 1.5rem 0;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #e5e7eb;
            position: relative;
        }
        
        /* Location card */
        .loc-label {
            font-size: 0.75rem;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.4rem;
        }
        
        .loc-value {
            font-size: 1rem;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 1.2rem;
        }
        
        /* Chart container - includes both title and chart */
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        
        .chart-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #005eac;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: #ffffff;
            padding: 0.75rem;
            border-radius: 14px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            border: 1px solid #f1f5f9;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: none !important;
            color: #6b7280;
            font-weight: 600;
            padding: 0.7rem 1.3rem;
            border-radius: 10px;
            transition: all 0.2s;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #f8fafc;
            color: #005eac;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #005eac 0%, #0077cc 100%) !important;
            color: #ffffff !important;
        }
        
        /* DataFrames - WHITE background */
        .stDataFrame {
            border: none !important;
        }
        
        div[data-testid="stDataFrame"] {
            border: none !important;
        }
        
        div[data-testid="stDataFrame"] > div {
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            overflow: hidden !important;
            background: #ffffff !important;
        }
        
        .dataframe {
            border: none !important;
            color: #2d3748 !important;
            background: #ffffff !important;
        }
        
        .dataframe thead tr th {
            background: #f8fafc !important;
            color: #2d3748 !important;
            font-weight: 600 !important;
            border: none !important;
            border-bottom: 2px solid #e5e7eb !important;
            padding: 1rem !important;
            font-size: 0.85rem !important;
        }
        
        .dataframe tbody tr td {
            border: none !important;
            border-bottom: 1px solid #f1f5f9 !important;
            padding: 0.9rem !important;
            color: #4b5563 !important;
            font-size: 0.9rem !important;
            background: #ffffff !important;
        }
        
        .dataframe tbody tr:hover {
            background: #fafbfc !important;
        }
        
        /* Map - light styling */
        .stMap > div {
            border-radius: 14px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important;
            border: 1px solid #e5e7eb !important;
        }
        
        /* Force light mode on map */
        .mapboxgl-map {
            background: #f8fafc !important;
        }
        
        /* Info boxes */
        .info-box {
            background: #e0f2fe;
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            color: #005eac;
            font-weight: 500;
            border-left: 4px solid #005eac;
        }
        
        .warning-box {
            background: #fff7ed;
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            color: #c2410c;
            font-weight: 500;
            border-left: 4px solid #f58220;
        }
        
        /* Download button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #f58220 0%, #ff9d4d 100%) !important;
            color: #ffffff !important;
            border: none !important;
            padding: 0.7rem 1.5rem !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 8px rgba(245, 130, 32, 0.2) !important;
            transition: all 0.3s ease !important;
        }
        
        .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(245, 130, 32, 0.3) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load data functions
@st.cache_data
def load_pincode_data():
    try:
        df = pd.read_csv("pincode.csv")
        df.columns = df.columns.str.strip().str.lower()
        df['district'] = df['district'].astype(str).str.strip().str.upper()
        df['statename'] = df['statename'].astype(str).str.strip().str.upper()
        return df
    except:
        return None

@st.cache_data
def load_pca_data():
    try:
        df = pd.read_excel("pca_demographics.xlsx")
        df.columns = df.columns.str.strip()
        return df
    except:
        try:
            df = pd.read_csv("pca_demographics.csv", encoding='utf-8')
            df.columns = df.columns.str.strip()
            return df
        except:
            try:
                df = pd.read_csv("pca_demographics.csv", encoding='latin-1')
                df.columns = df.columns.str.strip()
                return df
            except:
                return None

pincode_df = load_pincode_data()
pca_df = load_pca_data()

_mappls_token = None
_mappls_token_expiry = 0

def get_mappls_token(force_refresh=False):
    global _mappls_token, _mappls_token_expiry
    if not force_refresh and _mappls_token and time.time() < _mappls_token_expiry:
        return _mappls_token
    if not MAPPLS_CLIENT_ID or not MAPPLS_CLIENT_SECRET:
        return None
    token_url = "https://outpost.mappls.com/api/security/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": MAPPLS_CLIENT_ID,
        "client_secret": MAPPLS_CLIENT_SECRET,
    }
    try:
        r = requests.post(token_url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        access_token = data.get("access_token")
        token_type = data.get("token_type", "bearer")
        expires_in = data.get("expires_in", 3600)
        if not access_token:
            return None
        _mappls_token = f"{token_type} {access_token}"
        _mappls_token_expiry = time.time() + int(expires_in) - 60
        return _mappls_token
    except:
        return None

def lookup_pincode_in_csv(pincode: str):
    if pincode_df is None:
        return None
    result = pincode_df[pincode_df['pincode'].astype(str).str.strip() == str(pincode)]
    if result.empty:
        return None
    row = result.iloc[0]
    district = row.get('district', 'N/A')
    state = row.get('statename', 'N/A')
    return {
        "formatted_address": f"{row.get('officename', 'Unknown')}, {district}, {state}, {pincode}",
        "locality": row.get('officename', 'N/A'),
        "city": district,
        "state": state,
        "district": district,
        "lat": float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
        "lng": float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
        "eloc": None,
        "source": "Local Database"
    }

def mappls_geocode(address_text: str):
    token = get_mappls_token()
    if not token:
        return None
    url = "https://atlas.mappls.com/api/places/geocode"
    headers = {"Authorization": token}
    params = {"address": address_text, "region": "IND"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except:
        return None
    if isinstance(data.get("copResults"), dict):
        best = data["copResults"]
    elif isinstance(data.get("copResults"), list):
        results = data.get("copResults", [])
        if not results:
            return None
        best = results[0]
    else:
        return None
    lat = best.get("latitude") or best.get("lat")
    lng = best.get("longitude") or best.get("lng")
    return {
        "formatted_address": best.get("formattedAddress") or address_text,
        "eloc": best.get("eLoc"),
        "locality": best.get("locality"),
        "subLocality": best.get("subLocality"),
        "city": best.get("city"),
        "state": best.get("state"),
        "district": best.get("district"),
        "lat": lat,
        "lng": lng,
        "source": "Mappls API"
    }

def get_location_info(pincode: str):
    info = lookup_pincode_in_csv(pincode)
    if info and info.get('lat') and info.get('lng'):
        return info
    info = mappls_geocode(f"{pincode}, India")
    return info

def mappls_nearby(lat: float, lng: float, keyword: str, radius: int = 10000):
    if lat is None or lng is None:
        return []
    token = get_mappls_token()
    if not token:
        return []
    url = "https://atlas.mappls.com/api/places/nearby/json"
    headers = {"Authorization": token}
    all_rows = []
    page = 1
    max_pages = 10
    while page <= max_pages:
        params = {
            "keywords": keyword,
            "refLocation": f"{lat},{lng}",
            "radius": radius,
            "page": page,
            "sortBy": "dist:asc",
        }
        try:
            r = requests.get(url, headers=headers, params=params, timeout=15)
            if r.status_code == 401:
                token = get_mappls_token(force_refresh=True)
                if not token:
                    break
                headers = {"Authorization": token}
                r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            content_type = r.headers.get('content-type', '')
            if 'application/json' not in content_type:
                break
            data = r.json()
        except:
            break
        results = data.get("suggestedLocations", [])
        if not results:
            break
        for res in results:
            distance_m = res.get("distance", 0)
            distance_km = round(distance_m / 1000, 2) if distance_m else None
            all_rows.append({
                "Name": res.get("placeName") or res.get("poi") or "N/A",
                "Address": res.get("placeAddress") or res.get("address") or "N/A",
                "Distance": distance_km,
            })
        page_info = data.get("pageInfo", {})
        total_pages = page_info.get("totalPages", 1)
        if page >= total_pages:
            break
        page += 1
    return all_rows

def get_demographics_data(district_name, state_name):
    if pca_df is None:
        return None, "No Data"
    pca_df_copy = pca_df.copy()
    pca_df_copy['Name'] = pca_df_copy['Name'].astype(str).str.strip().str.upper()
    pca_df_copy['State'] = pca_df_copy['State'].astype(str).str.strip().str.upper()
    pca_df_copy['Level'] = pca_df_copy['Level'].astype(str).str.strip()
    pca_df_copy['TRU'] = pca_df_copy['TRU'].astype(str).str.strip()
    district_name_upper = str(district_name).strip().upper()
    state_name_upper = str(state_name).strip().upper()
    
    district_data = pca_df_copy[
        (pca_df_copy['Name'] == district_name_upper) & 
        (pca_df_copy['Level'] == 'DISTRICT') &
        (pca_df_copy['TRU'] == 'Total')
    ]
    if not district_data.empty:
        return district_data.iloc[0], f"District: {district_name}"
    
    district_words = district_name_upper.replace(' DISTRICT', '').replace(' CITY', '').split()
    all_districts = pca_df_copy[
        (pca_df_copy['Level'] == 'DISTRICT') &
        (pca_df_copy['TRU'] == 'Total')
    ]
    best_match = None
    best_match_score = 0
    for idx, row in all_districts.iterrows():
        pca_name = row['Name'].replace(' DISTRICT', '').replace(' CITY', '')
        pca_words = pca_name.split()
        match_score = sum(1 for word in district_words if word in pca_words)
        reverse_score = sum(1 for word in pca_words if word in district_words)
        total_score = match_score + reverse_score
        if total_score > best_match_score and total_score >= 1:
            best_match_score = total_score
            best_match = row
    if best_match is not None:
        return best_match, f"District: {best_match['Name']}"
    
    state_by_name = pca_df_copy[
        (pca_df_copy['Name'] == state_name_upper) & 
        (pca_df_copy['Level'] == 'STATE') &
        (pca_df_copy['TRU'] == 'Total')
    ]
    if not state_by_name.empty:
        return state_by_name.iloc[0], f"State: {state_name}"
    
    india_data = pca_df_copy[
        (pca_df_copy['Level'] == 'India') &
        (pca_df_copy['TRU'] == 'Total')
    ]
    if not india_data.empty:
        return india_data.iloc[0], "India (National Average)"
    return None, "No Data"

def create_vibrant_chart(chart_type, data, height=260):
    

    """Create vibrant, professional charts with pastel colors"""
    colors = {
        'pastel_multi': ['#a7c7e7', '#ffb3ba', '#baffc9', '#ffd9b3', '#d4b5ff', '#ffffba'],
        'pastel_blue': ['#93c5fd', '#60a5fa', '#3b82f6', '#2563eb'],
        'pastel_pair': ['#93c5fd', '#ffc9ba'],
        'pastel_gradient': ['#93c5fd', '#a7c7e7', '#bae1ff', '#cfe9ff']
    }
    
    fig = None
    
    if chart_type == "donut":
        fig = go.Figure(data=[go.Pie(
            labels=data['labels'],
            values=data['values'],
            hole=0.65,
            marker=dict(
                colors=data.get('colors', colors['pastel_multi'][:len(data['labels'])]),
                line=dict(color='#ffffff', width=3)
            ),
            textinfo='percent',
            textfont=dict(size=12, family='Poppins', color='#4b5563', weight=600),
            hovertemplate='<b>%{label}</b><br>%{value:,}<br><b>%{percent}</b><extra></extra>'
        )])
        
    elif chart_type == "bar":
        fig = go.Figure(data=[go.Bar(
            x=data['x'],
            y=data['y'],
            marker=dict(
                color=data.get('colors', colors['pastel_multi'][:len(data['x'])]),
                line=dict(width=0)
            ),
            text=data.get('text', data['y']),
            texttemplate='<b>%{text:,.0f}</b>',
            textposition='outside',
            textfont=dict(size=10, family='Poppins', color='#4b5563', weight=600),
            hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>'
        )])
        
    elif chart_type == "hbar":
        fig = go.Figure(data=[go.Bar(
            y=data['y'],
            x=data['x'],
            orientation='h',
            marker=dict(
                color=data.get('colors', colors['pastel_gradient'][:len(data['y'])]),
                line=dict(width=0)
            ),
            text=data.get('text', data['x']),
            texttemplate='<b>%{text:,.0f}</b>',
            textposition='outside',
            textfont=dict(size=10, family='Poppins', color='#4b5563', weight=600),
            hovertemplate='<b>%{y}</b><br>%{x:,}<extra></extra>'
        )])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(family='Poppins', size=11, color='#6b7280'),
        hovermode='closest'
    )

    
    if chart_type in ["bar", "hbar"]:
        fig.update_xaxes(showgrid=False, showline=False, zeroline=False, tickfont=dict(color='#6b7280'))
        fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9', showline=False, zeroline=False, tickfont=dict(color='#6b7280'))
    
    if fig is None:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    return fig

# ============= UI =============

st.markdown("""
    <div class="main-header">
        <h1>🎯 Lead Intelligence Dashboard</h1>
        <p>Discover business opportunities with demographic insights</p>
    </div>
""", unsafe_allow_html=True)

# Status
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if pincode_df is not None:
        st.markdown(f'<span class="status-text">✓ {len(pincode_df):,} locations</span>', unsafe_allow_html=True)
with col2:
    if pca_df is not None:
        st.markdown('<span class="status-text">✓ Demographics loaded</span>', unsafe_allow_html=True)

# Search - NO extra spacing
col1, col2 = st.columns([6, 1])
with col1:
    pincode = st.text_input(
        "Search",
        max_chars=6,
        placeholder="Enter 6-digit pincode (e.g., 400059)",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("Search", use_container_width=True, type="primary")

if search_button and pincode:
    if len(pincode) != 6 or not pincode.isdigit():
        st.markdown('<div class="warning-box">⚠️ Please enter a valid 6-digit pincode</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Analyzing..."):
            geo = get_location_info(pincode)
            
            if not geo:
                st.markdown('<div class="warning-box">❌ Location not found</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="section-header">📍 Location Details</div>', unsafe_allow_html=True)
                
                # Location info - same level as map
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"<div class='loc-label'>Address</div><div class='loc-value'>{geo['formatted_address']}</div>", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"<div class='loc-label'>District</div><div class='loc-value'>{geo.get('district', 'N/A')}</div>", unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"<div class='loc-label'>State</div><div class='loc-value'>{geo.get('state', 'N/A')}</div>", unsafe_allow_html=True)
                    
                    lat, lng = geo.get('lat'), geo.get('lng')
                    if lat and lng:
                        st.markdown(f"<div style='font-size: 0.8rem; color: #6b7280; font-weight: 500;'>📍 {lat:.6f}, {lng:.6f}</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if lat and lng:
                        map_df = pd.DataFrame([{"lat": lat, "lon": lng}])
                        st.map(map_df, zoom=11, height=280)
                
                # Demographics
                district_name = geo.get('district', '')
                state_name = geo.get('state', '')
                
                if district_name and state_name and pca_df is not None:
                    demo_data, data_level = get_demographics_data(district_name, state_name)
                    
                    if demo_data is not None:
                        st.markdown(f'<div class="section-header">📊 Demographics ({data_level})</div>', unsafe_allow_html=True)
                        
                        # Metrics
                        
                        total_pop = int(demo_data.get('TOT_P', 0))
                        total_hh = int(demo_data.get('No_HH', 0))
                        male_pop = int(demo_data.get('TOT_M', 0))
                        female_pop = int(demo_data.get('TOT_F', 0))
                        literate = int(demo_data.get('P_LIT', 0))
                        working = int(demo_data.get('TOT_WORK_P', 0))
                        
                        literacy_rate = (literate / total_pop * 100) if total_pop > 0 else 0
                        work_rate = (working / total_pop * 100) if total_pop > 0 else 0
                        
                        
                        
                        # Charts - 3 per row, title and chart in same box
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown('<div class="chart-title">Gender Distribution</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "donut",
                                {'labels': ['Male', 'Female'], 'values': [male_pop, female_pop], 'colors': ['#93c5fd', '#ffc9ba']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown('<div class="chart-title">Education Status</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "donut",
                                {'labels': ['Literate', 'Illiterate'], 'values': [literate, int(demo_data.get('P_ILL', 0))], 'colors': ['#baffc9', '#e5e7eb']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown('<div class="chart-title">Employment Status</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "donut",
                                {'labels': ['Working', 'Non-Working'], 'values': [working, int(demo_data.get('NON_WORK_P', 0))], 'colors': ['#a7c7e7', '#e5e7eb']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Second row
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            sc_pop = int(demo_data.get('P_SC', 0))
                            st_pop = int(demo_data.get('P_ST', 0))
                            other_pop = total_pop - sc_pop - st_pop
                            
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown('<div class="chart-title">Social Composition</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "bar",
                                {'x': ['General', 'SC', 'ST'], 'y': [other_pop, sc_pop, st_pop], 'colors': ['#d4b5ff', '#ffd9b3', '#a7c7e7']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            male_workers = int(demo_data.get('TOT_WORK_M', 0))
                            female_workers = int(demo_data.get('TOT_WORK_F', 0))
                            
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown('<div class="chart-title">Workers by Gender</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "hbar",
                                {'y': ['Male', 'Female'], 'x': [male_workers, female_workers], 'colors': ['#93c5fd', '#ffc9ba']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col3:
                            child_0_6 = int(demo_data.get('P_06', 0))
                            youth = int((total_pop - child_0_6) * 0.33)
                            adult = int((total_pop - child_0_6) * 0.42)
                            senior = total_pop - child_0_6 - youth - adult
                            
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown('<div class="chart-title">Age Groups</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "bar",
                                {'x': ['0-6', '7-25', '26-50', '50+'], 'y': [child_0_6, youth, adult, senior], 'colors': ['#baffc9', '#a7c7e7', '#93c5fd', '#d4b5ff']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            st.markdown('</div>', unsafe_allow_html=True)

                # Leads
                st.markdown('<div class="section-header">🎯 Business Leads (10km radius)</div>', unsafe_allow_html=True)
                
                if lat and lng:
                    token = get_mappls_token()
                    if not token:
                        st.markdown('<div class="warning-box">⚠️ API unavailable</div>', unsafe_allow_html=True)
                    else:
                        with st.spinner("Finding leads..."):
                            industries = mappls_nearby(lat, lng, keyword="industry")
                            insurance = mappls_nearby(lat, lng, keyword="insurance")
                            clubs = mappls_nearby(lat, lng, keyword="club")
                            banks = mappls_nearby(lat, lng, keyword="bank")
                            colleges = mappls_nearby(lat, lng, keyword="college")
                            medical = mappls_nearby(lat, lng, keyword="hospital")
                        
                        # Summary
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        
                        with col1:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{len(industries)}</div><div class="metric-text">Industries</div></div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{len(insurance)}</div><div class="metric-text">Insurance</div></div>', unsafe_allow_html=True)
                        with col3:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{len(clubs)}</div><div class="metric-text">Clubs</div></div>', unsafe_allow_html=True)
                        with col4:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{len(banks)}</div><div class="metric-text">Banks</div></div>', unsafe_allow_html=True)
                        with col5:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{len(colleges)}</div><div class="metric-text">Colleges</div></div>', unsafe_allow_html=True)
                        with col6:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{len(medical)}</div><div class="metric-text">Medical</div></div>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Tabs
                        tabs = st.tabs(["🏢 Industries", "🛡️ Insurance", "🤝 Clubs", "🏦 Banks", "🎓 Colleges", "🏥 Medical"])
                        
                        all_data = [industries, insurance, clubs, banks, colleges, medical]
                        names = ["Industries", "Insurance", "Clubs", "Banks", "Colleges", "Medical"]
                        
                        for tab, data, name in zip(tabs, all_data, names):
                            with tab:
                                if data:
                                    df = pd.DataFrame(data).head(50)
                                    df = df[['Name', 'Address', 'Distance']]
                                    df.columns = ['Name', 'Address', 'Distance (km)']
                                    st.dataframe(df, use_container_width=True, hide_index=True, height=400)
                                    
                                    csv = df.to_csv(index=False).encode('utf-8')
                                    st.download_button(f"📥 Export {name}", csv, f"{name.lower()}_{pincode}.csv", "text/csv")
                                else:
                                    st.markdown(f'<div class="info-box">No {name.lower()} found in this area</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #9ca3af; padding: 1.5rem; font-size: 0.85rem; border-top: 1px solid #e5e7eb;">Lead Intelligence Dashboard • Powered by Mappls & Census Data</div>', unsafe_allow_html=True)