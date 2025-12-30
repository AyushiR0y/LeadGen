import os
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dotenv import load_dotenv
import json
from openai import AzureOpenAI
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Lead Intelligence Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded to accommodate filters
)

load_dotenv()
MAPPLS_CLIENT_ID = os.getenv("MAPPLS_CLIENT_ID")
MAPPLS_CLIENT_SECRET = os.getenv("MAPPLS_CLIENT_SECRET")

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Custom CSS (unchanged)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
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
        
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        
        .element-container {
            margin-bottom: 0;
        }
        
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
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
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
        
        .status-text {
            color: #005eac;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
            margin-right: 2rem;
        }
        
        .stTextInput {
            flex: 1;
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
        
        .stTextInput input:focus {
            border-color: #005eac !important;
            box-shadow: 0 0 0 3px rgba(0, 94, 172, 0.1) !important;
        }
        
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
        
        .metric-box {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 1.5rem;
            border-radius: 14px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            transition: all 0.3s ease;
            border: 1px solid #f1f5f9;
            overflow: hidden;
            height: 100%;
        }
        
        .metric-box:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }
        
        .metric-number {
            font-size: 2rem;
            font-weight: 700;
            color: #005eac;
            margin-bottom: 0.4rem;
            animation: countUp 0.8s ease-out;
        }
        
        .metric-text {
            font-size: 0.8rem;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            word-wrap: break-word;
        }
        
        @keyframes countUp {
            from { opacity: 0; transform: scale(0.5); }
            to { opacity: 1; transform: scale(1); }
        }
        
        .section-header {
            font-size: 1.4rem;
            font-weight: 600;
            color: #2d3748;
            margin: 2rem 0 1.5rem 0;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #e5e7eb;
            position: relative;
        }
        
        .subsection-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #005eac;
            margin: 1.5rem 0 1rem 0;
            padding-left: 1rem;
            border-left: 4px solid #005eac;
        }
        
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
        
        .chart-box {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 14px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .chart-box:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }
        
        .chart-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #005eac;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            text-align: left;
        }
        
        .simple-header {
            font-size: 0.9rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
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
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #005eac 0%, #0077cc 100%) !important;
            color: #ffffff !important;
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
            border-bottom: 2px solid #e5e7eb !important;
            padding: 1rem !important;
        }
        
        .dataframe tbody tr:hover {
            background: #fafbfc !important;
        }
        
        .filter-container {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border: 1px solid #e5e7eb;
        }
        
        .filter-header {
            font-size: 1rem;
            font-weight: 600;
            color: #005eac;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        
        .filter-header svg {
            margin-right: 0.5rem;
        }
        
        .event-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid #f1f5f9;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .event-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 94, 172, 0.15);
            border-color: #005eac;
        }
        
        .event-card-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #005eac;
            margin-bottom: 0.5rem;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .event-card-date {
            font-size: 0.75rem;
            color: #6b7280;
            font-weight: 500;
            background: #e0f2fe;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            display: inline-block;
        }
        
        .event-card-location {
            font-size: 0.7rem;
            color: #9ca3af;
            margin-top: 0.25rem;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        [data-testid="stExpander"] summary {
            font-size: 0.7rem !important;
            padding: 0.3rem 0.5rem !important;
            min-height: unset !important;
        }
        
        [data-testid="stExpander"] summary p {
            font-size: 0.7rem !important;
            margin: 0 !important;
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

@st.cache_data
def load_census_data():
    """Load all census data from new Excel file with multiple sheets"""
    try:
        # Load all sheets from Excel file
        xls = pd.ExcelFile("clean_census_combined.xlsx")
        
        # Load education data
        education_df = pd.read_excel(xls, sheet_name="education_level")
        education_df.columns = education_df.columns.str.strip()
        
        # Load occupation data
        occupation_df = pd.read_excel(xls, sheet_name="occupation_classification")
        occupation_df.columns = occupation_df.columns.str.strip()
        
        # Load industrial data
        industrial_df = pd.read_excel(xls, sheet_name="industrial_category")
        industrial_df.columns = industrial_df.columns.str.strip()
        
        return education_df, occupation_df, industrial_df
    except Exception as e:
        st.error(f"Error loading census data: {str(e)}")
        return None, None, None

pincode_df = load_pincode_data()
pca_df = load_pca_data()
education_df, occupation_df, industrial_df = load_census_data()

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
@st.cache_data(ttl=3600)
def get_location_info(pincode: str):
    info = lookup_pincode_in_csv(pincode)
    if info and info.get('lat') and info.get('lng'):
        return info
    info = mappls_geocode(f"{pincode}, India")
    return info
    
@st.cache_data(ttl=3600)
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

def get_education_data(state_name):
    """Get education level data for state from new Excel file"""
    if education_df is None:
        return None
    
    edu_df_copy = education_df.copy()
    edu_df_copy['Area Name | Area Name'] = edu_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for total data and specific state
    state_data = edu_df_copy[
        (edu_df_copy['Area Name | Area Name'] == state_name_upper) & 
        (edu_df_copy['Total/Urban/Rural | Total/Urban/Rural'] == 'Total')
    ]
    
    if not state_data.empty:
        return state_data.iloc[0]
    
    # Try India level
    india_data = edu_df_copy[
        (edu_df_copy['Area Name | Area Name'] == 'INDIA') & 
        (edu_df_copy['Total/Urban/Rural | Total/Urban/Rural'] == 'Total')
    ]
    if not india_data.empty:
        return india_data.iloc[0]
    
    return None

def get_occupation_data(state_name):
    """Get occupation classification data for state from new Excel file"""
    if occupation_df is None:
        return None
    
    occ_df_copy = occupation_df.copy()
    occ_df_copy['Area Name | Area Name'] = occ_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for total data and specific state
    state_data = occ_df_copy[
        (occ_df_copy['Area Name | Area Name'] == state_name_upper) & 
        (occ_df_copy['Total/Rural/Urban | Persons'] == 'Total')
    ]
    
    if not state_data.empty:
        return state_data
    
    # Try India level
    india_data = occ_df_copy[
        (occ_df_copy['Area Name | Area Name'] == 'INDIA') & 
        (occ_df_copy['Total/Rural/Urban | Persons'] == 'Total')
    ]
    if not india_data.empty:
        return india_data
    
    return None

def get_industrial_data(state_name):
    """Get industrial category data for state from new Excel file"""
    if industrial_df is None:
        return None
    
    ind_df_copy = industrial_df.copy()
    ind_df_copy['Area Name | Area Name'] = ind_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for total data and specific state
    state_data = ind_df_copy[
        (ind_df_copy['Area Name | Area Name'] == state_name_upper) & 
        (ind_df_copy['Total/Rural/Urban | Total/Rural/Urban'] == 'Total')
    ]
    
    if not state_data.empty:
        return state_data.iloc[0]
    
    # Try India level
    india_data = ind_df_copy[
        (ind_df_copy['Area Name | Area Name'] == 'INDIA') & 
        (ind_df_copy['Total/Rural/Urban | Total/Rural/Urban'] == 'Total')
    ]
    if not india_data.empty:
        return india_data.iloc[0]
    
    return None

def get_filtered_industrial_data(state_name, religion=None, age_group=None, gender=None, level=None, tru=None):
    """Get filtered industrial category data based on multiple dimensions"""
    if industrial_df is None:
        return None
    
    ind_df_copy = industrial_df.copy()
    ind_df_copy['Area Name | Area Name'] = ind_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for specific state or India
    if state_name_upper in ind_df_copy['Area Name | Area Name'].values:
        filtered_data = ind_df_copy[ind_df_copy['Area Name | Area Name'] == state_name_upper]
    else:
        filtered_data = ind_df_copy[ind_df_copy['Area Name | Area Name'] == 'INDIA']
    
    # Apply additional filters
    if religion and religion != 'All':
        filtered_data = filtered_data[filtered_data['Religon | Religon'] == religion]
    
    if age_group and age_group != 'All':
        filtered_data = filtered_data[filtered_data['Age group | Age group'] == age_group]
    
    if level and level != 'All':
        filtered_data = filtered_data[filtered_data['Level | Level'] == level]
    
    if tru and tru != 'All':
        filtered_data = filtered_data[filtered_data['Total/Rural/Urban | Total/Rural/Urban'] == tru]
    
    return filtered_data

def get_industrial_filter_options(state_name):
    """Get available filter options for industrial data"""
    if industrial_df is None:
        return {}, [], [], []
    
    ind_df_copy = industrial_df.copy()
    ind_df_copy['Area Name | Area Name'] = ind_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for specific state or India
    if state_name_upper in ind_df_copy['Area Name | Area Name'].values:
        state_data = ind_df_copy[ind_df_copy['Area Name | Area Name'] == state_name_upper]
    else:
        state_data = ind_df_copy[ind_df_copy['Area Name | Area Name'] == 'INDIA']
    
    # Get unique values for each filter
    religions = sorted([str(x).strip() for x in state_data['Religon | Religon'].unique() if pd.notna(x)])
    age_groups = sorted([str(x).strip() for x in state_data['Age group | Age group'].unique() if pd.notna(x)])
    levels = sorted([str(x).strip() for x in state_data['Level | Level'].unique() if pd.notna(x)])
    trus = sorted([str(x).strip() for x in state_data['Total/Rural/Urban | Total/Rural/Urban'].unique() if pd.notna(x)])
    
    religions = ['All'] + religions
    age_groups = ['All'] + age_groups
    levels = ['All'] + levels
    trus = ['All'] + trus
    
    return religions, age_groups, levels, trus
def get_education_funnel_data(state_name):
    """Get education level data for funnel chart (Matriculation, HSC, Diploma, Graduation, Masters and above)"""
    if education_df is None:
        return None
    
    edu_df_copy = education_df.copy()
    edu_df_copy['Area Name | Area Name'] = edu_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for total data and specific state
    state_data = edu_df_copy[
        (edu_df_copy['Area Name | Area Name'] == state_name_upper) & 
        (edu_df_copy['Total/Urban/Rural | Total/Urban/Rural'] == 'Total')
    ]
    
    if state_data.empty:
        state_data = edu_df_copy[
            (edu_df_copy['Area Name | Area Name'] == 'INDIA') & 
            (edu_df_copy['Total/Urban/Rural | Total/Urban/Rural'] == 'Total')
        ]
    
    if state_data.empty:
        return None
    
    row = state_data.iloc[0]
    
    # Extract education levels for funnel (with combined buckets)
    funnel_data = []
    education_funnel_levels = [
        (['Literate without educational level | Persons', 'Below educational level | Persons'], 'Illiterate'),
        (['Matric/Secondary | Persons'], 'Matriculation'),
        (['Higher secondary/Intermediate Pre-University/Senior secondary | Persons'], 'HSC'),
        (['Non-technical diploma or certificate not equal to degree | Persons', 'Technical diploma or certificate not equal to degree | Persons'], 'Diploma'),
        (['Graduate & above | Persons', 'Post Graduate | Persons'], 'Graduate & above')
    ]

    try:
        for col_names, label in education_funnel_levels:
            total_val = 0
            for col_name in col_names:
                if col_name in edu_df_copy.columns:
                    total_val += pd.to_numeric(row.get(col_name, 0), errors='coerce') or 0
            if total_val > 0:
                funnel_data.append({'Education Level': label, 'Count': total_val})
    except:
        pass
    
    if funnel_data:
        return pd.DataFrame(funnel_data)
    return None

def create_industrial_breakdown(filtered_data, gender=None):
    """Create a breakdown of industrial categories from filtered data"""
    if filtered_data is None or filtered_data.empty:
        return None
    
    # Get all column names to understand structure
    all_cols = filtered_data.columns.tolist()
    
    # Identify HHI and Non-HHI columns based on presence of keywords
    # HHI columns typically contain "Household" or "HHI"
    # Non-HHI columns typically contain "Non" or patterns without household
    
    hhi_cols = []
    non_hhi_cols = []
    
    for col in all_cols:
        col_lower = str(col).lower()
        # Skip metadata columns (case-insensitive)
        if any(x.lower() in col_lower for x in ['Area Name', 'Religon', 'Age group', 'Level', 'Total/Rural/Urban']):
            continue

        # Check gender filter
        if gender == 'Male':
            if ('males' not in col_lower) and ('male' not in col_lower):
                continue
        elif gender == 'Female':
            if ('females' not in col_lower) and ('female' not in col_lower):
                continue
        else:  # All/Persons - prefer 'Persons' aggregate columns
            if 'persons' not in col_lower and 'person' not in col_lower and 'total' not in col_lower:
                # skip gender-specific columns when showing aggregate 'All'
                continue

        # Classify as HHI or Non-HHI based on column content
        if 'household' in col_lower or 'hhi' in col_lower or '| hhi' in col_lower:
            hhi_cols.append(col)
        elif 'non' in col_lower or 'non hhi' in col_lower or 'non-hhi' in col_lower:
            non_hhi_cols.append(col)
        else:
            # If we can't determine, assume it's Non-HHI (formal industry / other)
            non_hhi_cols.append(col)
    
    # If we didn't find any categorized columns, just use all non-metadata columns
    if not hhi_cols and not non_hhi_cols:
        for col in all_cols:
            if any(x in col for x in ['Area Name', 'Religon', 'Age group', 'Level', 'Total/Rural/Urban']):
                continue
            if gender == 'Male' and ('Males' in col or 'Male' in col):
                hhi_cols.append(col)
            elif gender == 'Female' and ('Females' in col or 'Female' in col):
                hhi_cols.append(col)
            elif gender != 'Male' and gender != 'Female' and 'Persons' in col:
                hhi_cols.append(col)
    
    # Sum values across all filtered rows
    hhi_sum = 0
    non_hhi_sum = 0
    
    for col in hhi_cols:
        try:
            hhi_sum += pd.to_numeric(filtered_data[col], errors='coerce').sum()
        except:
            pass
    
    for col in non_hhi_cols:
        try:
            non_hhi_sum += pd.to_numeric(filtered_data[col], errors='coerce').sum()
        except:
            pass
    
    # Create a more detailed breakdown if possible
    hhi_details = {}
    non_hhi_details = {}
    
    # Extract subcategories from column names
    for col in hhi_cols:
        parts = col.split(' | ')
        # Extract subcategory - usually in the middle sections
        if len(parts) >= 2:
            # Skip the last part if it's gender
            if 'Males' in parts[-1] or 'Females' in parts[-1] or 'Persons' in parts[-1]:
                subcategory = ' | '.join(parts[1:-1])
            else:
                subcategory = ' | '.join(parts[1:])
            
            subcategory = subcategory.strip()
            if subcategory:
                if subcategory not in hhi_details:
                    hhi_details[subcategory] = 0
                try:
                    hhi_details[subcategory] += pd.to_numeric(filtered_data[col], errors='coerce').sum()
                except:
                    pass
    
    for col in non_hhi_cols:
        parts = col.split(' | ')
        # Extract subcategory
        if len(parts) >= 2:
            if 'Males' in parts[-1] or 'Females' in parts[-1] or 'Persons' in parts[-1]:
                subcategory = ' | '.join(parts[1:-1])
            else:
                subcategory = ' | '.join(parts[1:])
            
            subcategory = subcategory.strip()
            if subcategory:
                if subcategory not in non_hhi_details:
                    non_hhi_details[subcategory] = 0
                try:
                    non_hhi_details[subcategory] += pd.to_numeric(filtered_data[col], errors='coerce').sum()
                except:
                    pass
    
    return {
        'HHI_Total': hhi_sum,
        'Non_HHI_Total': non_hhi_sum,
        'HHI_Details': hhi_details,
        'Non_HHI_Details': non_hhi_details
    }

@st.fragment
def industrial_section(state_name):
    """Isolated fragment for industrial category analysis to prevent full page rerun"""
    if industrial_df is None:
        st.markdown('<div class="warning-box">⚠️ Industrial data not available</div>', unsafe_allow_html=True)
        return
    
    st.markdown(f'<div class="section-header">🏭 Industrial Category Analysis (State Level) </div>', unsafe_allow_html=True)
    
    # Add information about HHI vs Non-HHI
    st.markdown('''
    <div class="info-box">
        <strong>Understanding Industrial Categories:</strong><br>
        <strong>HHI (Household Industry):</strong> Small-scale manufacturing or processing activities conducted within households, including handicrafts, food processing, textile etc.<br>
        <strong>Non-HHI (Non-Household Industry):</strong> Formal industrial establishments outside of households, including factories, corporations, and other manufacturing units.
    </div>
    ''', unsafe_allow_html=True)
    
    # Get filter options
    religions, age_groups, levels, trus = get_industrial_filter_options(state_name)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        religion_filter = st.selectbox(
            "Religion", 
            religions, 
            key="religion_select"
        )
    with col2:
        age_filter = st.selectbox(
            "Age Group", 
            age_groups, 
            key="age_select"
        )
    with col3:
        tru_filter = st.selectbox(
            "Area Type", 
            trus, 
            key="tru_select"
        )
    
    gender_filter = st.radio(
        "Gender", 
        ["All", "Male", "Female"], 
        key="gender_select",
        horizontal=True
    )
    
    # Get filtered data with error handling
    try:
        filtered_data = get_filtered_industrial_data(
            state_name, 
            religion=religion_filter, 
            age_group=age_filter, 
            tru=tru_filter
        )
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        filtered_data = None
    
    if filtered_data is not None and not filtered_data.empty:
        # Create industrial breakdown
        breakdown = create_industrial_breakdown(filtered_data, gender=gender_filter)
        
        if breakdown:
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="simple-header">HHI vs Non-HHI Distribution</div>', unsafe_allow_html=True)
                
                # Create donut chart
                fig = create_vibrant_chart(
                    "donut",
                    {
                        'labels': ['HHI (Household Industry)', 'Non-HHI (Formal Industry)'],
                        'values': [breakdown['HHI_Total'], breakdown['Non_HHI_Total']],
                        'colors': ['#93c5fd', '#c4fbdd']
                    },
                    height=250
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Display key metrics
                hhi_pct = (breakdown['HHI_Total'] / (breakdown['HHI_Total'] + breakdown['Non_HHI_Total']) * 100) if (breakdown['HHI_Total'] + breakdown['Non_HHI_Total']) > 0 else 0
                non_hhi_pct = (breakdown['Non_HHI_Total'] / (breakdown['HHI_Total'] + breakdown['Non_HHI_Total']) * 100) if (breakdown['HHI_Total'] + breakdown['Non_HHI_Total']) > 0 else 0
                
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                    <div style="text-align: center; padding: 0.5rem; background: #f0f9ff; border-radius: 8px; width: 48%;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #0369a1;">{hhi_pct:.1f}%</div>
                        <div style="font-size: 0.8rem; color: #64748b;">HHI Workers</div>
                    </div>
                    <div style="text-align: center; padding: 0.5rem; background: #e7fff2; border-radius: 8px; width: 48%;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #2c563f;">{non_hhi_pct:.1f}%</div>
                        <div style="font-size: 0.8rem; color: #2c563f;">Non-HHI Workers</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="simple-header">Industrial Subcategories</div>', unsafe_allow_html=True)
                
                # Combine HHI and Non-HHI details
                all_subcategories = {}
                
                # Add HHI subcategories
                for subcat, count in breakdown['HHI_Details'].items():
                    if subcat.strip():  # Skip empty subcategories
                        all_subcategories[f"HHI: {subcat}"] = count
                
                # Add Non-HHI subcategories
                for subcat, count in breakdown['Non_HHI_Details'].items():
                    if subcat.strip():  # Skip empty subcategories
                        all_subcategories[f"Non-HHI: {subcat}"] = count
                
                if all_subcategories:
                    # Sort by count and take top 10
                    sorted_subcats = sorted(all_subcategories.items(), key=lambda x: x[1], reverse=True)
                    labels = [item[0] for item in sorted_subcats[:10]]
                    values = [item[1] for item in sorted_subcats[:10]]
                    
                    # Create treemap for better visibility of long names
                    fig = create_vibrant_chart(
                        "treemap",
                        {
                            'labels': labels,
                            'values': values,
                            'colors': ['#ffffc1' if 'HHI' in label else '#ffc9ba' for label in labels]
                        },
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    with st.expander("ℹ️ Explanation of HHI, Non-HHI & Worker Categories"):
                        st.markdown("""
                        **HHI (Household Industry)**  
                        Small, family-run, home or village-based industry work (tailoring, handloom, handicrafts, beedi rolling, pickle/papad units etc.). Usually informal, variable income.

                        **Non-HHI (Non Household Industry)**  
                        Workers in factories, registered companies, or formal sector establishments. More stable salaries → better insurance affordability.

                        ---

                        ### 👥 Main Workers
                        Worked **180+ days/year** → consistent income → strong insurance prospects.

                        ---

                        ### 🌾 Category Meaning (Non-HHI Focus)
                        **Cultivators (Non-HHI)**  
                        Work in organized / institutional farming setups. Often moderate to high earning potential → term + health insurance suitable.

                        **Agricultural Labourers (Non-HHI)**  
                        Work on others’ land for wages. Income less stable → micro-insurance / low premium plans fit better.

                        **Plantation / Livestock / Forestry / Fishing etc. (Non-HHI)**  
                        Semi-stable, seasonal but structured sector → health + income protection relevant.

                        ---

                        ### 🏦 Why This Matters for Insurance Lead-Gen
                        - **Non-HHI Main Workers → strongest leads (stable predictable income)**
                        - **HHI Workers → flexible premium plans**
                        - **Agricultural Labourers → protection-focused policies**
                        - **Cultivators / Plantation / Livestock → high family cover potential**
                        """)

                    
                else:
                    st.markdown('<div class="info-box">No subcategory data available for the selected filters.</div>', unsafe_allow_html=True)
def get_occupation_data_filtered(state_name, gender=None, area_type=None, worker_type=None):
    """Get filtered occupation data based on multiple dimensions"""
    if occupation_df is None:
        return None
    
    occ_df_copy = occupation_df.copy()
    occ_df_copy['Area Name | Area Name'] = occ_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for specific state or India
    if state_name_upper in occ_df_copy['Area Name | Area Name'].values:
        filtered_data = occ_df_copy[occ_df_copy['Area Name | Area Name'] == state_name_upper]
    else:
        filtered_data = occ_df_copy[occ_df_copy['Area Name | Area Name'] == 'INDIA']
    
    # Apply area type filter
    if area_type and area_type != 'All':
        filtered_data = filtered_data[filtered_data['Total/Rural/Urban | Total/Rural/Urban'] == area_type]
    
    return filtered_data

def get_occupation_filter_options(state_name):
    """Get available filter options for occupation data"""
    if occupation_df is None:
        return [], []
    
    occ_df_copy = occupation_df.copy()
    occ_df_copy['Area Name | Area Name'] = occ_df_copy['Area Name | Area Name'].astype(str).str.strip().str.upper()
    state_name_upper = str(state_name).strip().upper()
    
    # Filter for specific state or India
    if state_name_upper in occ_df_copy['Area Name | Area Name'].values:
        state_data = occ_df_copy[occ_df_copy['Area Name | Area Name'] == state_name_upper]
    else:
        state_data = occ_df_copy[occ_df_copy['Area Name | Area Name'] == 'INDIA']
    
    # Get unique values for area type filter
    area_types = sorted([str(x).strip() for x in state_data['Total/Rural/Urban | Total/Rural/Urban'].unique() if pd.notna(x)])
    area_types = ['All'] + area_types
    
    return area_types

def bucket_occupation_categories(nco_name):
    """Bucket NCO names into broader categories"""
    if pd.isna(nco_name):
        return "Other"
    
    nco_name = str(nco_name).upper()
    
    # Management & Leadership
    if any(x in nco_name for x in ["LEGISLATORS", "SENIOR OFFICIALS", "MANAGERS", "GENERAL MANAGERS", "CORPORATE MANAGERS"]):
        return "Management & Leadership"
    
    # Professional Services
    if any(x in nco_name for x in ["PROFESSIONALS", "ENGINEERING SCIENCE PROFESSIONALS", "LIFE SCIENCE AND HEALTH PROFESSIONALS", "TEACHING PROFESSIONALS"]):
        return "Professional Services"
    
    # Technical & Support
    if any(x in nco_name for x in ["TECHNICIANS", "ASSOCIATE PROFESSIONALS", "ENGINEERING SCIENCE ASSOCIATE PROFESSIONALS", "LIFE SCIENCE AND HEALTH ASSOCIATE PROFESSIONALS", "TEACHING ASSOCIATE PROFESSIONALS"]):
        return "Technical & Support"
    
    # Administrative & Clerical
    if any(x in nco_name for x in ["CLERKS", "OFFICE CLERKS", "CUSTOMER SERVICES CLERKS"]):
        return "Administrative & Clerical"
    
    # Sales & Service
    if any(x in nco_name for x in ["SERVICE WORKERS", "SHOP & MARKET SALES WORKERS", "PERSONAL AND PROTECTIVE SERVICE WORKERS", "MODELS, SALES PERSONS", "DEMONSTRATORS"]):
        return "Sales & Service"
    
    # Agriculture & Fishery
    if any(x in nco_name for x in ["SKILLED AGRICULTURAL", "FISHERY WORKERS", "MARKET ORIENTED SKILLED AGRICULTURAL", "SUBSISTENCE AGRICULTURAL"]):
        return "Agriculture & Fishery"
    
    # Skilled Trades
    if any(x in nco_name for x in ["CRAFT AND RELATED TRADES", "EXTRACTION AND BUILDING TRADES", "METAL, MACHINERY", "PRECISION, HANDICRAFT", "PRINTING"]):
        return "Skilled Trades"
    
    # Machine Operators
    if any(x in nco_name for x in ["PLANT AND MACHINE OPERATORS", "ASSEMBLERS", "STATIONARY PLANT", "MACHINE OPERATORS", "DRIVERS", "MOBILE-PLANT OPERATORS"]):
        return "Machine Operators"
    
    # Elementary Labor
    if any(x in nco_name for x in ["ELEMENTARY OCCUPATIONS", "SALES AND SERVICES ELEMENTARY", "AGRICULTURAL, FISHERY AND RELATED LABOURERS", "LABOURERS IN MINING", "CONSTRUCTION", "MANUFACTURING", "TRANSPORT"]):
        return "Elementary Labor"
    
    # Unclassified
    if any(x in nco_name for x in ["WORKERS NOT CLASSIFIED", "WORKERS NOT REPORTING"]):
        return "Unclassified"
    
    return "Other"

def regularize_nco_name(nco_name):
    """Regularize NCO names to make them more readable"""
    if pd.isna(nco_name):
        return "Unknown"
    
    nco_name = str(nco_name).strip()
    
    # Remove common prefixes/suffixes and clean up
    replacements = {
        "LEGISLATORS, SENIOR OFFICIALS AND MANAGERS": "Legislators & Senior Officials",
        "Legislators and Senior Officials": "Legislators & Senior Officials",
        "Corporate Managers": "Corporate Managers",
        "General Managers": "General Managers",
        "Physical, Mathematical and Engineering Science Professionals": "Engineering & Science Professionals",
        "Life Science and Health Professionals": "Health & Life Science Professionals",
        "Teaching Professionals": "Teaching Professionals",
        "Other Professionals": "Other Professionals",
        "Physical and Engineering Science Associate Professionals": "Engineering Associates",
        "Life Science and Health Associate Professionals": "Health Associates",
        "Teaching Associate Professionals": "Teaching Associates",
        "Other Associate Professionals": "Other Associates",
        "Office Clerks": "Office Clerks",
        "Customer Services Clerks": "Customer Service Clerks",
        "Personal and Protective Service Workers": "Personal & Protective Services",
        "Models, Sales Persons and Demonstrators": "Sales & Demonstrators",
        "Market Oriented Skilled Agricultural and Fishery Workers": "Commercial Agriculture & Fishery",
        "Subsistence Agricultural and Fishery Workers": "Subsistence Agriculture & Fishery",
        "Extraction and Building Trades Workers": "Construction & Extraction Trades",
        "Metal, Machinery and Related Trades Workers": "Metal & Machinery Trades",
        "Precision, Handicraft, Printing and Related Trades Workers": "Precision & Handicraft Trades",
        "Other Craft and Related Trades Workers": "Other Craft Trades",
        "Stationary Plant and Related Operators": "Stationary Plant Operators",
        "Machine Operators and Assemblers": "Machine Operators & Assemblers",
        "Drivers and Mobile-Plant Operators": "Drivers & Mobile Operators",
        "Sales and Services Elementary Occupations": "Sales & Service Elementary",
        "Agricultural, Fishery and Related Labourers": "Agriculture & Fishery Laborers",
        "Labourers in Mining, Construction, Manufacturing and Transport": "General Laborers",
        "Workers Not Reporting Any Occupations": "Unreported Occupations"
    }
    
    return replacements.get(nco_name, nco_name)

def create_occupation_visualization(filtered_data, gender, worker_type):
    """Create visualization based on occupation data and filters"""
    if filtered_data is None or filtered_data.empty:
        return None, None, None
    
    # Determine which column to use based on gender and worker type
    if worker_type == 'Employer':
        if gender == 'Male':
            count_col = 'Employer | Males'
        elif gender == 'Female':
            count_col = 'Employer | Females'
        else:
            count_col = 'Employer | Persons'
    elif worker_type == 'Employee':
        if gender == 'Male':
            count_col = 'Employee | Males'
        elif gender == 'Female':
            count_col = 'Employee | Females'
        else:
            count_col = 'Employee | Persons'
    elif worker_type == 'Single worker':
        if gender == 'Male':
            count_col = 'Single worker | Males'
        elif gender == 'Female':
            count_col = 'Single worker | Females'
        else:
            count_col = 'Single worker | Persons'
    elif worker_type == 'Family worker':
        if gender == 'Male':
            count_col = 'Family worker | Males'
        elif gender == 'Female':
            count_col = 'Family worker | Females'
        else:
            count_col = 'Family worker | Persons'
    else:  # All workers
        if gender == 'Male':
            count_col = 'Total/Rural/Urban | Males'
        elif gender == 'Female':
            count_col = 'Total/Rural/Urban | Females'
        else:
            count_col = 'Total/Rural/Urban | Persons'
    
    # Check if the count column exists
    if count_col not in filtered_data.columns:
        return None, None, None
    
    # Apply bucketing to NCO names for the distribution chart
    filtered_data = filtered_data.copy()
    filtered_data['Occupation Category'] = filtered_data['NCO name | NCO name'].apply(bucket_occupation_categories)
    filtered_data['Regularized NCO'] = filtered_data['NCO name | NCO name'].apply(regularize_nco_name)
    
    # Group by bucketed category and sum the counts (for distribution chart)
    bucketed_data = filtered_data.groupby('Occupation Category')[count_col].sum().reset_index()
    bucketed_data = bucketed_data.sort_values(count_col, ascending=False)
    
    # Get unique bucket categories for dropdown
    bucket_options = sorted(filtered_data['Occupation Category'].unique())
    
    return bucketed_data, filtered_data[['Regularized NCO', 'Occupation Category', count_col]], count_col

@st.fragment
def occupation_section(state_name):
    """Isolated fragment for occupation classification analysis to prevent full page rerun"""
    if occupation_df is None:
        st.markdown('<div class="warning-box">⚠️ Occupation data not available</div>', unsafe_allow_html=True)
        return
    
    st.markdown(f'<div class="section-header">👥 Occupation Classification Analysis (State Level) </div>', unsafe_allow_html=True)
    
    # Get filter options
    area_types = get_occupation_filter_options(state_name)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        area_filter = st.selectbox(
            "Area Type", 
            area_types, 
            key="area_type_select"
        )
    with col2:
        gender_filter = st.radio(
            "Gender", 
            ["All", "Male", "Female"], 
            key="gender_select_occ",
            horizontal=True
        )
    with col3:
        worker_type_filter = st.selectbox(
            "Worker Type", 
            ["All", "Employer", "Employee", "Single worker", "Family worker"], 
            key="worker_type_select"
        )
    
    # Get filtered data with error handling
    try:
        filtered_data = get_occupation_data_filtered(
            state_name, 
            gender=gender_filter, 
            area_type=area_filter
        )
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        filtered_data = None
    
    if filtered_data is not None and not filtered_data.empty:
        # Create visualization
        bucketed_data, detailed_data, count_col = create_occupation_visualization(
            filtered_data, 
            gender=gender_filter, 
            worker_type=worker_type_filter
        )
        
        if bucketed_data is not None and not bucketed_data.empty:
            # Create visualizations with consistent height
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="simple-header">Occupation Distribution</div>', unsafe_allow_html=True)
                
                # Create horizontal bar chart with pastel colors (bucketed data)
                fig = create_vibrant_chart(
                    "hbar",
                    {
                        'y': bucketed_data['Occupation Category'],
                        'x': bucketed_data[count_col],  # Use the actual count column
                        'colors': ['#e6f2ff', '#e6f7ff', '#e6f5ff', '#e6f9ff', '#e6f0ff', '#e6f8ff', '#e6f3ff', '#e6f4ff', '#e6f6ff', '#e6faff']
                    },
                    height=350  # Consistent height
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with col2:
                st.markdown('<div class="simple-header">Occupation Breakdown</div>', unsafe_allow_html=True)
                
                # Add bucket filter dropdown
                bucket_options = sorted(detailed_data['Occupation Category'].unique())
                selected_bucket = st.selectbox(
                    "Select Occupation Category",
                    bucket_options,
                    key="bucket_filter_select"
                )
                
                # Filter data by selected bucket
                bucket_filtered = detailed_data[detailed_data['Occupation Category'] == selected_bucket]
                bucket_filtered = bucket_filtered.groupby('Regularized NCO')[count_col].sum().reset_index()
                bucket_filtered = bucket_filtered.sort_values(count_col, ascending=False)
                
                # Create horizontal bar chart for individual NCO names
                fig = create_vibrant_chart(
                    "hbar",
                    {
                        'y': bucket_filtered['Regularized NCO'],
                        'x': bucket_filtered[count_col],  # Use the actual count column
                        'colors': ['#ffe6e6', '#ffe0e0', '#ffdada', '#ffd4d4', '#ffcece', '#ffc8c8', '#ffc2c2', '#ffbcbc', '#ffb6b6', '#ffb0b0']
                    },
                    height=270  # Same height as left chart for alignment
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Display the data table
            with st.expander("View Data Table"):
                # Show both bucketed and detailed data
                st.markdown("**Bucketed Summary:**")
                st.dataframe(
                    bucketed_data.rename(columns={
                        'Occupation Category': 'Occupation Category',
                        count_col: 'Count'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("**Detailed Breakdown (Selected Bucket):**")
                bucket_filtered_display = detailed_data[detailed_data['Occupation Category'] == selected_bucket]
                bucket_filtered_display = bucket_filtered_display.groupby('Regularized NCO')[count_col].sum().reset_index()
                bucket_filtered_display = bucket_filtered_display.sort_values(count_col, ascending=False)
                st.dataframe(
                    bucket_filtered_display.rename(columns={
                        'Regularized NCO': 'NCO Name',
                        count_col: 'Count'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.markdown('<div class="warning-box">⚠️ Unable to create visualization. Please check your filter selections.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="info-box">No data available for the selected filters. Available records: {len(filtered_data) if filtered_data is not None else 0}</div>', unsafe_allow_html=True)
@st.cache_data(ttl=86400)
def get_upcoming_events(district: str, state: str):
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        prompt = f"""You are a helpful assistant that provides information about upcoming events in India by searching recent web results.
Please provide a list of upcoming cultural events, festivals, big concerts, and parties in {district} district, {state} state, India.
For each event, provide in a chronological list:
1. Name of the event/festival
2. Date (or expected date range)
3. Address/Location
4. Short description (2-3 sentences)
5. Official website or social media (if available)
Please return the response as a JSON array with the following structure:
[
  {{
    "name": "Event Name",
    "date": "Date range",
    "address": "Specific location or venue",
    "description": "Brief description of the event",
    "website": "URL or 'Not available'"
  }}
]
Focus on events within the next 3-6 months, on or after December 2025. Ensure that the link is correct otherwise don't provide. If you don't have specific information for this district, provide general information about major festivals and cultural events typically celebrated in this region. Return at least 7-10 events.
"""
 
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides accurate information about events in India. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        events = json.loads(content)
        
        if not isinstance(events, list):
            return []
        
        return events
    
    except Exception as e:
        st.error(f"Error fetching events: {str(e)}")
        return []
         
def create_vibrant_chart(chart_type, data, height=280, bar_width=0.6, align_end=False, long_text=False):
    """Create vibrant, professional charts with varied types"""
    colors = {
        'pastel_multi': ['#a7c7e7', '#ffb3ba', '#baffc9', '#ffd9b3', '#d4b5ff', '#ffffba'],
        'pastel_blue': ['#93c5fd', '#60a5fa', '#3b82f6', '#2563eb'],
        'pastel_pair': ['#93c5fd', '#ffc9ba'],
        'pastel_gradient': ['#93c5fd', '#a7c7e7', '#bae1ff', '#cfe9ff'],
        'education': ['#ffd9b3', '#ffb3ba', '#baffc9', '#a7c7e7', '#93c5fd', '#d4b5ff', '#ffffba'],
        'pastel_light': ['#e6f2ff', '#e6f7ff', '#e6f5ff', '#e6f9ff', '#e6f0ff', '#e6f8ff', '#e6f3ff', '#e6f4ff', '#e6f6ff', '#e6faff']
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
        
    elif chart_type == "pie":
        fig = go.Figure(data=[go.Pie(
            labels=data['labels'],
            values=data['values'],
            hole=0,
            marker=dict(
                colors=data.get('colors', colors['pastel_light'][:len(data['labels'])]),
                line=dict(color='#ffffff', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(size=10, family='Poppins', color='#4b5563', weight=600),
            hovertemplate='<b>%{label}</b><br>%{value:,}<br><b>%{percent}</b><extra></extra>',
            textposition='outside'
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
            hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>',
            width=bar_width
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
            hovertemplate='<b>%{y}</b><br>%{x:,}<extra></extra>',
            width=bar_width
        )])
    
    elif chart_type == "funnel":
        fig = go.Figure(data=[go.Funnel(
            y=data['y'],
            x=data['x'],
            marker=dict(
                color=data.get('colors', colors['education'][:len(data['y'])])
            ),
            textinfo='value+percent initial',
            textfont=dict(size=11, family='Poppins', color='#4b5563', weight=600),
            hovertemplate='<b>%{y}</b><br>%{x:,}<extra></extra>'
        )])
    
    elif chart_type == "area":
        fig = go.Figure(data=[go.Scatter(
            x=data['x'],
            y=data['y'],
            fill='tozeroy',
            mode='lines',
            line=dict(color=data.get('color', '#93c5fd'), width=3),
            fillcolor=data.get('fillcolor', 'rgba(147, 197, 253, 0.3)'),
            hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>'
        )])
    
    elif chart_type == "stacked_bar":
        fig = go.Figure()
        for i, (label, values) in enumerate(data['series'].items()):
            fig.add_trace(go.Bar(
                name=label,
                x=data['x'],
                y=values,
                marker=dict(color=data.get('colors', colors['pastel_multi'])[i]),
                hovertemplate='<b>%{x}</b><br>' + label + ': %{y:,}<extra></extra>',
                width=bar_width
            ))
        fig.update_layout(barmode='stack')
    
    elif chart_type == "grouped_bar":
        fig = go.Figure()
        for i, (label, values) in enumerate(data['series'].items()):
            fig.add_trace(go.Bar(
                name=label,
                x=data['x'],
                y=values,
                marker=dict(color=data.get('colors', colors['pastel_pair'])[i]),
                hovertemplate='<b>%{x}</b><br>' + label + ': %{y:,}<extra></extra>',
                width=bar_width
            ))
        fig.update_layout(barmode='group')
    
    elif chart_type == "line":
        fig = go.Figure()
        if 'series' in data:
            for i, (label, values) in enumerate(data['series'].items()):
                fig.add_trace(go.Scatter(
                    name=label,
                    x=data['x'],
                    y=values,
                    mode='lines+markers',
                    line=dict(color=data.get('colors', colors['pastel_multi'])[i], width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>' + label + ': %{y:,}<extra></extra>'
                ))
        else:
            fig.add_trace(go.Scatter(
                x=data['x'],
                y=data['y'],
                mode='lines+markers',
                line=dict(color=data.get('color', '#93c5fd'), width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>'
            ))
    
    elif chart_type == "treemap":
        fig = go.Figure(data=[go.Treemap(
            labels=data['labels'],
            parents=data.get('parents', [''] * len(data['labels'])),
            values=data['values'],
            marker=dict(
                colors=data.get('colors', colors['pastel_multi'][:len(data['labels'])]),
                line=dict(color='#ffffff', width=2)
            ),
            textfont=dict(size=11, family='Poppins', color='#4b5563', weight=600),
            hovertemplate='<b>%{label}</b><br>%{value:,}<extra></extra>',
            textinfo='label+value'
        )])
    
    # Adjust margins for long text in horizontal bar charts
    if chart_type == "hbar" and long_text:
        margin_left = 250  # Increased left margin for long text
    else:
        margin_left = 0
    
    fig.update_layout(
        margin=dict(l=margin_left, r=20, t=10, b=0),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True if chart_type in ["stacked_bar", "grouped_bar", "line"] else False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, family='Poppins')
        ) if chart_type in ["stacked_bar", "grouped_bar", "line"] else {},
        font=dict(family='Poppins', size=11, color='#6b7280'),
        hovermode='closest'
    )
    
    if chart_type in ["bar", "hbar", "stacked_bar", "grouped_bar", "line", "area"]:
        fig.update_xaxes(showgrid=False, showline=False, zeroline=False, tickfont=dict(color='#6b7280'))
        fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9', showline=False, zeroline=False, tickfont=dict(color='#6b7280'))
        
        # For horizontal bar charts, align to one end if requested and handle long text
        if chart_type == "hbar":
            if align_end:
                fig.update_layout(
                    xaxis=dict(
                        side="bottom",
                        autorange="reversed" if data.get('x', [0])[0] < 0 else None
                    )
                )
            
            if long_text:
                # Enable text wrapping for long labels
                fig.update_yaxes(
                    tickmode='array',
                    tickvals=list(range(len(data['y']))),
                    ticktext=data['y'],
                    automargin=True,
                    tickfont=dict(size=9, family='Poppins', color='#4b5563')
                )
    
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

# Search
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
                
                # Location info
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
                        st.markdown(f'<div class="section-header">📊 Demographics Overview ({data_level})</div>', unsafe_allow_html=True)
                        
                        # Basic Stats Cards
                        total_pop = int(demo_data.get('TOT_P', 0))
                        total_hh = int(demo_data.get('No_HH', 0))
                        male_pop = int(demo_data.get('TOT_M', 0))
                        female_pop = int(demo_data.get('TOT_F', 0))
                        literate = int(demo_data.get('P_LIT', 0))
                        working = int(demo_data.get('TOT_WORK_P', 0))
                        
                        literacy_rate = (literate / total_pop * 100) if total_pop > 0 else 0
                        work_rate = (working / total_pop * 100) if total_pop > 0 else 0
                        sex_ratio = int((female_pop / male_pop * 1000)) if male_pop > 0 else 0
                        avg_hh_size = round(total_pop / total_hh, 2) if total_hh > 0 else 0
                        
                        # Key Metrics Row
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        
                        with col1:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{total_pop:,}</div><div class="metric-text">Population</div></div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{total_hh:,}</div><div class="metric-text">Households</div></div>', unsafe_allow_html=True)
                        with col3:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{sex_ratio}</div><div class="metric-text">Sex Ratio</div></div>', unsafe_allow_html=True)
                        with col4:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{avg_hh_size}</div><div class="metric-text">Avg HH Size</div></div>', unsafe_allow_html=True)
                        with col5:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{literacy_rate:.1f}%</div><div class="metric-text">Literacy</div></div>', unsafe_allow_html=True)
                        with col6:
                            st.markdown(f'<div class="metric-box"><div class="metric-number">{work_rate:.1f}%</div><div class="metric-text">Working</div></div>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        # Show PCA row fields to help map occupation columns when needed
                        try:
                            with st.expander('PCA fields for this selected area'):
                                st.write(list(demo_data.index))
                        except Exception:
                            pass
                        
                        # Population Breakdown Section
                        st.markdown('<div class="subsection-header">👥 Population Breakdown</div>', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown('<div class="simple-header">Gender Distribution</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "donut",
                                {'labels': ['Male', 'Female'], 'values': [male_pop, female_pop], 'colors': ['#93c5fd', '#ffc9ba']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        with col2:
                            child_0_6 = int(demo_data.get('P_06', 0))
                            youth = int((total_pop - child_0_6) * 0.33)
                            adult = int((total_pop - child_0_6) * 0.42)
                            senior = total_pop - child_0_6 - youth - adult
                            
                            st.markdown('<div class="simple-header">Age Distribution</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "pie",
                                {'labels': ['0-6', '7-25', '26-50', '50+'], 'values': [child_0_6, youth, adult, senior], 
                                 'colors': ['#baffc9', '#a7c7e7', '#93c5fd', '#d4b5ff']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        with col3:
                            sc_pop = int(demo_data.get('P_SC', 0))
                            st_pop = int(demo_data.get('P_ST', 0))
                            other_pop = total_pop - sc_pop - st_pop
                            
                            st.markdown('<div class="simple-header">Social Composition</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "treemap",
                                {'labels': ['General', 'SC', 'ST'], 'values': [other_pop, sc_pop, st_pop], 
                                 'colors': ['#d4b5ff', '#ffd9b3', '#a7c7e7']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        # Education & Work Section
                        st.markdown('<div class="subsection-header">🎓 Education & Employment</div>', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown('<div class="simple-header">Literacy Status</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "donut",
                                {'labels': ['Literate', 'Illiterate'], 
                                 'values': [literate, int(demo_data.get('P_ILL', 0))], 
                                 'colors': ['#baffc9', '#ffb3ba']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        with col2:
                            st.markdown('<div class="simple-header">Work Participation</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "pie",
                                {'labels': ['Working', 'Non-Working'], 
                                 'values': [working, int(demo_data.get('NON_WORK_P', 0))], 
                                 'colors': ['#a7c7e7', '#e5e7eb']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        with col3:
                            male_workers = int(demo_data.get('TOT_WORK_M', 0))
                            female_workers = int(demo_data.get('TOT_WORK_F', 0))
                            
                            st.markdown('<div class="simple-header">Workers by Gender</div>', unsafe_allow_html=True)
                            fig = create_vibrant_chart(
                                "grouped_bar",
                                {'x': ['Workers'],
                                 'series': {'Male': [male_workers], 'Female': [female_workers]}, 
                                 'colors': ['#93c5fd', '#ffc9ba']}
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        # Education Level Data (State level)
                        if education_df is not None:
                            
                            funnel_df = get_education_funnel_data(state_name)
                            if funnel_df is not None and not funnel_df.empty:
                                # Display funnel and literacy side-by-side
                                col_funnel, col_lit = st.columns([1, 1])
                                with col_funnel:
                                    st.markdown('<div class="simple-header">Education Funnel (State Level) </div>', unsafe_allow_html=True)
                                    fig_funnel = go.Figure(go.Funnel(
                                        x=funnel_df['Count'],
                                        y=funnel_df['Education Level'],
                                        marker=dict(
                                            color=['#ffd9b3', '#ffb3ba', '#baffc9', '#a7c7e7'],
                                            line=dict(color='white', width=2)
                                        ),
                                        textposition='inside',
                                        textinfo='value+percent initial',
                                        hovertemplate='<b>%{y}</b><br>Count: %{x:,.0f}<extra></extra>'
                                    ))

                                    fig_funnel.update_layout(
                                        xaxis_title='Number of Persons',
                                        yaxis_title='Education Level',
                                        height=360,
                                        width=520,
                                        margin=dict(l=40, r=20, t=40, b=40),
                                        template='plotly_white',
                                        font=dict(size=11)
                                    )
                                    st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': True})

                                with col_lit:
                                    st.markdown('<div class="simple-header">Literacy Rate by Gender</div>', unsafe_allow_html=True)
                                    male_literacy = (int(demo_data.get('M_LIT', 0)) / male_pop * 100) if male_pop > 0 else 0
                                    female_literacy = (int(demo_data.get('F_LIT', 0)) / female_pop * 100) if female_pop > 0 else 0
                                    fig_lit = create_vibrant_chart(
                                        "line",
                                        {'x': ['Male', 'Female'], 
                                         'y': [male_literacy, female_literacy],
                                         'color': '#93c5fd'},
                                        height=360
                                    )
                                    st.plotly_chart(fig_lit, use_container_width=True, config={'displayModeBar': False})

                        # Industrial Category with Multi-level Filters
                        if industrial_df is not None:
                            industrial_section(state_name)
                        # Occupation Classification with Multi-level Filters
                        if occupation_df is not None:
                            occupation_section(state_name)

                        # end of education/occupation/industrial processing section
                # Upcoming Events Section
                st.markdown('<div class="section-header">🎉 Upcoming Events in the Area</div>', unsafe_allow_html=True)
                
                with st.spinner(f"Fetching upcoming events for {district_name}, {state_name}..."):
                    events = get_upcoming_events(district_name, state_name)
                
                if events:
                    # Sort events chronologically
                    def parse_date(date_str):
                        """Simple date parser for sorting"""
                        try:
                            # Try various date formats
                            for fmt in ["%B %d, %Y", "%B %Y", "%d %B %Y", "%Y-%m-%d"]:
                                try:
                                    return datetime.strptime(date_str.split('-')[0].strip(), fmt)
                                except:
                                    continue
                            return datetime(2099, 12, 31)  # Put unparseable dates at end
                        except:
                            return datetime(2099, 12, 31)
                    
                    events_sorted = sorted(events, key=lambda x: parse_date(x.get('date', '')))
                    
                    st.markdown(f'<div class="info-box">📅 Found {len(events_sorted)} upcoming events in {district_name} district</div>', unsafe_allow_html=True)
                    
                    # Display events in cards - 5 per row
                    num_events = len(events_sorted)
                    num_rows = (num_events + 4) // 5  # Ceiling division
                    
                    for row in range(num_rows):
                        cols = st.columns(5)
                        for col_idx in range(5):
                            event_idx = row * 5 + col_idx
                            if event_idx < num_events:
                                event = events_sorted[event_idx]
                                with cols[col_idx]:
                                    with st.container():
                                        st.markdown(f'''
                                        <div class="event-card">
                                            <div>
                                                <div class="event-card-title">{event.get('name', 'Unnamed Event')}</div>
                                                <div class="event-card-date">📅 {event.get('date', 'TBD')}</div>
                                            </div>
                                            <div class="event-card-location">📍 {event.get('address', 'Location TBD')}</div>
                                        </div>
                                        ''', unsafe_allow_html=True)
                                        
                                        # Expandable details
                                        with st.expander("View Details", expanded=False):
                                            st.markdown(f"**📝 Description:**")
                                            st.write(event.get('description', 'No description available'))
                                            
                                            st.markdown(f"**📍 Full Address:**")
                                            st.info(event.get('address', 'Not specified'))
                                            
                                            if event.get('website') and event['website'].lower() != 'not available':
                                                st.markdown(f"**🌐 Website:** [{event['website']}]({event['website']})")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Export button
                    events_df = pd.DataFrame(events_sorted)
                    csv_data = events_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Export Events to CSV",
                        data=csv_data,
                        file_name=f"upcoming_events_{district_name}_{pincode}.csv",
                        mime="text/csv",
                        key="events_export",
                        use_container_width=False
                    )
                else:
                    st.markdown('<div class="warning-box">⚠️ Unable to fetch upcoming events at this time. Please try again later.</div>', unsafe_allow_html=True)
                # Business Leads
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
st.markdown('<div style="text-align: center; color: #9ca3af; padding: 1.5rem; font-size: 0.85rem; border-top: 1px solid #e5e7eb;">Bajaj Life LeadGen • Source: https://censusindia.gov.in/ </div>', unsafe_allow_html=True)






