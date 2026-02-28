"""
EV/PHEV Selection Tool - Complete Web Application
With Heatmaps and Advanced Charts
Run with: streamlit run ev_selector_app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
from collections import Counter

# ============================================
# PAGE CONFIGURATION (Must be first!)
# ============================================

st.set_page_config(
    page_title="EV/PHEV Selector",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS STYLING
# ============================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem;
        background: #181c24;
        color: #f3f6fa;
    }
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #42a5f5, #00bcd4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #b0b8c1;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Cards */
    .vehicle-card {
        background: #232a36;
        color: #f3f6fa;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        border-left: 5px solid #42a5f5;
    }
    .metric-card {
        background: linear-gradient(135deg, #283e51 0%, #485563 100%);
        color: #f3f6fa;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #232a36 0%, #2c3440 100%);
        color: #f3f6fa;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2ecc71;
    }
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #181c24 0%, #232a36 100%);
        color: #f3f6fa;
    }
    /* Metrics */
    .stMetric {
        background: #232a36;
        color: #f3f6fa;
        padding: 1rem;
        border-radius: 10px;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #232a36;
        color: #f3f6fa;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #42a5f5, #00bcd4);
        color: #fff;
    }
    /* Success/Info boxes */
    .success-box {
        background: #234d20;
        border: 1px solid #2ecc71;
        border-radius: 10px;
        padding: 1rem;
        color: #b6fcd5;
    }
    .info-box {
        background: #223a5e;
        border: 1px solid #42a5f5;
        border-radius: 10px;
        padding: 1rem;
        color: #b3e5fc;
    }
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #b0b8c1;
        border-top: 1px solid #232a36;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# ENUMS AND DATA CLASSES
# ============================================

class Powertrain(Enum):
    EV = "EV"
    PHEV = "PHEV"

class VehicleType(Enum):
    SEDAN = "sedan"
    SUV = "suv"
    HATCHBACK = "hatchback"
    TRUCK = "truck"
    CROSSOVER = "crossover"
    WAGON = "wagon"
    MINIVAN = "minivan"

class Region(Enum):
    USA_FEDERAL = "usa_federal"
    USA_CALIFORNIA = "usa_california"
    USA_COLORADO = "usa_colorado"
    USA_NEW_JERSEY = "usa_new_jersey"
    USA_NEW_YORK = "usa_new_york"
    USA_TEXAS = "usa_texas"
    CANADA_FEDERAL = "canada_federal"
    CANADA_QUEBEC = "canada_quebec"
    CANADA_BC = "canada_bc"
    CANADA_ONTARIO = "canada_ontario"
    UK = "uk"
    GERMANY = "germany"
    FRANCE = "france"
    NETHERLANDS = "netherlands"
    NORWAY = "norway"
    AUSTRALIA = "australia"
    PORTUGAL = "portugal"


@dataclass
class UserPreferences:
    daily_commute_km: float = 50
    annual_km: float = 20000
    long_trips_frequency: str = "rarely"
    typical_long_trip_km: float = 400
    home_charging_available: bool = True
    home_charging_type: str = "level2"
    work_charging_available: bool = False
    public_charging_reliance: str = "low"
    max_budget: float = 50000
    min_budget: float = 0
    consider_incentives: bool = True
    region: Region = Region.USA_FEDERAL
    ownership_years: int = 5
    expected_resale_percent: float = 50
    electricity_cost_kwh: float = 0.15
    gas_cost_liter: float = 1.50
    vehicle_types: List[VehicleType] = field(default_factory=lambda: [VehicleType.SEDAN, VehicleType.SUV])
    min_seats: int = 5
    min_cargo_liters: int = 300
    needs_awd: bool = False
    needs_towing: bool = False
    min_towing_kg: int = 0
    range_priority: int = 3
    charging_speed_priority: int = 3
    acceleration_priority: int = 2
    efficiency_priority: int = 3
    tech_features_priority: int = 3
    safety_priority: int = 4
    reliability_priority: int = 4
    cargo_priority: int = 3
    zero_emissions_priority: int = 3
    preferred_brands: List[str] = field(default_factory=list)
    excluded_brands: List[str] = field(default_factory=list)


@dataclass
class TCOResult:
    vehicle_name: str
    purchase_price: float
    incentives_total: float
    net_purchase_price: float
    annual_fuel_cost: float
    annual_maintenance_cost: float
    annual_insurance_cost: float
    annual_registration_cost: float
    total_fuel_cost: float
    total_maintenance_cost: float
    total_insurance_cost: float
    total_registration_cost: float
    depreciation: float
    total_cost_of_ownership: float
    cost_per_km: float
    cost_per_year: float
    savings_vs_avg_ice: float = 0


# ============================================
# VEHICLE DATABASE
# ============================================

@st.cache_data
def load_vehicle_database(use_sync: bool = False) -> Tuple[List[Dict], int, int]:
    """Load comprehensive vehicle database.

    If `use_sync` is True, attempts to merge in entries from
    `evdb_sync.json`.  Returned tuple is
    `(vehicles_list, added_count, skipped_count)`.
    """
    
    vehicles_data = [
        # ===== TESLA =====
        {"id": "tesla_model_3_sr", "name": "Tesla Model 3 Standard Range", "brand": "Tesla",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 40240,
         "range_km": 438, "battery_kwh": 60, "dc_charging_kw": 170, "zero_to_100_kmh": 6.1,
         "top_speed_kmh": 201, "horsepower": 271, "torque_nm": 420, "kwh_per_100km": 13.7,
         "cargo_liters": 561, "curb_weight_kg": 1752, "length_mm": 4694, "width_mm": 1849,
         "height_mm": 1443, "wheelbase_mm": 2875, "autopilot_available": True, "ota_updates": True,
         "heat_pump": True, "frunk_liters": 88, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 5,
         "v2l_capable": False, "v2h_capable": False, "ground_clearance_mm": 140},
        
        {"id": "tesla_model_3_lr", "name": "Tesla Model 3 Long Range AWD", "brand": "Tesla",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 47240,
         "range_km": 629, "battery_kwh": 82, "dc_charging_kw": 250, "zero_to_100_kmh": 4.4,
         "top_speed_kmh": 201, "horsepower": 366, "torque_nm": 493, "awd": True,
         "kwh_per_100km": 14.1, "cargo_liters": 561, "curb_weight_kg": 1830, "length_mm": 4694,
         "width_mm": 1849, "height_mm": 1443, "wheelbase_mm": 2875, "autopilot_available": True,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 88, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "towing_capacity_kg": 0, "safety_rating_ncap": 5,
         "v2l_capable": False, "v2h_capable": False, "ground_clearance_mm": 140},
        
        {"id": "tesla_model_3_perf", "name": "Tesla Model 3 Performance", "brand": "Tesla",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 52240,
         "range_km": 547, "battery_kwh": 82, "dc_charging_kw": 250, "zero_to_100_kmh": 3.1,
         "top_speed_kmh": 262, "horsepower": 510, "torque_nm": 660, "awd": True,
         "kwh_per_100km": 15.0, "cargo_liters": 561, "curb_weight_kg": 1836, "length_mm": 4694,
         "width_mm": 1849, "height_mm": 1443, "wheelbase_mm": 2875, "autopilot_available": True,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 88, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "towing_capacity_kg": 0, "safety_rating_ncap": 5,
         "v2l_capable": False, "v2h_capable": False, "ground_clearance_mm": 140},
        
        {"id": "tesla_model_y_lr", "name": "Tesla Model Y Long Range AWD", "brand": "Tesla",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 48490,
         "range_km": 533, "battery_kwh": 82, "dc_charging_kw": 250, "zero_to_100_kmh": 5.0,
         "top_speed_kmh": 217, "horsepower": 384, "torque_nm": 493, "awd": True,
         "kwh_per_100km": 15.4, "cargo_liters": 854, "curb_weight_kg": 1979, "length_mm": 4751,
         "width_mm": 1921, "height_mm": 1624, "wheelbase_mm": 2890, "ground_clearance_mm": 167,
         "autopilot_available": True, "ota_updates": True, "heat_pump": True, "frunk_liters": 117,
         "towing_capacity_kg": 1588, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "v2l_capable": False, "v2h_capable": False},
        
        {"id": "tesla_model_y_perf", "name": "Tesla Model Y Performance", "brand": "Tesla",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 52490,
         "range_km": 487, "battery_kwh": 82, "dc_charging_kw": 250, "zero_to_100_kmh": 3.7,
         "top_speed_kmh": 250, "horsepower": 510, "torque_nm": 660, "awd": True,
         "kwh_per_100km": 16.0, "cargo_liters": 854, "curb_weight_kg": 2003, "length_mm": 4751,
         "width_mm": 1921, "height_mm": 1624, "wheelbase_mm": 2890, "ground_clearance_mm": 167,
         "autopilot_available": True, "ota_updates": True, "heat_pump": True, "frunk_liters": 117,
         "towing_capacity_kg": 1588, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "v2l_capable": False, "v2h_capable": False},
        
        {"id": "tesla_cybertruck", "name": "Tesla Cybertruck AWD", "brand": "Tesla",
         "powertrain": "EV", "vehicle_type": "truck", "year": 2024, "base_price": 79990,
         "range_km": 547, "battery_kwh": 123, "dc_charging_kw": 250, "zero_to_100_kmh": 4.3,
         "top_speed_kmh": 180, "horsepower": 600, "torque_nm": 930, "awd": True,
         "kwh_per_100km": 22.5, "cargo_liters": 1897, "curb_weight_kg": 3104, "length_mm": 5682,
         "width_mm": 2200, "height_mm": 1790, "wheelbase_mm": 3807, "ground_clearance_mm": 432,
         "autopilot_available": True, "ota_updates": True, "heat_pump": True, "frunk_liters": 283,
         "v2l_capable": True, "v2h_capable": True, "towing_capacity_kg": 4990,
         "made_in_north_america": True, "battery_sourcing_compliant": True, "reliability_score": 3.0,
         "seats": 5, "safety_rating_ncap": 5},
        
        # ===== HYUNDAI =====
        {"id": "hyundai_ioniq_5_sr", "name": "Hyundai Ioniq 5 Standard Range", "brand": "Hyundai",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 41450,
         "range_km": 354, "battery_kwh": 58, "dc_charging_kw": 175, "zero_to_100_kmh": 8.5,
         "top_speed_kmh": 185, "horsepower": 168, "torque_nm": 350, "awd": False,
         "kwh_per_100km": 16.4, "cargo_liters": 527, "curb_weight_kg": 1800, "length_mm": 4635,
         "width_mm": 1890, "height_mm": 1605, "wheelbase_mm": 3000, "ground_clearance_mm": 160,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 57, "v2l_capable": True,
         "v2h_capable": False, "towing_capacity_kg": 0, "made_in_north_america": False,
         "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False},
        
        {"id": "hyundai_ioniq_5_lr", "name": "Hyundai Ioniq 5 Long Range AWD", "brand": "Hyundai",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 52600,
         "range_km": 488, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 5.1,
         "top_speed_kmh": 185, "horsepower": 320, "torque_nm": 605, "awd": True,
         "kwh_per_100km": 15.9, "cargo_liters": 527, "curb_weight_kg": 2100, "length_mm": 4635,
         "width_mm": 1890, "height_mm": 1605, "wheelbase_mm": 3000, "ground_clearance_mm": 160,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 57, "v2l_capable": True,
         "v2h_capable": False, "towing_capacity_kg": 1600, "made_in_north_america": False,
         "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False},
        
        {"id": "hyundai_ioniq_6_lr", "name": "Hyundai Ioniq 6 Long Range", "brand": "Hyundai",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 45500,
         "range_km": 614, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 7.4,
         "top_speed_kmh": 185, "horsepower": 225, "torque_nm": 350, "awd": False,
         "kwh_per_100km": 13.9, "cargo_liters": 401, "curb_weight_kg": 1885, "length_mm": 4855,
         "width_mm": 1880, "height_mm": 1495, "wheelbase_mm": 2950, "ground_clearance_mm": 140,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "made_in_north_america": False, "msrp_under_55k_sedan": True, "reliability_score": 4.0,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "frunk_liters": 0},
        
        {"id": "hyundai_ioniq_6_lr_awd", "name": "Hyundai Ioniq 6 Long Range AWD", "brand": "Hyundai",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 49500,
         "range_km": 581, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 5.1,
         "top_speed_kmh": 185, "horsepower": 320, "torque_nm": 605, "awd": True,
         "kwh_per_100km": 14.3, "cargo_liters": 401, "curb_weight_kg": 2010, "length_mm": 4855,
         "width_mm": 1880, "height_mm": 1495, "wheelbase_mm": 2950, "ground_clearance_mm": 140,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "made_in_north_america": False, "msrp_under_55k_sedan": True, "reliability_score": 4.0,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "frunk_liters": 0},
        
        {"id": "hyundai_kona_ev", "name": "Hyundai Kona Electric", "brand": "Hyundai",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 33550,
         "range_km": 418, "battery_kwh": 64.8, "dc_charging_kw": 102, "zero_to_100_kmh": 7.8,
         "top_speed_kmh": 167, "horsepower": 201, "torque_nm": 255, "awd": False,
         "kwh_per_100km": 15.5, "cargo_liters": 466, "curb_weight_kg": 1715, "length_mm": 4355,
         "width_mm": 1825, "height_mm": 1575, "wheelbase_mm": 2660, "ground_clearance_mm": 155,
         "heat_pump": True, "v2l_capable": True, "v2h_capable": False, "made_in_north_america": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.2, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "ota_updates": False, "frunk_liters": 0},
        
        # ===== KIA =====
                # ===== CHINESE EV/PHEV MODELS =====
                {"id": "byd_atto3", "name": "BYD Atto 3 (Yuan Plus)", "brand": "BYD", "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 38000, "range_km": 420, "battery_kwh": 60.5, "dc_charging_kw": 88, "zero_to_100_kmh": 7.3, "top_speed_kmh": 160, "horsepower": 204, "torque_nm": 310, "kwh_per_100km": 15.6, "cargo_liters": 440, "curb_weight_kg": 1750, "length_mm": 4455, "width_mm": 1875, "height_mm": 1615, "wheelbase_mm": 2720, "seats": 5, "awd": False, "towing_capacity_kg": 750, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
                {"id": "byd_han_ev", "name": "BYD Han EV", "brand": "BYD", "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 60000, "range_km": 521, "battery_kwh": 85.4, "dc_charging_kw": 120, "zero_to_100_kmh": 3.9, "top_speed_kmh": 185, "horsepower": 380, "torque_nm": 700, "kwh_per_100km": 16.2, "cargo_liters": 410, "curb_weight_kg": 2250, "length_mm": 4980, "width_mm": 1910, "height_mm": 1495, "wheelbase_mm": 2920, "seats": 5, "awd": True, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.2},
                {"id": "mg4_electric", "name": "MG4 Electric", "brand": "MG", "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 32000, "range_km": 450, "battery_kwh": 64, "dc_charging_kw": 135, "zero_to_100_kmh": 7.7, "top_speed_kmh": 160, "horsepower": 204, "torque_nm": 250, "kwh_per_100km": 16.0, "cargo_liters": 363, "curb_weight_kg": 1685, "length_mm": 4287, "width_mm": 1836, "height_mm": 1504, "wheelbase_mm": 2705, "seats": 5, "awd": False, "towing_capacity_kg": 500, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
                {"id": "nio_et7", "name": "NIO ET7", "brand": "NIO", "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 70000, "range_km": 580, "battery_kwh": 100, "dc_charging_kw": 180, "zero_to_100_kmh": 3.8, "top_speed_kmh": 200, "horsepower": 653, "torque_nm": 850, "kwh_per_100km": 17.5, "cargo_liters": 410, "curb_weight_kg": 2150, "length_mm": 5098, "width_mm": 1987, "height_mm": 1505, "wheelbase_mm": 3060, "seats": 5, "awd": True, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.3},
                {"id": "xpeng_p7", "name": "XPeng P7", "brand": "XPeng", "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 48000, "range_km": 586, "battery_kwh": 80, "dc_charging_kw": 120, "zero_to_100_kmh": 6.7, "top_speed_kmh": 170, "horsepower": 267, "torque_nm": 390, "kwh_per_100km": 15.8, "cargo_liters": 440, "curb_weight_kg": 1836, "length_mm": 4880, "width_mm": 1896, "height_mm": 1450, "wheelbase_mm": 2998, "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.1},
                {"id": "ora_funky_cat", "name": "Ora Funky Cat", "brand": "Ora", "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 31000, "range_km": 310, "battery_kwh": 48, "dc_charging_kw": 80, "zero_to_100_kmh": 8.3, "top_speed_kmh": 160, "horsepower": 171, "torque_nm": 250, "kwh_per_100km": 16.6, "cargo_liters": 228, "curb_weight_kg": 1540, "length_mm": 4235, "width_mm": 1825, "height_mm": 1596, "wheelbase_mm": 2650, "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
            # ===== EUROPEAN EV/PHEV MODELS =====
            {"id": "vw_id3", "name": "Volkswagen ID.3", "brand": "Volkswagen", "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 39000, "range_km": 426, "battery_kwh": 58, "dc_charging_kw": 120, "zero_to_100_kmh": 7.3, "top_speed_kmh": 160, "horsepower": 204, "torque_nm": 310, "kwh_per_100km": 15.5, "cargo_liters": 385, "curb_weight_kg": 1750, "length_mm": 4261, "width_mm": 1809, "height_mm": 1568, "wheelbase_mm": 2770, "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
            {"id": "vw_id4", "name": "Volkswagen ID.4", "brand": "Volkswagen", "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 47000, "range_km": 522, "battery_kwh": 77, "dc_charging_kw": 135, "zero_to_100_kmh": 8.5, "top_speed_kmh": 160, "horsepower": 204, "torque_nm": 310, "kwh_per_100km": 16.2, "cargo_liters": 543, "curb_weight_kg": 2124, "length_mm": 4584, "width_mm": 1852, "height_mm": 1631, "wheelbase_mm": 2771, "seats": 5, "awd": False, "towing_capacity_kg": 1000, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
            {"id": "renault_zoe", "name": "Renault Zoe", "brand": "Renault", "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 33000, "range_km": 395, "battery_kwh": 52, "dc_charging_kw": 50, "zero_to_100_kmh": 9.5, "top_speed_kmh": 140, "horsepower": 135, "torque_nm": 245, "kwh_per_100km": 17.2, "cargo_liters": 338, "curb_weight_kg": 1502, "length_mm": 4087, "width_mm": 1787, "height_mm": 1562, "wheelbase_mm": 2588, "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
            {"id": "peugeot_e208", "name": "Peugeot e-208", "brand": "Peugeot", "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 34000, "range_km": 362, "battery_kwh": 50, "dc_charging_kw": 100, "zero_to_100_kmh": 8.1, "top_speed_kmh": 150, "horsepower": 136, "torque_nm": 260, "kwh_per_100km": 15.5, "cargo_liters": 311, "curb_weight_kg": 1455, "length_mm": 4055, "width_mm": 1745, "height_mm": 1430, "wheelbase_mm": 2540, "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 4, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
            {"id": "bmw_i4", "name": "BMW i4 eDrive40", "brand": "BMW", "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 59000, "range_km": 590, "battery_kwh": 83.9, "dc_charging_kw": 205, "zero_to_100_kmh": 5.7, "top_speed_kmh": 190, "horsepower": 340, "torque_nm": 430, "kwh_per_100km": 16.1, "cargo_liters": 470, "curb_weight_kg": 2125, "length_mm": 4783, "width_mm": 1852, "height_mm": 1448, "wheelbase_mm": 2856, "seats": 5, "awd": False, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.5},
            {"id": "mercedes_eqb", "name": "Mercedes-Benz EQB 300 4MATIC", "brand": "Mercedes-Benz", "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 55000, "range_km": 419, "battery_kwh": 66.5, "dc_charging_kw": 100, "zero_to_100_kmh": 8.0, "top_speed_kmh": 160, "horsepower": 228, "torque_nm": 390, "kwh_per_100km": 18.1, "cargo_liters": 495, "curb_weight_kg": 2150, "length_mm": 4684, "width_mm": 1834, "height_mm": 1667, "wheelbase_mm": 2829, "seats": 7, "awd": True, "towing_capacity_kg": 1800, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.0},
            {"id": "volvo_xc40_recharge", "name": "Volvo XC40 Recharge", "brand": "Volvo", "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 53000, "range_km": 418, "battery_kwh": 78, "dc_charging_kw": 150, "zero_to_100_kmh": 4.9, "top_speed_kmh": 180, "horsepower": 408, "torque_nm": 660, "kwh_per_100km": 20.7, "cargo_liters": 452, "curb_weight_kg": 2158, "length_mm": 4440, "width_mm": 1863, "height_mm": 1651, "wheelbase_mm": 2702, "seats": 5, "awd": True, "towing_capacity_kg": 1800, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.2},
            {"id": "polestar_2", "name": "Polestar 2 Long Range", "brand": "Polestar", "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 51000, "range_km": 551, "battery_kwh": 82, "dc_charging_kw": 205, "zero_to_100_kmh": 7.4, "top_speed_kmh": 160, "horsepower": 231, "torque_nm": 330, "kwh_per_100km": 16.8, "cargo_liters": 405, "curb_weight_kg": 1994, "length_mm": 4606, "width_mm": 1859, "height_mm": 1479, "wheelbase_mm": 2735, "seats": 5, "awd": False, "towing_capacity_kg": 1500, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "reliability_score": 4.3},
        {"id": "kia_ev6_sr", "name": "Kia EV6 Standard Range", "brand": "Kia",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 42600,
         "range_km": 370, "battery_kwh": 58, "dc_charging_kw": 180, "zero_to_100_kmh": 8.5,
         "top_speed_kmh": 185, "horsepower": 167, "torque_nm": 350, "awd": False,
         "kwh_per_100km": 15.7, "cargo_liters": 490, "curb_weight_kg": 1820, "length_mm": 4680,
         "width_mm": 1880, "height_mm": 1550, "wheelbase_mm": 2900, "ground_clearance_mm": 160,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 52, "v2l_capable": True,
         "v2h_capable": False, "towing_capacity_kg": 0, "made_in_north_america": False,
         "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False},
        
        {"id": "kia_ev6_lr", "name": "Kia EV6 Long Range AWD", "brand": "Kia",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 54900,
         "range_km": 499, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 5.2,
         "top_speed_kmh": 188, "horsepower": 320, "torque_nm": 605, "awd": True,
         "kwh_per_100km": 15.5, "cargo_liters": 490, "curb_weight_kg": 2090, "length_mm": 4680,
         "width_mm": 1880, "height_mm": 1550, "wheelbase_mm": 2900, "ground_clearance_mm": 160,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 52, "v2l_capable": True,
         "v2h_capable": False, "towing_capacity_kg": 1600, "made_in_north_america": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False},
        
        {"id": "kia_ev6_gt", "name": "Kia EV6 GT", "brand": "Kia",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 61600,
         "range_km": 426, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 3.5,
         "top_speed_kmh": 260, "horsepower": 576, "torque_nm": 740, "awd": True,
         "kwh_per_100km": 18.2, "cargo_liters": 490, "curb_weight_kg": 2205, "length_mm": 4680,
         "width_mm": 1880, "height_mm": 1550, "wheelbase_mm": 2900, "ground_clearance_mm": 160,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 52, "v2l_capable": True,
         "v2h_capable": False, "towing_capacity_kg": 1600, "made_in_north_america": False,
         "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False},
        
        {"id": "kia_ev9_lr", "name": "Kia EV9 Long Range AWD", "brand": "Kia",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 56395,
         "range_km": 451, "battery_kwh": 99.8, "dc_charging_kw": 233, "zero_to_100_kmh": 6.0,
         "top_speed_kmh": 200, "horsepower": 379, "torque_nm": 700, "awd": True,
         "kwh_per_100km": 22.1, "cargo_liters": 333, "curb_weight_kg": 2585, "length_mm": 5010,
         "width_mm": 1980, "height_mm": 1755, "wheelbase_mm": 3100, "ground_clearance_mm": 195,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": True,
         "towing_capacity_kg": 2500, "made_in_north_america": False, "msrp_under_80k_suv": True,
         "reliability_score": 4.0, "seats": 7, "safety_rating_ncap": 5, "autopilot_available": False,
         "frunk_liters": 0},
        
        {"id": "kia_niro_ev", "name": "Kia Niro EV", "brand": "Kia",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 39600,
         "range_km": 407, "battery_kwh": 64.8, "dc_charging_kw": 80, "zero_to_100_kmh": 7.8,
         "top_speed_kmh": 167, "horsepower": 201, "torque_nm": 255, "awd": False,
         "kwh_per_100km": 15.9, "cargo_liters": 475, "curb_weight_kg": 1737, "length_mm": 4420,
         "width_mm": 1825, "height_mm": 1570, "wheelbase_mm": 2720, "ground_clearance_mm": 160,
         "heat_pump": True, "v2l_capable": True, "v2h_capable": False, "made_in_north_america": False,
         "reliability_score": 4.2, "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "ota_updates": False, "frunk_liters": 0},
        
        # ===== FORD =====
        {"id": "ford_mache_select", "name": "Ford Mustang Mach-E Select", "brand": "Ford",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 42995,
         "range_km": 402, "battery_kwh": 72.6, "dc_charging_kw": 115, "zero_to_100_kmh": 6.3,
         "top_speed_kmh": 180, "horsepower": 266, "torque_nm": 430, "awd": False,
         "kwh_per_100km": 18.0, "cargo_liters": 822, "curb_weight_kg": 1969, "length_mm": 4724,
         "width_mm": 1881, "height_mm": 1597, "wheelbase_mm": 2984, "ground_clearance_mm": 147,
         "ota_updates": True, "frunk_liters": 136, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False},
        
        {"id": "ford_mache_premium", "name": "Ford Mustang Mach-E Premium AWD", "brand": "Ford",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 52995,
         "range_km": 502, "battery_kwh": 91, "dc_charging_kw": 150, "zero_to_100_kmh": 4.8,
         "top_speed_kmh": 180, "horsepower": 346, "torque_nm": 580, "awd": True,
         "kwh_per_100km": 18.1, "cargo_liters": 822, "curb_weight_kg": 2185, "length_mm": 4724,
         "width_mm": 1881, "height_mm": 1597, "wheelbase_mm": 2984, "ground_clearance_mm": 147,
         "ota_updates": True, "frunk_liters": 136, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_80k_suv": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False},
        
        {"id": "ford_mache_gt", "name": "Ford Mustang Mach-E GT", "brand": "Ford",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 59995,
         "range_km": 418, "battery_kwh": 91, "dc_charging_kw": 150, "zero_to_100_kmh": 3.8,
         "top_speed_kmh": 200, "horsepower": 480, "torque_nm": 860, "awd": True,
         "kwh_per_100km": 21.8, "cargo_liters": 822, "curb_weight_kg": 2273, "length_mm": 4724,
         "width_mm": 1881, "height_mm": 1597, "wheelbase_mm": 2984, "ground_clearance_mm": 147,
         "ota_updates": True, "frunk_liters": 136, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_80k_suv": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False},
        
        {"id": "ford_f150_lightning_sr", "name": "Ford F-150 Lightning Standard", "brand": "Ford",
         "powertrain": "EV", "vehicle_type": "truck", "year": 2024, "base_price": 49995,
         "range_km": 386, "battery_kwh": 98, "dc_charging_kw": 150, "zero_to_100_kmh": 5.0,
         "top_speed_kmh": 180, "horsepower": 452, "torque_nm": 775, "awd": True,
         "kwh_per_100km": 25.4, "cargo_liters": 1495, "curb_weight_kg": 2948, "length_mm": 5915,
         "width_mm": 2032, "height_mm": 2004, "wheelbase_mm": 3696, "ground_clearance_mm": 226,
         "ota_updates": True, "frunk_liters": 400, "v2l_capable": True, "v2h_capable": True,
         "towing_capacity_kg": 3402, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False, "heat_pump": False},
        
        {"id": "ford_f150_lightning_er", "name": "Ford F-150 Lightning Extended Range", "brand": "Ford",
         "powertrain": "EV", "vehicle_type": "truck", "year": 2024, "base_price": 59995,
         "range_km": 515, "battery_kwh": 131, "dc_charging_kw": 150, "zero_to_100_kmh": 4.5,
         "top_speed_kmh": 180, "horsepower": 580, "torque_nm": 1050, "awd": True,
         "kwh_per_100km": 25.4, "cargo_liters": 1495, "curb_weight_kg": 3130, "length_mm": 5915,
         "width_mm": 2032, "height_mm": 2004, "wheelbase_mm": 3696, "ground_clearance_mm": 226,
         "ota_updates": True, "frunk_liters": 400, "v2l_capable": True, "v2h_capable": True,
         "towing_capacity_kg": 4536, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False, "heat_pump": False},
        
        # ===== CHEVROLET =====
        {"id": "chevy_bolt_ev", "name": "Chevrolet Bolt EV", "brand": "Chevrolet",
         "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 27495,
         "range_km": 423, "battery_kwh": 65, "dc_charging_kw": 55, "zero_to_100_kmh": 7.0,
         "top_speed_kmh": 150, "horsepower": 200, "torque_nm": 360, "awd": False,
         "kwh_per_100km": 15.4, "cargo_liters": 462, "curb_weight_kg": 1616, "length_mm": 4148,
         "width_mm": 1765, "height_mm": 1611, "wheelbase_mm": 2600, "ground_clearance_mm": 145,
         "made_in_north_america": True, "battery_sourcing_compliant": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "ota_updates": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "chevy_bolt_euv", "name": "Chevrolet Bolt EUV", "brand": "Chevrolet",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 28795,
         "range_km": 402, "battery_kwh": 65, "dc_charging_kw": 55, "zero_to_100_kmh": 7.0,
         "top_speed_kmh": 150, "horsepower": 200, "torque_nm": 360, "awd": False,
         "kwh_per_100km": 16.2, "cargo_liters": 462, "curb_weight_kg": 1669, "length_mm": 4306,
         "width_mm": 1770, "height_mm": 1616, "wheelbase_mm": 2675, "ground_clearance_mm": 145,
         "autopilot_available": True, "made_in_north_america": True, "battery_sourcing_compliant": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "ota_updates": False, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "chevy_equinox_ev", "name": "Chevrolet Equinox EV", "brand": "Chevrolet",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 34995,
         "range_km": 515, "battery_kwh": 85, "dc_charging_kw": 150, "zero_to_100_kmh": 7.0,
         "top_speed_kmh": 180, "horsepower": 213, "torque_nm": 320, "awd": False,
         "kwh_per_100km": 16.5, "cargo_liters": 863, "curb_weight_kg": 2086, "length_mm": 4841,
         "width_mm": 1904, "height_mm": 1680, "wheelbase_mm": 2954, "ground_clearance_mm": 213,
         "autopilot_available": True, "ota_updates": True, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.8,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "chevy_blazer_ev", "name": "Chevrolet Blazer EV", "brand": "Chevrolet",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 45995,
         "range_km": 449, "battery_kwh": 85, "dc_charging_kw": 190, "zero_to_100_kmh": 6.0,
         "top_speed_kmh": 190, "horsepower": 288, "torque_nm": 333, "awd": False,
         "kwh_per_100km": 18.9, "cargo_liters": 863, "curb_weight_kg": 2404, "length_mm": 4883,
         "width_mm": 1953, "height_mm": 1681, "wheelbase_mm": 2954, "ground_clearance_mm": 175,
         "autopilot_available": True, "ota_updates": True, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "chevy_silverado_ev", "name": "Chevrolet Silverado EV", "brand": "Chevrolet",
         "powertrain": "EV", "vehicle_type": "truck", "year": 2024, "base_price": 52000,
         "range_km": 644, "battery_kwh": 200, "dc_charging_kw": 350, "zero_to_100_kmh": 4.5,
         "top_speed_kmh": 180, "horsepower": 510, "torque_nm": 834, "awd": True,
         "kwh_per_100km": 31.1, "cargo_liters": 1800, "curb_weight_kg": 4103, "length_mm": 5920,
         "width_mm": 2072, "height_mm": 1930, "wheelbase_mm": 3683, "ground_clearance_mm": 273,
         "autopilot_available": True, "ota_updates": True, "v2l_capable": True, "v2h_capable": True,
         "towing_capacity_kg": 4536, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "heat_pump": False, "frunk_liters": 0},
        
        # ===== RIVIAN =====
        {"id": "rivian_r1t", "name": "Rivian R1T Dual Motor", "brand": "Rivian",
         "powertrain": "EV", "vehicle_type": "truck", "year": 2024, "base_price": 69900,
         "range_km": 531, "battery_kwh": 135, "dc_charging_kw": 220, "zero_to_100_kmh": 4.0,
         "top_speed_kmh": 175, "horsepower": 600, "torque_nm": 1124, "awd": True,
         "kwh_per_100km": 25.4, "cargo_liters": 1132, "curb_weight_kg": 3075, "length_mm": 5514,
         "width_mm": 2015, "height_mm": 1815, "wheelbase_mm": 3450, "ground_clearance_mm": 368,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "towing_capacity_kg": 4990, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False, "frunk_liters": 0},
        
        {"id": "rivian_r1s", "name": "Rivian R1S Dual Motor", "brand": "Rivian",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 75900,
         "range_km": 515, "battery_kwh": 135, "dc_charging_kw": 220, "zero_to_100_kmh": 4.5,
         "top_speed_kmh": 175, "horsepower": 600, "torque_nm": 1124, "awd": True,
         "kwh_per_100km": 26.2, "cargo_liters": 498, "curb_weight_kg": 3175, "length_mm": 5050,
         "width_mm": 2015, "height_mm": 1815, "wheelbase_mm": 3075, "ground_clearance_mm": 368,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "towing_capacity_kg": 3500, "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_80k_suv": True, "reliability_score": 3.5, "seats": 7, "safety_rating_ncap": 5,
         "autopilot_available": False, "frunk_liters": 0},
        
        # ===== BMW =====
        {"id": "bmw_i4_edrive35", "name": "BMW i4 eDrive35", "brand": "BMW",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 52200,
         "range_km": 435, "battery_kwh": 66, "dc_charging_kw": 180, "zero_to_100_kmh": 5.8,
         "top_speed_kmh": 190, "horsepower": 281, "torque_nm": 400, "awd": False,
         "kwh_per_100km": 15.2, "cargo_liters": 470, "curb_weight_kg": 2050, "length_mm": 4783,
         "width_mm": 1852, "height_mm": 1448, "wheelbase_mm": 2856, "ground_clearance_mm": 130,
         "ota_updates": True, "made_in_north_america": False, "msrp_under_55k_sedan": True,
         "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "heat_pump": False, "v2l_capable": False, "v2h_capable": False,
         "frunk_liters": 0},
        
        {"id": "bmw_i4_m50", "name": "BMW i4 M50", "brand": "BMW",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 67300,
         "range_km": 435, "battery_kwh": 83.9, "dc_charging_kw": 200, "zero_to_100_kmh": 3.9,
         "top_speed_kmh": 225, "horsepower": 536, "torque_nm": 795, "awd": True,
         "kwh_per_100km": 19.3, "cargo_liters": 470, "curb_weight_kg": 2290, "length_mm": 4783,
         "width_mm": 1852, "height_mm": 1448, "wheelbase_mm": 2856, "ground_clearance_mm": 130,
         "ota_updates": True, "made_in_north_america": False, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "bmw_ix_xdrive50", "name": "BMW iX xDrive50", "brand": "BMW",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 87100,
         "range_km": 523, "battery_kwh": 111.5, "dc_charging_kw": 195, "zero_to_100_kmh": 4.6,
         "top_speed_kmh": 200, "horsepower": 516, "torque_nm": 765, "awd": True,
         "kwh_per_100km": 21.3, "cargo_liters": 500, "curb_weight_kg": 2510, "length_mm": 4953,
         "width_mm": 1967, "height_mm": 1696, "wheelbase_mm": 3000, "ground_clearance_mm": 177,
         "ota_updates": True, "towing_capacity_kg": 2500, "made_in_north_america": False,
         "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False,
         "heat_pump": True, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # ===== MERCEDES =====
        {"id": "mercedes_eqe_350", "name": "Mercedes-Benz EQE 350+", "brand": "Mercedes-Benz",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 74900,
         "range_km": 550, "battery_kwh": 90.6, "dc_charging_kw": 170, "zero_to_100_kmh": 6.4,
         "top_speed_kmh": 210, "horsepower": 288, "torque_nm": 530, "awd": False,
         "kwh_per_100km": 16.5, "cargo_liters": 430, "curb_weight_kg": 2355, "length_mm": 4946,
         "width_mm": 1906, "height_mm": 1512, "wheelbase_mm": 3120, "ground_clearance_mm": 130,
         "ota_updates": True, "heat_pump": True, "made_in_north_america": False,
         "reliability_score": 3.8, "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "mercedes_eqs_450", "name": "Mercedes-Benz EQS 450+", "brand": "Mercedes-Benz",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 104400,
         "range_km": 560, "battery_kwh": 108.4, "dc_charging_kw": 200, "zero_to_100_kmh": 6.2,
         "top_speed_kmh": 210, "horsepower": 329, "torque_nm": 565, "awd": False,
         "kwh_per_100km": 19.4, "cargo_liters": 610, "curb_weight_kg": 2480, "length_mm": 5216,
         "width_mm": 1926, "height_mm": 1512, "wheelbase_mm": 3210, "ground_clearance_mm": 130,
         "ota_updates": True, "heat_pump": True, "made_in_north_america": False,
         "reliability_score": 3.8, "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # ===== VOLKSWAGEN =====
        {"id": "vw_id4_standard", "name": "Volkswagen ID.4 Standard", "brand": "Volkswagen",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 38995,
         "range_km": 338, "battery_kwh": 62, "dc_charging_kw": 135, "zero_to_100_kmh": 8.5,
         "top_speed_kmh": 160, "horsepower": 201, "torque_nm": 310, "awd": False,
         "kwh_per_100km": 18.3, "cargo_liters": 543, "curb_weight_kg": 2058, "length_mm": 4584,
         "width_mm": 1852, "height_mm": 1640, "wheelbase_mm": 2766, "ground_clearance_mm": 175,
         "ota_updates": True, "heat_pump": True, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "vw_id4_pro_awd", "name": "Volkswagen ID.4 Pro S Plus AWD", "brand": "Volkswagen",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 53995,
         "range_km": 418, "battery_kwh": 82, "dc_charging_kw": 135, "zero_to_100_kmh": 5.4,
         "top_speed_kmh": 180, "horsepower": 295, "torque_nm": 460, "awd": True,
         "kwh_per_100km": 19.6, "cargo_liters": 543, "curb_weight_kg": 2224, "length_mm": 4584,
         "width_mm": 1852, "height_mm": 1640, "wheelbase_mm": 2766, "ground_clearance_mm": 175,
         "ota_updates": True, "heat_pump": True, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "vw_id_buzz", "name": "Volkswagen ID. Buzz", "brand": "Volkswagen",
         "powertrain": "EV", "vehicle_type": "minivan", "year": 2024, "base_price": 59995,
         "range_km": 373, "battery_kwh": 91, "dc_charging_kw": 200, "zero_to_100_kmh": 7.0,
         "top_speed_kmh": 160, "horsepower": 282, "torque_nm": 413, "awd": False,
         "kwh_per_100km": 24.4, "cargo_liters": 306, "curb_weight_kg": 2502, "length_mm": 4712,
         "width_mm": 1985, "height_mm": 1927, "wheelbase_mm": 2988, "ground_clearance_mm": 175,
         "ota_updates": True, "heat_pump": True, "made_in_north_america": False,
         "reliability_score": 3.5, "seats": 7, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # ===== VOLVO =====
        {"id": "volvo_ex30", "name": "Volvo EX30 Single Motor", "brand": "Volvo",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 34950,
         "range_km": 440, "battery_kwh": 69, "dc_charging_kw": 153, "zero_to_100_kmh": 5.3,
         "top_speed_kmh": 180, "horsepower": 268, "torque_nm": 343, "awd": False,
         "kwh_per_100km": 15.7, "cargo_liters": 318, "curb_weight_kg": 1790, "length_mm": 4233,
         "width_mm": 1836, "height_mm": 1549, "wheelbase_mm": 2650, "ground_clearance_mm": 175,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "made_in_north_america": False, "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "frunk_liters": 0},
        
        {"id": "volvo_xc40_recharge", "name": "Volvo XC40 Recharge Twin", "brand": "Volvo",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 53550,
         "range_km": 418, "battery_kwh": 78, "dc_charging_kw": 150, "zero_to_100_kmh": 4.7,
         "top_speed_kmh": 180, "horsepower": 402, "torque_nm": 660, "awd": True,
         "kwh_per_100km": 18.7, "cargo_liters": 419, "curb_weight_kg": 2188, "length_mm": 4425,
         "width_mm": 1863, "height_mm": 1647, "wheelbase_mm": 2702, "ground_clearance_mm": 175,
         "ota_updates": True, "heat_pump": True, "towing_capacity_kg": 1500,
         "made_in_north_america": False, "msrp_under_55k_sedan": True, "reliability_score": 4.0,
         "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "volvo_c40_recharge", "name": "Volvo C40 Recharge Twin", "brand": "Volvo",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 54695,
         "range_km": 426, "battery_kwh": 78, "dc_charging_kw": 150, "zero_to_100_kmh": 4.7,
         "top_speed_kmh": 180, "horsepower": 402, "torque_nm": 660, "awd": True,
         "kwh_per_100km": 18.3, "cargo_liters": 413, "curb_weight_kg": 2185, "length_mm": 4440,
         "width_mm": 1873, "height_mm": 1596, "wheelbase_mm": 2702, "ground_clearance_mm": 175,
         "ota_updates": True, "heat_pump": True, "towing_capacity_kg": 1500,
         "made_in_north_america": False, "msrp_under_55k_sedan": True, "reliability_score": 4.0,
         "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # ===== POLESTAR =====
        {"id": "polestar_2_sr", "name": "Polestar 2 Standard Range", "brand": "Polestar",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 44900,
         "range_km": 418, "battery_kwh": 69, "dc_charging_kw": 135, "zero_to_100_kmh": 6.2,
         "top_speed_kmh": 205, "horsepower": 299, "torque_nm": 490, "awd": False,
         "kwh_per_100km": 16.5, "cargo_liters": 405, "curb_weight_kg": 1995, "length_mm": 4606,
         "width_mm": 1859, "height_mm": 1479, "wheelbase_mm": 2735, "ground_clearance_mm": 150,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 41, "made_in_north_america": False,
         "msrp_under_55k_sedan": True, "reliability_score": 3.8, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "v2l_capable": False, "v2h_capable": False},
        
        {"id": "polestar_2_lr_dual", "name": "Polestar 2 Long Range Dual Motor", "brand": "Polestar",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 51900,
         "range_km": 515, "battery_kwh": 82, "dc_charging_kw": 205, "zero_to_100_kmh": 4.5,
         "top_speed_kmh": 205, "horsepower": 421, "torque_nm": 740, "awd": True,
         "kwh_per_100km": 15.9, "cargo_liters": 405, "curb_weight_kg": 2123, "length_mm": 4606,
         "width_mm": 1859, "height_mm": 1479, "wheelbase_mm": 2735, "ground_clearance_mm": 150,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 41, "made_in_north_america": False,
         "msrp_under_55k_sedan": True, "reliability_score": 3.8, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "v2l_capable": False, "v2h_capable": False},
        
        # ===== LUCID =====
        {"id": "lucid_air_pure", "name": "Lucid Air Pure", "brand": "Lucid",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 77900,
         "range_km": 660, "battery_kwh": 88, "dc_charging_kw": 250, "zero_to_100_kmh": 4.5,
         "top_speed_kmh": 225, "horsepower": 430, "torque_nm": 550, "awd": False,
         "kwh_per_100km": 13.3, "cargo_liters": 456, "curb_weight_kg": 2041, "length_mm": 4975,
         "width_mm": 1939, "height_mm": 1410, "wheelbase_mm": 2960, "ground_clearance_mm": 130,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 280, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "reliability_score": 3.5, "seats": 5,
         "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": True,
         "v2l_capable": False, "v2h_capable": False},
        
        {"id": "lucid_air_touring", "name": "Lucid Air Touring", "brand": "Lucid",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 107900,
         "range_km": 685, "battery_kwh": 112, "dc_charging_kw": 300, "zero_to_100_kmh": 3.4,
         "top_speed_kmh": 270, "horsepower": 620, "torque_nm": 885, "awd": True,
         "kwh_per_100km": 16.4, "cargo_liters": 456, "curb_weight_kg": 2270, "length_mm": 4975,
         "width_mm": 1939, "height_mm": 1410, "wheelbase_mm": 2960, "ground_clearance_mm": 130,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 280, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "reliability_score": 3.5, "seats": 5,
         "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": True,
         "v2l_capable": False, "v2h_capable": False},
        
        # ===== PORSCHE =====
        {"id": "porsche_taycan", "name": "Porsche Taycan", "brand": "Porsche",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 92250,
         "range_km": 407, "battery_kwh": 79.2, "dc_charging_kw": 270, "zero_to_100_kmh": 4.8,
         "top_speed_kmh": 230, "horsepower": 402, "torque_nm": 345, "awd": False,
         "kwh_per_100km": 19.5, "cargo_liters": 407, "curb_weight_kg": 2130, "length_mm": 4963,
         "width_mm": 1966, "height_mm": 1381, "wheelbase_mm": 2900, "ground_clearance_mm": 130,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 84, "made_in_north_america": False,
         "reliability_score": 3.5, "seats": 4, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "v2l_capable": False, "v2h_capable": False},
        
        {"id": "porsche_taycan_4s", "name": "Porsche Taycan 4S", "brand": "Porsche",
         "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 106950,
         "range_km": 454, "battery_kwh": 93.4, "dc_charging_kw": 270, "zero_to_100_kmh": 4.0,
         "top_speed_kmh": 250, "horsepower": 537, "torque_nm": 640, "awd": True,
         "kwh_per_100km": 20.6, "cargo_liters": 407, "curb_weight_kg": 2220, "length_mm": 4963,
         "width_mm": 1966, "height_mm": 1381, "wheelbase_mm": 2900, "ground_clearance_mm": 130,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 84, "made_in_north_america": False,
         "reliability_score": 3.5, "seats": 4, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "v2l_capable": False, "v2h_capable": False},
        
        {"id": "porsche_macan_ev", "name": "Porsche Macan Electric", "brand": "Porsche",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 78800,
         "range_km": 513, "battery_kwh": 100, "dc_charging_kw": 270, "zero_to_100_kmh": 5.2,
         "top_speed_kmh": 220, "horsepower": 402, "torque_nm": 650, "awd": True,
         "kwh_per_100km": 19.5, "cargo_liters": 540, "curb_weight_kg": 2295, "length_mm": 4784,
         "width_mm": 1938, "height_mm": 1622, "wheelbase_mm": 2893, "ground_clearance_mm": 185,
         "ota_updates": True, "heat_pump": True, "frunk_liters": 84, "towing_capacity_kg": 2000,
         "made_in_north_america": False, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False, "v2l_capable": False, "v2h_capable": False},
        
        # ===== GENESIS =====
            {"id": "porsche_taycan_turbo_s", "name": "Porsche Taycan Turbo S", "brand": "Porsche", "powertrain": "EV", "vehicle_type": "sedan", "year": 2024, "base_price": 190000, "range_km": 450, "battery_kwh": 93.4, "dc_charging_kw": 270, "zero_to_100_kmh": 2.8, "top_speed_kmh": 260, "horsepower": 761, "torque_nm": 1050, "kwh_per_100km": 21.0, "cargo_liters": 366, "curb_weight_kg": 2295, "length_mm": 4963, "width_mm": 1966, "height_mm": 1378, "wheelbase_mm": 2900, "autopilot_available": False, "ota_updates": True, "heat_pump": True, "frunk_liters": 84, "reliability_score": 4.0, "seats": 4, "awd": True, "towing_capacity_kg": 0, "safety_rating_ncap": 5, "v2l_capable": False, "v2h_capable": False, "ground_clearance_mm": 128},
        {"id": "genesis_gv60", "name": "Genesis GV60 Advanced", "brand": "Genesis",
         "powertrain": "EV", "vehicle_type": "crossover", "year": 2024, "base_price": 52000,
         "range_km": 399, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 5.6,
         "top_speed_kmh": 185, "horsepower": 314, "torque_nm": 605, "awd": True,
         "kwh_per_100km": 19.4, "cargo_liters": 432, "curb_weight_kg": 2105, "length_mm": 4515,
         "width_mm": 1890, "height_mm": 1580, "wheelbase_mm": 2900, "ground_clearance_mm": 160,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "made_in_north_america": False, "msrp_under_55k_sedan": True, "reliability_score": 4.0,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "frunk_liters": 0},
        
        {"id": "genesis_electrified_gv70", "name": "Genesis Electrified GV70", "brand": "Genesis",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 66450,
         "range_km": 383, "battery_kwh": 77.4, "dc_charging_kw": 233, "zero_to_100_kmh": 4.2,
         "top_speed_kmh": 235, "horsepower": 429, "torque_nm": 700, "awd": True,
         "kwh_per_100km": 20.2, "cargo_liters": 503, "curb_weight_kg": 2290, "length_mm": 4715,
         "width_mm": 1910, "height_mm": 1630, "wheelbase_mm": 2875, "ground_clearance_mm": 185,
         "ota_updates": True, "heat_pump": True, "v2l_capable": True, "v2h_capable": False,
         "towing_capacity_kg": 1588, "made_in_north_america": False, "reliability_score": 4.0,
         "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False, "frunk_liters": 0},
        
        # ===== NISSAN =====
        {"id": "nissan_leaf_s", "name": "Nissan Leaf S", "brand": "Nissan",
         "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 28140,
         "range_km": 240, "battery_kwh": 40, "dc_charging_kw": 50, "zero_to_100_kmh": 7.9,
         "top_speed_kmh": 144, "horsepower": 147, "torque_nm": 320, "awd": False,
         "kwh_per_100km": 16.7, "cargo_liters": 435, "curb_weight_kg": 1520, "length_mm": 4490,
         "width_mm": 1788, "height_mm": 1540, "wheelbase_mm": 2700, "ground_clearance_mm": 150,
         "made_in_north_america": True, "battery_sourcing_compliant": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.2, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "ota_updates": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "nissan_leaf_sv_plus", "name": "Nissan Leaf SV Plus", "brand": "Nissan",
         "powertrain": "EV", "vehicle_type": "hatchback", "year": 2024, "base_price": 36190,
         "range_km": 342, "battery_kwh": 62, "dc_charging_kw": 100, "zero_to_100_kmh": 6.9,
         "top_speed_kmh": 157, "horsepower": 214, "torque_nm": 340, "awd": False,
         "kwh_per_100km": 18.1, "cargo_liters": 435, "curb_weight_kg": 1748, "length_mm": 4490,
         "width_mm": 1788, "height_mm": 1540, "wheelbase_mm": 2700, "ground_clearance_mm": 150,
         "made_in_north_america": True, "battery_sourcing_compliant": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.2, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "ota_updates": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "nissan_ariya", "name": "Nissan Ariya Evolve+ e-4ORCE", "brand": "Nissan",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 53590,
         "range_km": 435, "battery_kwh": 87, "dc_charging_kw": 130, "zero_to_100_kmh": 5.1,
         "top_speed_kmh": 200, "horsepower": 389, "torque_nm": 600, "awd": True,
         "kwh_per_100km": 20.0, "cargo_liters": 466, "curb_weight_kg": 2207, "length_mm": 4595,
         "width_mm": 1850, "height_mm": 1660, "wheelbase_mm": 2775, "ground_clearance_mm": 185,
         "ota_updates": True, "heat_pump": True, "made_in_north_america": False,
         "msrp_under_55k_sedan": True, "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5,
         "towing_capacity_kg": 0, "autopilot_available": False, "v2l_capable": False,
         "v2h_capable": False, "frunk_liters": 0},
        
        # ===== SUBARU =====
        {"id": "subaru_solterra", "name": "Subaru Solterra Premium", "brand": "Subaru",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 44995,
         "range_km": 354, "battery_kwh": 71.4, "dc_charging_kw": 150, "zero_to_100_kmh": 6.9,
         "top_speed_kmh": 160, "horsepower": 215, "torque_nm": 337, "awd": True,
         "kwh_per_100km": 20.2, "cargo_liters": 441, "curb_weight_kg": 1986, "length_mm": 4690,
         "width_mm": 1860, "height_mm": 1650, "wheelbase_mm": 2850, "ground_clearance_mm": 210,
         "ota_updates": True, "made_in_north_america": False, "msrp_under_55k_sedan": True,
         "reliability_score": 4.0, "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "heat_pump": False, "v2l_capable": False,
         "v2h_capable": False, "frunk_liters": 0},
        
        # ===== LEXUS =====
        {"id": "lexus_rz_450e", "name": "Lexus RZ 450e", "brand": "Lexus",
         "powertrain": "EV", "vehicle_type": "suv", "year": 2024, "base_price": 55175,
         "range_km": 354, "battery_kwh": 71.4, "dc_charging_kw": 150, "zero_to_100_kmh": 5.6,
         "top_speed_kmh": 160, "horsepower": 308, "torque_nm": 435, "awd": True,
         "kwh_per_100km": 20.2, "cargo_liters": 522, "curb_weight_kg": 2100, "length_mm": 4805,
         "width_mm": 1895, "height_mm": 1635, "wheelbase_mm": 2850, "ground_clearance_mm": 177,
         "ota_updates": True, "made_in_north_america": False, "msrp_under_80k_suv": True,
         "reliability_score": 4.5, "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0,
         "autopilot_available": False, "heat_pump": False, "v2l_capable": False,
         "v2h_capable": False, "frunk_liters": 0},
        
        # ===== PHEVs =====
        # Toyota
        {"id": "toyota_rav4_prime", "name": "Toyota RAV4 Prime XSE", "brand": "Toyota",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 48090,
         "range_km": 68, "combined_range_km": 980, "battery_kwh": 18.1, "dc_charging_kw": 0,
         "zero_to_100_kmh": 5.7, "top_speed_kmh": 180, "horsepower": 302, "torque_nm": 227,
         "awd": True, "kwh_per_100km": 17.5, "l_per_100km": 6.0, "cargo_liters": 949,
         "curb_weight_kg": 2015, "length_mm": 4600, "width_mm": 1855, "height_mm": 1690,
         "wheelbase_mm": 2690, "ground_clearance_mm": 200, "towing_capacity_kg": 1134,
         "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_55k_sedan": True, "reliability_score": 4.5, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False, "ota_updates": False, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "toyota_prius_prime", "name": "Toyota Prius Prime", "brand": "Toyota",
         "powertrain": "PHEV", "vehicle_type": "hatchback", "year": 2024, "base_price": 32675,
         "range_km": 72, "combined_range_km": 870, "battery_kwh": 13.6, "dc_charging_kw": 0,
         "zero_to_100_kmh": 6.6, "top_speed_kmh": 177, "horsepower": 220, "torque_nm": 208,
         "awd": True, "kwh_per_100km": 16.0, "l_per_100km": 4.7, "cargo_liters": 538,
         "curb_weight_kg": 1570, "length_mm": 4600, "width_mm": 1780, "height_mm": 1420,
         "wheelbase_mm": 2750, "ground_clearance_mm": 130, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 4.8,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "ota_updates": False, "heat_pump": False, "v2l_capable": False, "v2h_capable": False,
         "frunk_liters": 0},
        
        # Honda
        {"id": "honda_crv_phev", "name": "Honda CR-V Plug-in Hybrid", "brand": "Honda",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 47195,
         "range_km": 60, "combined_range_km": 595, "battery_kwh": 17.7, "dc_charging_kw": 0,
         "zero_to_100_kmh": 7.5, "top_speed_kmh": 180, "horsepower": 315, "torque_nm": 335,
         "awd": True, "kwh_per_100km": 18.5, "l_per_100km": 6.5, "cargo_liters": 587,
         "curb_weight_kg": 2013, "length_mm": 4694, "width_mm": 1855, "height_mm": 1679,
         "wheelbase_mm": 2700, "ground_clearance_mm": 198, "made_in_north_america": True,
         "battery_sourcing_compliant": True, "msrp_under_55k_sedan": True, "reliability_score": 4.5,
         "seats": 5, "safety_rating_ncap": 5, "towing_capacity_kg": 0, "autopilot_available": False,
         "ota_updates": False, "heat_pump": False, "v2l_capable": False, "v2h_capable": False,
         "frunk_liters": 0},
        
        # Volvo PHEVs
        {"id": "volvo_xc60_recharge", "name": "Volvo XC60 Recharge", "brand": "Volvo",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 57395,
         "range_km": 56, "combined_range_km": 660, "battery_kwh": 18.8, "dc_charging_kw": 0,
         "zero_to_100_kmh": 4.9, "top_speed_kmh": 180, "horsepower": 455, "torque_nm": 709,
         "awd": True, "kwh_per_100km": 19.5, "l_per_100km": 7.5, "cargo_liters": 468,
         "curb_weight_kg": 2185, "length_mm": 4708, "width_mm": 1902, "height_mm": 1658,
         "wheelbase_mm": 2865, "ground_clearance_mm": 216, "ota_updates": True,
         "towing_capacity_kg": 2100, "made_in_north_america": False, "reliability_score": 3.8,
         "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "volvo_xc90_recharge", "name": "Volvo XC90 Recharge", "brand": "Volvo",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 72395,
         "range_km": 51, "combined_range_km": 620, "battery_kwh": 18.8, "dc_charging_kw": 0,
         "zero_to_100_kmh": 5.4, "top_speed_kmh": 180, "horsepower": 455, "torque_nm": 709,
         "awd": True, "kwh_per_100km": 20.5, "l_per_100km": 8.0, "cargo_liters": 262,
         "curb_weight_kg": 2350, "length_mm": 4953, "width_mm": 1923, "height_mm": 1776,
         "wheelbase_mm": 2984, "ground_clearance_mm": 238, "ota_updates": True,
         "towing_capacity_kg": 2700, "made_in_north_america": False, "reliability_score": 3.8,
         "seats": 7, "safety_rating_ncap": 5, "autopilot_available": False, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # Jeep
        {"id": "jeep_wrangler_4xe", "name": "Jeep Wrangler 4xe", "brand": "Jeep",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 56395,
         "range_km": 35, "combined_range_km": 595, "battery_kwh": 17.3, "dc_charging_kw": 0,
         "zero_to_100_kmh": 6.0, "top_speed_kmh": 177, "horsepower": 375, "torque_nm": 637,
         "awd": True, "kwh_per_100km": 22.0, "l_per_100km": 10.5, "cargo_liters": 548,
         "curb_weight_kg": 2313, "length_mm": 4785, "width_mm": 1894, "height_mm": 1848,
         "wheelbase_mm": 3008, "ground_clearance_mm": 257, "towing_capacity_kg": 1588,
         "made_in_north_america": True, "battery_sourcing_compliant": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 4, "autopilot_available": False, "ota_updates": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        {"id": "jeep_grand_cherokee_4xe", "name": "Jeep Grand Cherokee 4xe", "brand": "Jeep",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 62875,
         "range_km": 42, "combined_range_km": 710, "battery_kwh": 17.3, "dc_charging_kw": 0,
         "zero_to_100_kmh": 6.0, "top_speed_kmh": 209, "horsepower": 375, "torque_nm": 637,
         "awd": True, "kwh_per_100km": 20.5, "l_per_100km": 9.5, "cargo_liters": 1067,
         "curb_weight_kg": 2540, "length_mm": 4914, "width_mm": 1979, "height_mm": 1804,
         "wheelbase_mm": 2964, "ground_clearance_mm": 221, "towing_capacity_kg": 2722,
         "made_in_north_america": True, "battery_sourcing_compliant": True, "reliability_score": 3.5,
         "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False, "ota_updates": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # Mazda
        {"id": "mazda_cx90_phev", "name": "Mazda CX-90 PHEV", "brand": "Mazda",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 47445,
         "range_km": 42, "combined_range_km": 800, "battery_kwh": 17.8, "dc_charging_kw": 0,
         "zero_to_100_kmh": 5.9, "top_speed_kmh": 200, "horsepower": 323, "torque_nm": 500,
         "awd": True, "kwh_per_100km": 19.0, "l_per_100km": 8.4, "cargo_liters": 453,
         "curb_weight_kg": 2350, "length_mm": 5119, "width_mm": 1994, "height_mm": 1747,
         "wheelbase_mm": 3120, "ground_clearance_mm": 206, "towing_capacity_kg": 2268,
         "made_in_north_america": True, "battery_sourcing_compliant": True,
         "msrp_under_55k_sedan": True, "reliability_score": 4.0, "seats": 7, "safety_rating_ncap": 5,
         "autopilot_available": False, "ota_updates": False, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # Lexus PHEV
        {"id": "lexus_nx_450h", "name": "Lexus NX 450h+", "brand": "Lexus",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 58785,
         "range_km": 61, "combined_range_km": 880, "battery_kwh": 18.1, "dc_charging_kw": 0,
         "zero_to_100_kmh": 6.0, "top_speed_kmh": 200, "horsepower": 302, "torque_nm": 227,
         "awd": True, "kwh_per_100km": 17.5, "l_per_100km": 6.0, "cargo_liters": 520,
         "curb_weight_kg": 2030, "length_mm": 4660, "width_mm": 1865, "height_mm": 1660,
         "wheelbase_mm": 2690, "ground_clearance_mm": 177, "towing_capacity_kg": 907,
         "made_in_north_america": True, "battery_sourcing_compliant": True, "reliability_score": 4.5,
         "seats": 5, "safety_rating_ncap": 5, "autopilot_available": False, "ota_updates": False,
         "heat_pump": False, "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
        
        # BMW PHEV
        {"id": "bmw_x5_xdrive50e", "name": "BMW X5 xDrive50e", "brand": "BMW",
         "powertrain": "PHEV", "vehicle_type": "suv", "year": 2024, "base_price": 73900,
         "range_km": 64, "combined_range_km": 700, "battery_kwh": 25.7, "dc_charging_kw": 0,
         "zero_to_100_kmh": 4.8, "top_speed_kmh": 243, "horsepower": 483, "torque_nm": 700,
         "awd": True, "kwh_per_100km": 21.0, "l_per_100km": 8.5, "cargo_liters": 500,
         "curb_weight_kg": 2595, "length_mm": 4922, "width_mm": 2004, "height_mm": 1745,
         "wheelbase_mm": 2975, "ground_clearance_mm": 214, "towing_capacity_kg": 2700,
         "made_in_north_america": True, "reliability_score": 3.5, "seats": 5, "safety_rating_ncap": 5,
         "autopilot_available": False, "ota_updates": True, "heat_pump": False,
         "v2l_capable": False, "v2h_capable": False, "frunk_liters": 0},
    ]
    
    # If requested, merge in synchronization data
    added = 0
    skipped = 0
    if use_sync:
        try:
            with open("evdb_sync.json", "r", encoding="utf-8") as f:
                sync_list = json.load(f)
            existing_names = {v.get("name", "").strip().lower() for v in vehicles_data}
            for entry in sync_list:
                name = entry.get("name", "").strip()
                if not name:
                    continue
                if name.lower() in existing_names:
                    skipped += 1
                    continue
                vehicles_data.append(entry)
                existing_names.add(name.lower())
                added += 1
        except FileNotFoundError:
            # sync file simply isn't present; ignore
            pass
    return vehicles_data, added, skipped


# ============================================
# INCENTIVE CALCULATOR
# ============================================

@st.cache_data
def get_incentives_data():
    """Get incentive data for all regions"""
    return {
        "usa_federal": {"ev": 7500, "phev": 3750, "name": "Federal Tax Credit"},
        "usa_california": {"ev": 9500, "phev": 5750, "name": "Federal + CA Rebate"},
        "usa_colorado": {"ev": 12500, "phev": 6250, "name": "Federal + CO Credit"},
        "usa_new_jersey": {"ev": 11500, "phev": 3750, "name": "Federal + NJ Rebate"},
        "usa_new_york": {"ev": 10000, "phev": 4250, "name": "Federal + NY Rebate"},
        "usa_texas": {"ev": 10000, "phev": 6250, "name": "Federal + TX Rebate"},
        "canada_federal": {"ev": 5000, "phev": 2500, "name": "iZEV Federal"},
        "canada_quebec": {"ev": 12000, "phev": 7500, "name": "Federal + QC Rebate"},
        "canada_bc": {"ev": 9000, "phev": 4500, "name": "Federal + BC Rebate"},
        "canada_ontario": {"ev": 5000, "phev": 2500, "name": "Federal Only"},
        "uk": {"ev": 1500, "phev": 0, "name": "Plug-in Grant (GBP)"},
        "germany": {"ev": 4500, "phev": 0, "name": "Umweltbonus (EUR)"},
        "france": {"ev": 5000, "phev": 0, "name": "Bonus Écologique (EUR)"},
        "netherlands": {"ev": 2950, "phev": 0, "name": "SEPP Subsidy (EUR)"},
        "norway": {"ev": 0, "phev": 0, "name": "VAT Exempt (25% savings)"},
        "australia": {"ev": 3000, "phev": 0, "name": "State Rebates (AUD)"},
    }


def calculate_incentive(vehicle_data: Dict, region: str) -> float:
    """Calculate incentive for a vehicle in a region"""
    incentives = get_incentives_data()
    region_data = incentives.get(region, {"ev": 0, "phev": 0})
    
    powertrain = vehicle_data.get("powertrain", "EV")
    price = vehicle_data.get("base_price", 0)
    
    # Check eligibility based on price caps
    if region.startswith("usa"):
        vehicle_type = vehicle_data.get("vehicle_type", "sedan")
        if vehicle_type in ["sedan", "hatchback"]:
            if price > 55000:
                return 0
        else:
            if price > 80000:
                return 0
        
        # Check manufacturing requirements for US federal
        if not vehicle_data.get("made_in_north_america", False):
            return region_data.get("ev" if powertrain == "EV" else "phev", 0) * 0.5
    
    return region_data.get("ev" if powertrain == "EV" else "phev", 0)


# ============================================
# TCO CALCULATOR
# ============================================

def calculate_tco(vehicle_data: Dict, preferences: UserPreferences) -> TCOResult:
    """Calculate Total Cost of Ownership"""
    
    # Get incentive
    incentive = calculate_incentive(vehicle_data, preferences.region.value)
    
    purchase_price = vehicle_data.get("base_price", 0) + 1500  # + destination
    net_purchase_price = purchase_price - incentive
    
    # Annual fuel cost
    annual_km = preferences.annual_km
    powertrain = vehicle_data.get("powertrain", "EV")
    
    if powertrain == "EV":
        kwh_per_100km = vehicle_data.get("kwh_per_100km", 18)
        annual_kwh = (kwh_per_100km / 100) * annual_km
        annual_fuel_cost = annual_kwh * preferences.electricity_cost_kwh
    else:  # PHEV
        electric_range = vehicle_data.get("range_km", 50)
        daily_km = preferences.daily_commute_km
        
        if electric_range >= daily_km:
            electric_ratio = 0.70
        elif electric_range >= daily_km * 0.5:
            electric_ratio = 0.50
        else:
            electric_ratio = 0.30
        
        electric_km = annual_km * electric_ratio
        gas_km = annual_km * (1 - electric_ratio)
        
        kwh_per_100km = vehicle_data.get("kwh_per_100km", 18)
        l_per_100km = vehicle_data.get("l_per_100km", 6)
        
        electric_cost = (kwh_per_100km / 100) * electric_km * preferences.electricity_cost_kwh
        gas_cost = (l_per_100km / 100) * gas_km * preferences.gas_cost_liter
        annual_fuel_cost = electric_cost + gas_cost
    
    # Maintenance
    if powertrain == "EV":
        annual_maintenance = annual_km * 0.03
    else:
        annual_maintenance = annual_km * 0.05
    
    # Insurance - region specific
    region_insurance_map = {
        "usa_federal": 1800,
        "usa_california": 2000,
        "usa_colorado": 1700,
        "usa_new_jersey": 2100,
        "usa_new_york": 2200,
        "usa_texas": 1600,
        "canada_federal": 1400,
        "canada_quebec": 1200,
        "canada_bc": 1300,
        "canada_ontario": 1350,
        "uk": 900,
        "germany": 800,
        "france": 850,
        "netherlands": 950,
        "norway": 1000,
        "australia": 1100,
        "portugal": 700
    }
    region_key = preferences.region.value if hasattr(preferences.region, 'value') else str(preferences.region)
    base_insurance = region_insurance_map.get(region_key, 1500)
    # Optionally, you can still differentiate by powertrain if needed:
    # if powertrain == "EV":
    #     base_insurance += 100
    price_factor = (vehicle_data.get("base_price", 40000) / 10000) * 100
    annual_insurance = base_insurance + price_factor
    
    # Registration
    annual_registration = 150 if powertrain == "EV" else 200
    
    # Calculate totals
    years = preferences.ownership_years
    total_fuel = annual_fuel_cost * years
    total_maintenance = annual_maintenance * years
    total_insurance = annual_insurance * years
    total_registration = annual_registration * years
    
    # Depreciation
    if powertrain == "EV":
        resale_percent = 45
    else:
        resale_percent = 40
    
    resale_value = net_purchase_price * (resale_percent / 100)
    depreciation = net_purchase_price - resale_value
    
    # Total TCO
    total_tco = (
        net_purchase_price - resale_value +
        total_fuel + total_maintenance + total_insurance + total_registration
    )
    
    # ICE comparison
    ice_annual_fuel = (9.0 / 100) * annual_km * preferences.gas_cost_liter
    ice_annual_maintenance = annual_km * 0.07
    ice_total = (
        40000 * 0.5 +  # Depreciation
        ice_annual_fuel * years +
        ice_annual_maintenance * years +
        1500 * years +  # Insurance
        150 * years  # Registration
    )
    
    savings = ice_total - total_tco
    
    return TCOResult(
        vehicle_name=vehicle_data.get("name", "Unknown"),
        purchase_price=purchase_price,
        incentives_total=incentive,
        net_purchase_price=net_purchase_price,
        annual_fuel_cost=annual_fuel_cost,
        annual_maintenance_cost=annual_maintenance,
        annual_insurance_cost=annual_insurance,
        annual_registration_cost=annual_registration,
        total_fuel_cost=total_fuel,
        total_maintenance_cost=total_maintenance,
        total_insurance_cost=total_insurance,
        total_registration_cost=total_registration,
        depreciation=depreciation,
        total_cost_of_ownership=total_tco,
        cost_per_km=total_tco / (annual_km * years) if annual_km > 0 else 0,
        cost_per_year=total_tco / years,
        savings_vs_avg_ice=savings
    )


# ============================================
# SCORING ENGINE
# ============================================

def score_vehicle(vehicle_data: Dict, preferences: UserPreferences) -> Dict:
    """Score a vehicle against user preferences"""
    
    scores = {}
    total_score = 0
    max_possible = 0
    
    # Range score
    weight = preferences.range_priority
    max_possible += weight * 10
    daily_need = preferences.daily_commute_km
    vehicle_range = vehicle_data.get("range_km", 0)
    
    if vehicle_range >= daily_need * 5:
        range_score = 10
    elif vehicle_range >= daily_need * 3:
        range_score = 8
    elif vehicle_range >= daily_need * 2:
        range_score = 6
    elif vehicle_range >= daily_need * 1.5:
        range_score = 4
    else:
        range_score = 2
    
    scores["Range"] = range_score
    total_score += range_score * weight
    
    # Charging speed
    weight = preferences.charging_speed_priority
    max_possible += weight * 10
    dc_kw = vehicle_data.get("dc_charging_kw", 0)
    
    if dc_kw >= 250:
        charging_score = 10
    elif dc_kw >= 200:
        charging_score = 8
    elif dc_kw >= 150:
        charging_score = 6
    elif dc_kw >= 100:
        charging_score = 4
    else:
        charging_score = 2
    
    scores["Charging"] = charging_score
    total_score += charging_score * weight
    
    # Efficiency
    weight = preferences.efficiency_priority
    max_possible += weight * 10
    efficiency = vehicle_data.get("kwh_per_100km", 20)
    
    if efficiency <= 14:
        eff_score = 10
    elif efficiency <= 16:
        eff_score = 8
    elif efficiency <= 18:
        eff_score = 6
    elif efficiency <= 20:
        eff_score = 4
    else:
        eff_score = 2
    
    scores["Efficiency"] = eff_score
    total_score += eff_score * weight
    
    # Acceleration
    weight = preferences.acceleration_priority
    max_possible += weight * 10
    zero_to_100 = vehicle_data.get("zero_to_100_kmh", 8)
    
    if zero_to_100 <= 3.5:
        accel_score = 10
    elif zero_to_100 <= 4.5:
        accel_score = 8
    elif zero_to_100 <= 5.5:
        accel_score = 6
    elif zero_to_100 <= 7.0:
        accel_score = 4
    else:
        accel_score = 2
    
    scores["Performance"] = accel_score
    total_score += accel_score * weight
    
    # Safety
    weight = preferences.safety_priority
    max_possible += weight * 10
    safety_score = vehicle_data.get("safety_rating_ncap", 5) * 2
    scores["Safety"] = safety_score
    total_score += safety_score * weight
    
    # Reliability
    weight = preferences.reliability_priority
    max_possible += weight * 10
    reliability_score = vehicle_data.get("reliability_score", 4) * 2
    scores["Reliability"] = reliability_score
    total_score += reliability_score * weight
    
    # Cargo
    weight = preferences.cargo_priority
    max_possible += weight * 10
    cargo = vehicle_data.get("cargo_liters", 400)
    
    if cargo >= preferences.min_cargo_liters * 2:
        cargo_score = 10
    elif cargo >= preferences.min_cargo_liters * 1.5:
        cargo_score = 8
    elif cargo >= preferences.min_cargo_liters:
        cargo_score = 6
    else:
        cargo_score = 4
    
    scores["Cargo"] = cargo_score
    total_score += cargo_score * weight
    
    # Tech features
    weight = preferences.tech_features_priority
    max_possible += weight * 10
    tech_score = 0
    if vehicle_data.get("autopilot_available"):
        tech_score += 3
    if vehicle_data.get("ota_updates"):
        tech_score += 2
    if vehicle_data.get("heat_pump"):
        tech_score += 2
    if vehicle_data.get("v2l_capable"):
        tech_score += 2
    if vehicle_data.get("v2h_capable"):
        tech_score += 1
    tech_score = min(tech_score, 10)
    scores["Tech"] = tech_score
    total_score += tech_score * weight
    
    # Brand preference bonus
    brand_bonus = 0
    if preferences.preferred_brands and vehicle_data.get("brand") in preferences.preferred_brands:
        brand_bonus = 5
    
    final_score = (total_score / max_possible) * 100 if max_possible > 0 else 0
    final_score = min(final_score + brand_bonus, 100)
    
    return {
        "final_score": round(final_score, 1),
        "category_scores": scores,
        "brand_bonus": brand_bonus
    }


def filter_vehicles(vehicles: List[Dict], preferences: UserPreferences) -> List[Dict]:
    """Filter vehicles based on requirements"""
    
    filtered = []
    vehicle_type_values = [vt.value for vt in preferences.vehicle_types]
    
    for v in vehicles:
        # Budget
        if v.get("base_price", 0) > preferences.max_budget * 1.1:
            continue
        if v.get("base_price", 0) < preferences.min_budget:
            continue
        
        # Vehicle type
        if v.get("vehicle_type") not in vehicle_type_values:
            continue
        
        # Seats
        if v.get("seats", 5) < preferences.min_seats:
            continue
        
        # AWD
        if preferences.needs_awd and not v.get("awd", False):
            continue
        
        # Towing
        if preferences.needs_towing:
            if v.get("towing_capacity_kg", 0) < preferences.min_towing_kg:
                continue
        
        # Excluded brands
        if v.get("brand") in preferences.excluded_brands:
            continue
        
        filtered.append(v)
    
    return filtered


def recommend_powertrain(preferences: UserPreferences) -> Dict:
    """Recommend EV or PHEV based on preferences"""
    
    ev_score = 0
    phev_score = 0
    reasons_ev = []
    reasons_phev = []
    
    # Daily commute
    if preferences.daily_commute_km <= 50:
        ev_score += 3
        phev_score += 2
        reasons_ev.append("Short commute easily covered by EV")
    elif preferences.daily_commute_km <= 100:
        ev_score += 2
        phev_score += 2
    else:
        phev_score += 3
        reasons_phev.append("Long commute benefits from PHEV flexibility")
    
    # Long trips
    if preferences.long_trips_frequency == "never":
        ev_score += 3
        reasons_ev.append("No long trips needed")
    elif preferences.long_trips_frequency == "rarely":
        ev_score += 2
        phev_score += 2
    elif preferences.long_trips_frequency == "monthly":
        phev_score += 3
        reasons_phev.append("Regular long trips easier with PHEV")
    else:
        phev_score += 4
        reasons_phev.append("Frequent long trips - PHEV recommended")
    
    # Home charging
    if preferences.home_charging_available:
        if preferences.home_charging_type == "level2":
            ev_score += 4
            reasons_ev.append("Level 2 home charging available")
        else:
            ev_score += 2
            phev_score += 1
    else:
        phev_score += 4
        reasons_phev.append("No home charging - PHEV more flexible")
    
    # Work charging
    if preferences.work_charging_available:
        ev_score += 2
        reasons_ev.append("Work charging available")
    
    # Zero emissions priority
    if preferences.zero_emissions_priority >= 4:
        ev_score += 3
        reasons_ev.append("Strong preference for zero emissions")
    elif preferences.zero_emissions_priority <= 2:
        phev_score += 2
    
    total = ev_score + phev_score
    ev_pct = round((ev_score / total) * 100, 1) if total > 0 else 50
    phev_pct = round((phev_score / total) * 100, 1) if total > 0 else 50
    
    if ev_score > phev_score + 3:
        recommendation = "EV"
        confidence = "High"
    elif phev_score > ev_score + 3:
        recommendation = "PHEV"
        confidence = "High"
    elif ev_score > phev_score:
        recommendation = "EV"
        confidence = "Medium"
    elif phev_score > ev_score:
        recommendation = "PHEV"
        confidence = "Medium"
    else:
        recommendation = "Either"
        confidence = "Low"
    
    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "ev_score": ev_score,
        "phev_score": phev_score,
        "ev_percentage": ev_pct,
        "phev_percentage": phev_pct,
        "reasons_ev": reasons_ev,
        "reasons_phev": reasons_phev
    }


# ============================================
# CHART FUNCTIONS (Including Heatmaps)
# ============================================

def create_powertrain_gauge(ev_pct: float, phev_pct: float) -> go.Figure:
    """Create powertrain recommendation gauge"""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ev_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "EV Recommendation Score", 'font': {'size': 18, 'color': '#f3f6fa'}},
        delta={'reference': 50, 'increasing': {'color': "#00D4AA"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#b3e5fc"},
            'bar': {'color': "#42a5f5"},
            'bgcolor': "#232a36",
            'borderwidth': 2,
            'bordercolor': "#485563",
            'steps': [
                {'range': [0, 30], 'color': '#e74c3c'},
                {'range': [30, 50], 'color': '#f1c40f'},
                {'range': [50, 70], 'color': '#4ECDC4'},
                {'range': [70, 100], 'color': '#00D4AA'}
            ],
            'threshold': {
                'line': {'color': "#fff", 'width': 4},
                'thickness': 0.75,
                'value': ev_pct
            }
        }
    ))
    
    fig.add_annotation(
        x=0.5, y=-0.15,
        text=f"← PHEV ({phev_pct}%) | EV ({ev_pct}%) →",
        showarrow=False,
        font={'size': 14}
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=60),
        paper_bgcolor='#181c24',
        font={'color': "#f3f6fa"}
    )
    
    return fig


def create_vehicle_comparison_radar(vehicles_data: List[Dict], scores: List[Dict]) -> go.Figure:
    """Create radar chart comparing vehicles"""
    
    categories = ['Range', 'Charging', 'Efficiency', 'Performance', 'Safety', 'Reliability', 'Cargo', 'Tech']
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set2
    
    for i, (vehicle, score) in enumerate(zip(vehicles_data[:5], scores[:5])):
        values = [score['category_scores'].get(cat, 5) for cat in categories]
        values.append(values[0])  # Close the polygon
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=vehicle['name'][:25],
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(
            bgcolor="#232a36",
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                color="#b3e5fc",
                gridcolor="#485563"
            ),
            angularaxis=dict(color="#b3e5fc", gridcolor="#485563")
        ),
        showlegend=True,
        title={"text": "Vehicle Comparison - Category Scores", "font": {"color": "#f3f6fa"}},
        height=500,
        paper_bgcolor='#181c24',
        font={"color": "#f3f6fa"}
    )
    
    return fig


def create_specs_heatmap(vehicles_data: List[Dict]) -> go.Figure:
    """Create heatmap comparing vehicle specifications"""
    
    # Select vehicles and metrics
    vehicles = vehicles_data[:15]
    vehicle_names = [v['name'][:20] for v in vehicles]
    
    # Metrics to compare (normalized 0-10)
    metrics = ['Range', 'Charging', 'Efficiency', 'Power', 'Cargo', 'Price Value']
    
    # Create normalized data matrix
    data_matrix = []
    
    for v in vehicles:
        row = []
        # Range (normalize to 0-10, max 700km)
        row.append(min(v.get('range_km', 0) / 70, 10))
        # Charging (normalize, max 350kW)
        row.append(min(v.get('dc_charging_kw', 0) / 35, 10))
        # Efficiency (inverse, lower is better)
        eff = v.get('kwh_per_100km', 25)
        row.append(max(0, 10 - (eff - 12) / 2))
        # Power (normalize, max 600hp)
        row.append(min(v.get('horsepower', 0) / 60, 10))
        # Cargo (normalize, max 1000L)
        row.append(min(v.get('cargo_liters', 0) / 100, 10))
        # Price value (inverse of price, lower price = higher value)
        price = v.get('base_price', 50000)
        row.append(max(0, 10 - (price - 25000) / 10000))
        
        data_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=metrics,
        y=vehicle_names,
        colorscale=[[0, '#232a36'], [0.5, '#42a5f5'], [1, '#2ecc71']],
        text=[[f'{val:.1f}' for val in row] for row in data_matrix],
        texttemplate='%{text}',
        textfont={"size": 10, "color": "#f3f6fa"},
        hoverongaps=False,
        colorbar=dict(title=dict(text="Score (0-10)", font={"color": "#f3f6fa"}), tickcolor="#f3f6fa", bgcolor="#232a36")
    ))
    
    fig.update_layout(
        title={'text': 'Vehicle Specifications Heatmap (Higher = Better)', 'font': {'color': '#f3f6fa'}},
        xaxis_title='Metric',
        yaxis_title='Vehicle',
        height=600,
        yaxis=dict(tickmode='linear', color='#f3f6fa'),
        xaxis=dict(color='#f3f6fa'),
        paper_bgcolor='#181c24',
        font={'color': '#f3f6fa'}
    )
    
    return fig


def create_brand_specs_heatmap(vehicles_data: List[Dict]) -> go.Figure:
    """Create heatmap comparing brands across metrics"""
    
    # Aggregate by brand
    brand_data = {}
    for v in vehicles_data:
        brand = v.get('brand', 'Unknown')
        if brand not in brand_data:
            brand_data[brand] = {
                'range': [], 'charging': [], 'efficiency': [],
                'power': [], 'price': [], 'reliability': []
            }
        brand_data[brand]['range'].append(v.get('range_km', 0))
        brand_data[brand]['charging'].append(v.get('dc_charging_kw', 0))
        brand_data[brand]['efficiency'].append(v.get('kwh_per_100km', 20))
        brand_data[brand]['power'].append(v.get('horsepower', 0))
        brand_data[brand]['price'].append(v.get('base_price', 50000))
        brand_data[brand]['reliability'].append(v.get('reliability_score', 3.5))
    
    # Calculate averages and normalize
    brands = list(brand_data.keys())
    metrics = ['Avg Range', 'Avg Charging', 'Efficiency', 'Avg Power', 'Price Value', 'Reliability']
    
    data_matrix = []
    for brand in brands:
        row = []
        # Range
        avg_range = np.mean(brand_data[brand]['range'])
        row.append(min(avg_range / 60, 10))
        # Charging
        avg_charging = np.mean(brand_data[brand]['charging'])
        row.append(min(avg_charging / 30, 10))
        # Efficiency (inverse)
        avg_eff = np.mean(brand_data[brand]['efficiency'])
        row.append(max(0, 10 - (avg_eff - 12) / 2))
        # Power
        avg_power = np.mean(brand_data[brand]['power'])
        row.append(min(avg_power / 50, 10))
        # Price value (inverse)
        avg_price = np.mean(brand_data[brand]['price'])
        row.append(max(0, 10 - (avg_price - 25000) / 10000))
        # Reliability
        avg_rel = np.mean(brand_data[brand]['reliability'])
        row.append(avg_rel * 2)
        
        data_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=metrics,
        y=brands,
        colorscale=[[0, '#232a36'], [0.5, '#42a5f5'], [1, '#2ecc71']],
        text=[[f'{val:.1f}' for val in row] for row in data_matrix],
        texttemplate='%{text}',
        textfont={"size": 11, "color": "#f3f6fa"},
        colorbar=dict(title=dict(text="Score", font={"color": "#f3f6fa"}), tickcolor="#f3f6fa", bgcolor="#232a36")
    ))
    
    fig.update_layout(
        title={'text': 'Brand Comparison Heatmap', 'font': {'color': '#f3f6fa'}},
        xaxis_title='Metric',
        yaxis_title='Brand',
        height=500,
        yaxis=dict(color='#f3f6fa'),
        xaxis=dict(color='#f3f6fa'),
        paper_bgcolor='#181c24',
        font={'color': '#f3f6fa'}
    )
    
    return fig


def create_correlation_heatmap(vehicles_data: List[Dict]) -> go.Figure:
    """Create correlation heatmap between vehicle attributes"""
    
    df = pd.DataFrame(vehicles_data)
    
    # Select numeric columns
    numeric_cols = ['base_price', 'range_km', 'battery_kwh', 'dc_charging_kw',
                   'zero_to_100_kmh', 'horsepower', 'kwh_per_100km', 'cargo_liters',
                   'curb_weight_kg', 'reliability_score']
    
    # Filter to existing columns
    existing_cols = [col for col in numeric_cols if col in df.columns]
    
    # Calculate correlation matrix
    corr_matrix = df[existing_cols].corr()
    
    # Rename columns for display
    display_names = {
        'base_price': 'Price',
        'range_km': 'Range',
        'battery_kwh': 'Battery',
        'dc_charging_kw': 'DC Charging',
        'zero_to_100_kmh': '0-100 Time',
        'horsepower': 'Power',
        'kwh_per_100km': 'Consumption',
        'cargo_liters': 'Cargo',
        'curb_weight_kg': 'Weight',
        'reliability_score': 'Reliability'
    }
    
    labels = [display_names.get(col, col) for col in existing_cols]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale=[[0, '#232a36'], [0.5, '#42a5f5'], [1, '#2ecc71']],
        zmid=0,
        text=[[f'{val:.2f}' for val in row] for row in corr_matrix.values],
        texttemplate='%{text}',
        textfont={"size": 10, "color": "#f3f6fa"},
        colorbar=dict(title=dict(text="Correlation", font={"color": "#f3f6fa"}), tickcolor="#f3f6fa", bgcolor="#232a36")
    ))
    
    fig.update_layout(
        title={'text': 'Attribute Correlation Heatmap', 'font': {'color': '#f3f6fa'}},
        height=500,
        yaxis=dict(color='#f3f6fa'),
        xaxis=dict(color='#f3f6fa'),
        paper_bgcolor='#181c24',
        font={'color': '#f3f6fa'}
    )
    
    return fig


def create_price_range_heatmap(vehicles_data: List[Dict]) -> go.Figure:
    """Create price vs range density heatmap"""
    
    df = pd.DataFrame(vehicles_data)
    
    # Create bins
    price_bins = [25000, 35000, 45000, 55000, 65000, 75000, 85000, 100000, 150000]
    range_bins = [200, 300, 400, 500, 600, 700]
    
    price_labels = ['25-35k', '35-45k', '45-55k', '55-65k', '65-75k', '75-85k', '85-100k', '100k+']
    range_labels = ['200-300', '300-400', '400-500', '500-600', '600+']
    
    # Create 2D histogram
    df['price_bin'] = pd.cut(df['base_price'], bins=price_bins, labels=price_labels)
    df['range_bin'] = pd.cut(df['range_km'], bins=range_bins, labels=range_labels)
    
    # Count vehicles in each bin
    heatmap_data = df.groupby(['range_bin', 'price_bin']).size().unstack(fill_value=0)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns.tolist(),
        y=heatmap_data.index.tolist(),
        colorscale=[[0, '#232a36'], [0.5, '#42a5f5'], [1, '#2ecc71']],
        text=heatmap_data.values,
        texttemplate='%{text}',
        textfont={"size": 14, "color": "#f3f6fa"},
        colorbar=dict(title=dict(text="# Vehicles", font={"color": "#f3f6fa"}), tickcolor="#f3f6fa", bgcolor="#232a36")
    ))
    
    fig.update_layout(
        title={'text': 'Vehicle Distribution: Price vs Range', 'font': {'color': '#f3f6fa'}},
        xaxis_title='Price Range (€)',
        yaxis_title='Range (km)',
        height=400,
        yaxis=dict(color='#f3f6fa'),
        xaxis=dict(color='#f3f6fa'),
        paper_bgcolor='#181c24',
        font={'color': '#f3f6fa'}
    )
    
    return fig


def create_tco_heatmap(vehicles_data: List[Dict], tco_results: List[TCOResult]) -> go.Figure:
    """Create TCO breakdown heatmap"""
    
    vehicles = vehicles_data[:12]
    tcos = tco_results[:12]
    
    vehicle_names = [v['name'][:20] for v in vehicles]
    categories = ['Depreciation', 'Fuel', 'Maintenance', 'Insurance', 'Registration']
    
    data_matrix = []
    for tco in tcos:
        row = [
            tco.depreciation / 1000,  # In thousands
            tco.total_fuel_cost / 1000,
            tco.total_maintenance_cost / 1000,
            tco.total_insurance_cost / 1000,
            tco.total_registration_cost / 1000
        ]
        data_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=categories,
        y=vehicle_names,
        colorscale=[[0, '#232a36'], [0.5, '#42a5f5'], [1, '#e74c3c']],
        text=[[f'€{val:.1f}k' for val in row] for row in data_matrix],
        texttemplate='%{text}',
        textfont={"size": 10, "color": "#f3f6fa"},
        colorbar=dict(title=dict(text="Cost (€k)", font={"color": "#f3f6fa"}), tickcolor="#f3f6fa", bgcolor="#232a36")
    ))
    
    fig.update_layout(
        title={'text': 'TCO Breakdown Heatmap (5 Years, in €1000s)', 'font': {'color': '#f3f6fa'}},
        xaxis_title='Cost Category',
        yaxis_title='Vehicle',
        height=500,
        yaxis=dict(color='#f3f6fa'),
        xaxis=dict(color='#f3f6fa'),
        paper_bgcolor='#181c24',
        font={'color': '#f3f6fa'}
    )
    
    return fig


def create_features_heatmap(vehicles_data: List[Dict]) -> go.Figure:
    """Create features availability heatmap"""
    
    vehicles = vehicles_data[:15]
    vehicle_names = [v['name'][:20] for v in vehicles]
    
    features = ['AWD', 'Autopilot', 'OTA Updates', 'Heat Pump', 'V2L', 'V2H', 'Frunk']
    
    data_matrix = []
    for v in vehicles:
        row = [
            1 if v.get('awd') else 0,
            1 if v.get('autopilot_available') else 0,
            1 if v.get('ota_updates') else 0,
            1 if v.get('heat_pump') else 0,
            1 if v.get('v2l_capable') else 0,
            1 if v.get('v2h_capable') else 0,
            1 if v.get('frunk_liters', 0) > 0 else 0
        ]
        data_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=features,
        y=vehicle_names,
        colorscale=[[0, '#232a36'], [1, '#2ecc71']],
        text=[['✓' if val == 1 else '✗' for val in row] for row in data_matrix],
        texttemplate='%{text}',
        textfont={"size": 14, "color": "#f3f6fa"},
        showscale=False
    ))
    
    fig.update_layout(
        title={'text': 'Feature Availability Matrix', 'font': {'color': '#f3f6fa'}},
        xaxis_title='Feature',
        yaxis_title='Vehicle',
        height=550,
        yaxis=dict(color='#f3f6fa'),
        xaxis=dict(color='#f3f6fa'),
        paper_bgcolor='#181c24',
        font={'color': '#f3f6fa'}
    )
    
    return fig


def create_price_range_chart(vehicles_data: List[Dict], preferences: UserPreferences) -> go.Figure:
    """Create price vs range scatter plot"""
    
    df = pd.DataFrame(vehicles_data)
    
    # Add incentive-adjusted price
    df['net_price'] = df.apply(
        lambda x: x['base_price'] - calculate_incentive(x.to_dict(), preferences.region.value),
        axis=1
    )
    
    fig = px.scatter(
        df,
        x='net_price',
        y='range_km',
        color='brand',
        size='horsepower',
        hover_name='name',
        hover_data={
            'base_price': ':€,.0f',
            'net_price': ':€,.0f',
            'range_km': True,
            'horsepower': True,
            'zero_to_100_kmh': True
        },
        title='Price vs Range (After Incentives)',
        labels={
            'net_price': 'Net Price (€)',
            'range_km': 'Range (km)',
            'brand': 'Brand'
        }
    )
    
    # Add budget line
    fig.add_vline(
        x=preferences.max_budget,
        line_dash="dash",
        line_color="red",
        annotation_text="Budget Limit"
    )
    
    fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
    
    return fig


def create_tco_comparison_chart(vehicles_data: List[Dict], tco_results: List[TCOResult]) -> go.Figure:
    """Create TCO comparison bar chart"""
    
    names = [v['name'][:25] for v in vehicles_data[:10]]
    
    fig = go.Figure()
    
    # Stacked bar components
    fig.add_trace(go.Bar(
        name='Depreciation',
        x=names,
        y=[tco.depreciation for tco in tco_results[:10]],
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='Fuel/Energy',
        x=names,
        y=[tco.total_fuel_cost for tco in tco_results[:10]],
        marker_color='#2ecc71'
    ))
    
    fig.add_trace(go.Bar(
        name='Maintenance',
        x=names,
        y=[tco.total_maintenance_cost for tco in tco_results[:10]],
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        name='Insurance',
        x=names,
        y=[tco.total_insurance_cost for tco in tco_results[:10]],
        marker_color='#9b59b6'
    ))
    
    fig.update_layout(
        barmode='stack',
        title='Total Cost of Ownership Comparison (5 Years)',
        xaxis_title='Vehicle',
        yaxis_title='Cost ($)',
        height=500,
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_tco_breakdown_pie(tco: TCOResult) -> go.Figure:
    """Create TCO breakdown pie chart"""
    
    labels = ['Depreciation', 'Fuel/Energy', 'Maintenance', 'Insurance', 'Registration']
    values = [
        tco.depreciation,
        tco.total_fuel_cost,
        tco.total_maintenance_cost,
        tco.total_insurance_cost,
        tco.total_registration_cost
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
    )])
    
    fig.update_layout(
        title=f'TCO Breakdown: {tco.vehicle_name[:30]}',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_efficiency_comparison(vehicles_data: List[Dict]) -> go.Figure:
    """Create efficiency comparison chart"""
    
    df = pd.DataFrame(vehicles_data)
    df = df.sort_values('kwh_per_100km')
    
    fig = px.bar(
        df.head(15),
        x='name',
        y='kwh_per_100km',
        color='brand',
        title='Energy Efficiency Comparison (Lower is Better)',
        labels={
            'name': 'Vehicle',
            'kwh_per_100km': 'kWh per 100km'
        }
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=450,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_charging_speed_chart(vehicles_data: List[Dict]) -> go.Figure:
    """Create charging speed comparison"""
    
    df = pd.DataFrame(vehicles_data)
    df = df.sort_values('dc_charging_kw', ascending=False)
    
    fig = px.bar(
        df.head(15),
        x='name',
        y='dc_charging_kw',
        color='brand',
        title='DC Fast Charging Speed Comparison',
        labels={
            'name': 'Vehicle',
            'dc_charging_kw': 'Max DC Charging (kW)'
        }
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=450,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_brand_distribution(vehicles_data: List[Dict]) -> go.Figure:
    """Create brand distribution chart"""
    
    df = pd.DataFrame(vehicles_data)
    brand_counts = df['brand'].value_counts()
    
    fig = px.pie(
        values=brand_counts.values,
        names=brand_counts.index,
        title='Vehicles by Brand in Your Selection',
        hole=0.3
    )
    
    fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
    
    return fig


def create_savings_chart(tco_results: List[TCOResult]) -> go.Figure:
    """Create savings vs ICE comparison"""
    
    names = [tco.vehicle_name[:25] for tco in tco_results[:10]]
    savings = [tco.savings_vs_avg_ice for tco in tco_results[:10]]
    
    colors = ['#2ecc71' if s > 0 else '#e74c3c' for s in savings]
    
    fig = go.Figure(go.Bar(
        x=names,
        y=savings,
        marker_color=colors
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title='5-Year Savings vs Average Gas Car',
        xaxis_title='Vehicle',
        yaxis_title='Savings ($)',
        height=400,
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_performance_scatter(vehicles_data: List[Dict]) -> go.Figure:
    """Create performance scatter plot"""
    
    df = pd.DataFrame(vehicles_data)
    
    fig = px.scatter(
        df,
        x='zero_to_100_kmh',
        y='horsepower',
        color='brand',
        size='base_price',
        hover_name='name',
        title='Performance: 0-100 km/h vs Horsepower',
        labels={
            'zero_to_100_kmh': '0-100 km/h (seconds)',
            'horsepower': 'Horsepower'
        }
    )
    
    fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
    
    return fig


def create_range_battery_scatter(vehicles_data: List[Dict]) -> go.Figure:
    """Create range vs battery size scatter"""
    
    df = pd.DataFrame(vehicles_data)
    
    fig = px.scatter(
        df,
        x='battery_kwh',
        y='range_km',
        color='brand',
        size='kwh_per_100km',
        hover_name='name',
        trendline='ols',
        title='Range vs Battery Size (Efficiency Analysis)',
        labels={
            'battery_kwh': 'Battery Size (kWh)',
            'range_km': 'Range (km)'
        }
    )
    
    fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
    
    return fig


def create_specs_comparison_table(vehicles_data: List[Dict]) -> pd.DataFrame:
    """Create specs comparison dataframe"""
    
    df = pd.DataFrame(vehicles_data)
    
    display_cols = [
        'name', 'brand', 'powertrain', 'base_price', 'range_km',
        'battery_kwh', 'dc_charging_kw', 'zero_to_100_kmh',
        'horsepower', 'cargo_liters', 'seats', 'awd'
    ]
    
    # Filter to existing columns
    existing_cols = [col for col in display_cols if col in df.columns]
    
    df_display = df[existing_cols].copy()
    
    # Rename columns
    column_names = {
        'name': 'Vehicle',
        'brand': 'Brand',
        'powertrain': 'Type',
        'base_price': 'Price ($)',
        'range_km': 'Range (km)',
        'battery_kwh': 'Battery (kWh)',
        'dc_charging_kw': 'DC Charging (kW)',
        'zero_to_100_kmh': '0-100 km/h (s)',
        'horsepower': 'HP',
        'cargo_liters': 'Cargo (L)',
        'seats': 'Seats',
        'awd': 'AWD'
    }
    
    df_display = df_display.rename(columns=column_names)
    
    return df_display


# ============================================
# MAIN STREAMLIT APP
# ============================================

def main():
    # Header
    st.markdown('<p class="main-header">🚗 EV/PHEV Selection Tool</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Find your perfect electric vehicle with AI-powered recommendations</p>', unsafe_allow_html=True)
    
    # Load vehicle database (optionally merging evdb sync data)
    # the checkbox is created later after sidebar context is opened
    vehicles_data = []  # placeholder
    
    # Sidebar - User Preferences
    with st.sidebar:
        st.header("⚙️ Your Preferences")
        
        # Live database option
        use_sync = st.checkbox("Use live EVDB data (evdb_sync.json)", value=False,
                              help="Merge scraped data from ev-database.org into the local list")
        # load the vehicles immediately so that any subsequent widgets (brand list etc.)
        # can access the correct dataset
        vehicles_data, added_sync, skipped_sync = load_vehicle_database(use_sync)
        if use_sync:
            if added_sync:
                st.sidebar.success(f"Imported {added_sync} vehicles from evdb_sync.json")
            if skipped_sync:
                st.sidebar.info(f"Skipped {skipped_sync} duplicate names from sync")
        # any duplicate detection can also run here if desired
        name_counts = Counter(v.get('name','').strip().lower() for v in vehicles_data)
        duplicates = {n:cnt for n,cnt in name_counts.items() if cnt > 1}
        if duplicates:
            st.sidebar.warning(f"Detected {len(duplicates)} duplicate vehicle names in database")
            for n,cnt in duplicates.items():
                st.sidebar.write(f"{n} (x{cnt})")
        
        # Driving Habits
        st.subheader("🚙 Driving Habits")
        daily_commute = st.slider("Daily Commute (km)", 0, 200, 50, help="Your round-trip daily driving distance")
        annual_km = st.slider("Annual Driving (km)", 5000, 50000, 20000, step=1000)
        long_trips = st.selectbox(
            "Long Trip Frequency (300+ km)",
            ["never", "rarely", "monthly", "weekly"],
            index=1
        )
        
        # Charging
        st.subheader("🔌 Charging Situation")
        home_charging = st.selectbox(
            "Home Charging",
            ["Level 2 (240V)", "Level 1 (120V)", "No Home Charging"],
            index=0,
            help="Level 2 adds ~40km/hour, Level 1 adds ~6km/hour"
        )
        work_charging = st.checkbox("Work Charging Available")
        
        # Budget
        st.subheader("💰 Budget")
        budget_range = st.slider(
            "Budget Range (€)",
            20000, 150000, (30000, 60000), step=5000
        )
        
        region = st.selectbox(
            "Your Region",
            [
                ("USA - California", "usa_california"),
                ("USA - Colorado", "usa_colorado"),
                ("USA - New Jersey", "usa_new_jersey"),
                ("USA - New York", "usa_new_york"),
                ("USA - Texas", "usa_texas"),
                ("USA - Other", "usa_federal"),
                ("Canada - Quebec", "canada_quebec"),
                ("Canada - BC", "canada_bc"),
                ("Canada - Ontario", "canada_ontario"),
                ("Canada - Other", "canada_federal"),
                ("UK", "uk"),
                ("Germany", "germany"),
                ("France", "france"),
                ("Norway", "norway"),
                ("Australia", "australia"),
                ("Portugal", "portugal"),
            ],
            format_func=lambda x: x[0]
        )
        
        ownership_years = st.selectbox("Ownership Period", [3, 5, 7, 10], index=1)
        
        # Energy Costs
        st.subheader("⚡ Energy Costs")
        electricity_cost = st.slider("Electricity (€/kWh)", 0.05, 0.40, 0.15, 0.01)
        gas_cost = st.slider("Gas (€/L)", 0.80, 2.50, 1.50, 0.05)
        
        # Vehicle Preferences
        st.subheader("🚘 Vehicle Type")
        vehicle_types = st.multiselect(
            "Vehicle Types",
            ["sedan", "suv", "crossover", "hatchback", "truck", "minivan"],
            default=["sedan", "suv", "crossover"]
        )
        
        min_seats = st.selectbox("Minimum Seats", [2, 4, 5, 6, 7], index=2)
        needs_awd = st.checkbox("Require AWD")
        needs_towing = st.checkbox("Need Towing Capability")
        
        if needs_towing:
            min_towing = st.slider("Min Towing (kg)", 500, 5000, 1500, 100)
        else:
            min_towing = 0
        
        # Priorities
        st.subheader("📊 Priorities (1-5)")
        col1, col2 = st.columns(2)
        with col1:
            range_priority = st.slider("Range", 1, 5, 3, key="range")
            charging_priority = st.slider("Charging", 1, 5, 3, key="charging")
            efficiency_priority = st.slider("Efficiency", 1, 5, 3, key="efficiency")
            safety_priority = st.slider("Safety", 1, 5, 4, key="safety")
        with col2:
            accel_priority = st.slider("Performance", 1, 5, 2, key="accel")
            tech_priority = st.slider("Tech", 1, 5, 3, key="tech")
            reliability_priority = st.slider("Reliability", 1, 5, 4, key="reliability")
            emissions_priority = st.slider("Zero Emissions", 1, 5, 3, key="emissions")
        
        # Brand Preferences
        st.subheader("🏷️ Brand Preferences")
        # we'll load the database here so that the checkbox above influences it
        all_brands = sorted(list(set(v['brand'] for v in vehicles_data)))
        preferred_brands = st.multiselect("Preferred Brands", all_brands)
        excluded_brands = st.multiselect("Excluded Brands", all_brands)

        # Add recalculate button
        recalc = st.button("🔄 Recalculate", help="Apply your preferences and update all results.")

    # Build preferences object
    if recalc:
        preferences = UserPreferences(
            daily_commute_km=daily_commute,
            annual_km=annual_km,
            long_trips_frequency=long_trips,
            home_charging_available=home_charging != "No Home Charging",
            home_charging_type="level2" if "Level 2" in home_charging else "level1",
            work_charging_available=work_charging,
            max_budget=budget_range[1],
            min_budget=budget_range[0],
            region=Region(region[1]),
            ownership_years=ownership_years,
            electricity_cost_kwh=electricity_cost,
            gas_cost_liter=gas_cost,
            vehicle_types=[VehicleType(vt) for vt in vehicle_types] if vehicle_types else [VehicleType.SEDAN],
            min_seats=min_seats,
            needs_awd=needs_awd,
            needs_towing=needs_towing,
            min_towing_kg=min_towing,
            range_priority=range_priority,
            charging_speed_priority=charging_priority,
            efficiency_priority=efficiency_priority,
            acceleration_priority=accel_priority,
            tech_features_priority=tech_priority,
            safety_priority=safety_priority,
            reliability_priority=reliability_priority,
            zero_emissions_priority=emissions_priority,
            preferred_brands=preferred_brands,
            excluded_brands=excluded_brands
        )
    else:
        preferences = None
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Recommendations",
        "🔥 Heatmaps",
        "📊 Comparison Charts",
        "💰 Cost Analysis",
        "📋 All Vehicles",
        "🔍 Vehicle Details"
    ])
    
    # Filter vehicles
    if preferences is not None:
        filtered_vehicles = filter_vehicles(vehicles_data, preferences)

        # Score vehicles
        scored_vehicles = []
        for v in filtered_vehicles:
            score = score_vehicle(v, preferences)
            tco = calculate_tco(v, preferences)
            scored_vehicles.append({
                'vehicle': v,
                'score': score,
                'tco': tco
            })

        # Sort by score
        scored_vehicles.sort(key=lambda x: x['score']['final_score'], reverse=True)

        # Get powertrain recommendation
        pt_rec = recommend_powertrain(preferences)
    else:
        filtered_vehicles = []
        scored_vehicles = []
        pt_rec = None
    
    # ==================== TAB 1: RECOMMENDATIONS ====================
    with tab1:
        st.header("🎯 Your Personalized Recommendations")
        if pt_rec is None or not scored_vehicles:
            st.info("Set your preferences and click 'Recalculate' to see recommendations.")
        else:
            # Powertrain recommendation
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Powertrain Recommendation")
                st.plotly_chart(
                    create_powertrain_gauge(pt_rec['ev_percentage'], pt_rec['phev_percentage']),
                    use_container_width=True
                )
            with col2:
                st.subheader(f"Recommended: {pt_rec['recommendation']}")
                st.write(f"**Confidence:** {pt_rec['confidence']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if pt_rec['reasons_ev']:
                        st.markdown("**Reasons favoring EV:**")
                        for reason in pt_rec['reasons_ev']:
                            st.write(f"✅ {reason}")
                with col_b:
                    if pt_rec['reasons_phev']:
                        st.markdown("**Reasons favoring PHEV:**")
                        for reason in pt_rec['reasons_phev']:
                            st.write(f"🔌 {reason}")
            st.divider()
            # Top recommendations
            st.subheader(f"🏆 Top {min(5, len(scored_vehicles))} Recommendations")
            if not scored_vehicles:
                st.warning("⚠️ No vehicles match your criteria. Try adjusting your filters in the sidebar.")
            else:
                for i, item in enumerate(scored_vehicles[:5]):
                    v = item['vehicle']
                    score = item['score']
                    tco = item['tco']
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        with col1:
                            powertrain_icon = "⚡" if v['powertrain'] == "EV" else "🔌"
                            st.markdown(f"### {i+1}. {powertrain_icon} {v['name']}")
                            st.write(f"**{v['brand']}** | {v['vehicle_type'].upper()} | {'AWD' if v.get('awd') else 'RWD/FWD'}")
                        with col2:
                            st.metric("Match Score", f"{score['final_score']:.0f}/100")
                            st.write(f"Range: **{v['range_km']} km**")
                        with col3:
                            st.metric("Net Price", f"€{tco.net_purchase_price:,.0f}")
                            st.write(f"Incentives: **€{tco.incentives_total:,.0f}**")
                        with col4:
                            st.metric(f"{ownership_years}-Year TCO", f"€{tco.total_cost_of_ownership:,.0f}")
                            if tco.savings_vs_avg_ice > 0:
                                st.write(f"💰 Saves **€{tco.savings_vs_avg_ice:,.0f}**")
                        st.divider()
                # Special picks
                if scored_vehicles and len(scored_vehicles) >= 1:
                    st.subheader("⭐ Special Picks")
                    col1, col2, col3 = st.columns(3)
                    # Best value
                    best_value = min(scored_vehicles[:10], key=lambda x: x['tco'].total_cost_of_ownership)
                    with col1:
                        st.markdown("### 💰 Best Value")
                        st.write(f"**{best_value['vehicle']['name']}**")
                        st.write(f"TCO: €{best_value['tco'].total_cost_of_ownership:,.0f}")
                    # Best range
                    best_range = max(scored_vehicles[:10], key=lambda x: x['vehicle']['range_km'])
                    with col2:
                        st.markdown("### 🛣️ Best Range")
                        st.write(f"**{best_range['vehicle']['name']}**")
                        st.write(f"Range: {best_range['vehicle']['range_km']} km")
                    # Best performance
                    best_perf = min(scored_vehicles[:10], key=lambda x: x['vehicle']['zero_to_100_kmh'])
                    with col3:
                        st.markdown("### 🏎️ Best Performance")
                        st.write(f"**{best_perf['vehicle']['name']}**")
                        st.write(f"0-100: {best_perf['vehicle']['zero_to_100_kmh']}s")
    
    # ==================== TAB 2: HEATMAPS ====================
    with tab2:
        st.header("🔥 Heatmap Analysis")
        
        if not scored_vehicles:
            st.warning("No vehicles to analyze. Adjust your filters.")
        else:
            # Specs heatmap
            st.subheader("📊 Vehicle Specifications Heatmap")
            st.plotly_chart(
                create_specs_heatmap([s['vehicle'] for s in scored_vehicles]),
                use_container_width=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Brand comparison heatmap
                st.subheader("🏷️ Brand Comparison")
                st.plotly_chart(
                    create_brand_specs_heatmap([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            with col2:
                # Features heatmap
                st.subheader("✨ Feature Availability")
                st.plotly_chart(
                    create_features_heatmap([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            # Correlation heatmap
            st.subheader("🔗 Attribute Correlations")
            st.plotly_chart(
                create_correlation_heatmap([s['vehicle'] for s in scored_vehicles]),
                use_container_width=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price vs Range distribution
                st.subheader("📍 Price vs Range Distribution")
                st.plotly_chart(
                    create_price_range_heatmap([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            with col2:
                # TCO heatmap
                st.subheader("💵 TCO Breakdown Heatmap")
                st.plotly_chart(
                    create_tco_heatmap(
                        [s['vehicle'] for s in scored_vehicles],
                        [s['tco'] for s in scored_vehicles]
                    ),
                    use_container_width=True
                )
    
    # ==================== TAB 3: COMPARISON CHARTS ====================
    with tab3:
        st.header("📊 Vehicle Comparison Charts")
        
        if not scored_vehicles:
            st.warning("No vehicles to compare. Adjust your filters.")
        else:
            # Radar chart
            st.subheader("🎯 Category Comparison (Top 5)")
            st.plotly_chart(
                create_vehicle_comparison_radar(
                    [s['vehicle'] for s in scored_vehicles[:5]],
                    [s['score'] for s in scored_vehicles[:5]]
                ),
                use_container_width=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price vs Range
                st.plotly_chart(
                    create_price_range_chart(
                        [s['vehicle'] for s in scored_vehicles],
                        preferences
                    ),
                    use_container_width=True
                )
            
            with col2:
                # Brand distribution
                st.plotly_chart(
                    create_brand_distribution([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Efficiency comparison
                st.plotly_chart(
                    create_efficiency_comparison([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            with col2:
                # Charging speed
                st.plotly_chart(
                    create_charging_speed_chart([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Performance scatter
                st.plotly_chart(
                    create_performance_scatter([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
            
            with col2:
                # Range vs Battery
                st.plotly_chart(
                    create_range_battery_scatter([s['vehicle'] for s in scored_vehicles]),
                    use_container_width=True
                )
    
    # ==================== TAB 4: COST ANALYSIS ====================
    with tab4:
        st.header("💰 Total Cost of Ownership Analysis")
        
        if not scored_vehicles:
            st.warning("No vehicles to analyze. Adjust your filters.")
        else:
            # TCO comparison
            st.plotly_chart(
                create_tco_comparison_chart(
                    [s['vehicle'] for s in scored_vehicles[:10]],
                    [s['tco'] for s in scored_vehicles[:10]]
                ),
                use_container_width=True
            )
            
            # Savings chart
            st.plotly_chart(
                create_savings_chart([s['tco'] for s in scored_vehicles[:10]]),
                use_container_width=True
            )
            
            # Detailed breakdown for selected vehicle
            st.subheader("📋 Detailed TCO Breakdown")
            
            vehicle_names = [s['vehicle']['name'] for s in scored_vehicles[:15]]
            selected_vehicle = st.selectbox("Select Vehicle for Details", vehicle_names)
            
            selected_idx = vehicle_names.index(selected_vehicle)
            selected_tco = scored_vehicles[selected_idx]['tco']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(
                    create_tco_breakdown_pie(selected_tco),
                    use_container_width=True
                )
            
            with col2:
                st.markdown("### 💵 Cost Details")
                
                st.write(f"**Purchase Price:** €{selected_tco.purchase_price:,.0f}")
                st.write(f"**Incentives:** -€{selected_tco.incentives_total:,.0f}")
                st.write(f"**Net Price:** €{selected_tco.net_purchase_price:,.0f}")
                
                st.divider()
                
                st.write(f"**Annual Fuel Cost:** €{selected_tco.annual_fuel_cost:,.0f}")
                st.write(f"**Annual Maintenance:** €{selected_tco.annual_maintenance_cost:,.0f}")
                st.write(f"**Annual Insurance:** €{selected_tco.annual_insurance_cost:,.0f}")
                st.write(f"**Annual Registration:** €{selected_tco.annual_registration_cost:,.0f}")
                
                st.divider()
                
                st.write(f"**{ownership_years}-Year TCO:** €{selected_tco.total_cost_of_ownership:,.0f}")
                st.write(f"**Cost per km:** €{selected_tco.cost_per_km:.3f}")
                
                if selected_tco.savings_vs_avg_ice > 0:
                    st.success(f"💰 Saves €{selected_tco.savings_vs_avg_ice:,.0f} vs average gas car!")
                else:
                    st.info(f"Costs €{abs(selected_tco.savings_vs_avg_ice):,.0f} more than avg gas car")
    
    # ==================== TAB 5: ALL VEHICLES ====================
    with tab5:
        st.header("📋 All Matching Vehicles")
        
        if not scored_vehicles:
            st.warning("No vehicles match your criteria.")
        else:
            st.write(f"**{len(scored_vehicles)} vehicles** match your criteria")
            
            # Create comparison table
            df = create_specs_comparison_table([s['vehicle'] for s in scored_vehicles])
            
            # Add score and TCO columns
            df['Score'] = [s['score']['final_score'] for s in scored_vehicles]
            df['Net Price'] = [f"€{s['tco'].net_purchase_price:,.0f}" for s in scored_vehicles]
            df[f'{ownership_years}Y TCO'] = [f"€{s['tco'].total_cost_of_ownership:,.0f}" for s in scored_vehicles]
            
            st.dataframe(
                df,
                use_container_width=True,
                height=600
            )
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download as CSV",
                csv,
                "ev_comparison.csv",
                "text/csv"
            )
    
    # ==================== TAB 6: VEHICLE DETAILS ====================
    with tab6:
        st.header("🔍 Vehicle Details")
        
        if not scored_vehicles:
            st.warning("No vehicles available.")
        else:
            # Vehicle selector
            vehicle_names = [s['vehicle']['name'] for s in scored_vehicles]
            selected = st.selectbox("Select a Vehicle", vehicle_names, key="detail_select")
            
            selected_idx = vehicle_names.index(selected)
            v = scored_vehicles[selected_idx]['vehicle']
            score = scored_vehicles[selected_idx]['score']
            tco = scored_vehicles[selected_idx]['tco']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{v['name']}")
                st.write(f"**Brand:** {v['brand']}")
                st.write(f"**Type:** {v['powertrain']} {v['vehicle_type'].upper()}")
                st.write(f"**Year:** {v['year']}")
                
                st.divider()
                st.markdown("### 💰 Pricing")
                st.write(f"**Base Price:** €{v['base_price']:,}")
                st.write(f"**Incentives:** -€{tco.incentives_total:,}")
                st.write(f"**Net Price:** €{tco.net_purchase_price:,}")
                
                st.divider()
                st.markdown("### 🔋 Battery & Range")
                st.write(f"**Range:** {v['range_km']} km")
                st.write(f"**Battery:** {v['battery_kwh']} kWh")
                st.write(f"**Efficiency:** {v['kwh_per_100km']} kWh/100km")
                st.write(f"**DC Charging:** {v['dc_charging_kw']} kW")
            
            with col2:
                st.markdown("### 🏎️ Performance")
                st.write(f"**0-100 km/h:** {v['zero_to_100_kmh']} seconds")
                st.write(f"**Top Speed:** {v['top_speed_kmh']} km/h")
                st.write(f"**Horsepower:** {v['horsepower']} HP")
                st.write(f"**Torque:** {v['torque_nm']} Nm")
                st.write(f"**AWD:** {'Yes ✓' if v.get('awd') else 'No'}")
                
                st.divider()
                st.markdown("### 📦 Practicality")
                st.write(f"**Seats:** {v['seats']}")
                st.write(f"**Cargo:** {v['cargo_liters']} L")
                st.write(f"**Towing:** {v.get('towing_capacity_kg', 0)} kg")
                st.write(f"**Ground Clearance:** {v.get('ground_clearance_mm', 'N/A')} mm")
                
                st.divider()
                st.markdown("### ✨ Features")
                features = []
                if v.get('autopilot_available'):
                    features.append("🤖 Autopilot")
                if v.get('ota_updates'):
                    features.append("📡 OTA Updates")
                if v.get('heat_pump'):
                    features.append("♨️ Heat Pump")
                if v.get('v2l_capable'):
                    features.append("🔌 V2L")
                if v.get('v2h_capable'):
                    features.append("🏠 V2H")
                if v.get('frunk_liters', 0) > 0:
                    features.append(f"📦 Frunk ({v['frunk_liters']}L)")
                
                st.write(" | ".join(features) if features else "Standard features")
            
            # Score breakdown
            st.divider()
            st.subheader(f"📊 Match Score: {score['final_score']:.0f}/100")
            
            score_df = pd.DataFrame(
                list(score['category_scores'].items()),
                columns=['Category', 'Score']
            )
            
            fig = px.bar(
                score_df,
                x='Category',
                y='Score',
                color='Score',
                color_continuous_scale='Viridis',
                title='Category Scores (out of 10)'
            )
            fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.divider()
    st.markdown("""
        <div class="footer">
            <p>🚗 EV/PHEV Selection Tool | Built with Streamlit & Plotly</p>
            <p>Data is for demonstration purposes. Always verify with official sources before purchasing.</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
