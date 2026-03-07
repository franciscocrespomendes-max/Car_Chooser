# EV Database Scraper Integration Guide

## Overview
The Car Chooser project now integrates with `evdb_scraper.py` to fetch and manage vehicle data from the EV database.

## Current Setup ✅

### Data Flow
```
evdb_scraper.py → evdb_sync.json → streamlit_app.py
                     (78 vehicles)
```

### What's Included
- **78 Electric Vehicles** across 28 brands
- **2 Powertrain Types**: EV (Battery Electric) and PHEV (Plug-in Hybrid)
- **36+ Data Fields** per vehicle including:
  - Performance specs (0-100 km/h, top speed, horsepower, torque)
  - Range, battery capacity, charging power
  - Dimensions, weight, ground clearance
  - Features (autopilot, OTA updates, V2L/V2H capability)
  - Pricing and reliability scores

### Vehicles by Brand

| Brand | Count | Brand | Count |
|-------|-------|-------|-------|
| Tesla | 6 | Hyundai | 5 |
| Volvo | 6 | Kia | 5 |
| BMW | 5 | Volkswagen | 5 |
| Chevrolet | 5 | Ford | 5 |
| Mercedes-Benz | 3 | Nissan | 3 |
| Polestar | 3 | Porsche | 4 |
| Genesis | 2 | Lucid | 2 |
| Rivian | 2 | Lexus | 2 |
| Jeep | 2 | BYD | 2 |
| Toyota | 2 | Volvo (PHEV) | 2 |
| Other* | 10 | | |

*Honda, Mazda, Subaru, Nissan, Renault, Peugeot, MG, NIO, XPeng, Ora

## Using the Scraper

### Update Vehicle Data
```bash
python evdb_scraper.py
```

This will:
1. Attempt to fetch live data from ev-database.org
2. Extract detailed specifications for each vehicle
3. Save to `evdb_sync.json` with enhanced data
4. Fall back to local cache if website is unavailable

### Run the Streamlit App
```bash
streamlit run streamlit_app.py
```

The app automatically:
- ✅ Loads from `evdb_sync.json` if available
- ✅ Falls back to hardcoded data if needed
- ✅ Displays source in the sidebar
- ✅ Provides vehicle comparison tools with all specs

## Scraper Features

### Improved Robustness
- Proper HTTP headers to avoid blocking
- Timeout handling
- Graceful fallback to local data
- Server-respectful rate limiting (1s between requests)

### Data Functions Available
```python
from evdb_scraper import (
    fetch_ev_list,           # Get list of EVs from website
    fetch_ev_details,        # Get detailed specs for a vehicle
    fetch_from_local_json,   # Load from evdb_sync.json
)
```

## File Structure

```
Car_Chooser/
├── evdb_scraper.py       → Data collection script
├── evdb_sync.json        → Current vehicle database (78 vehicles)
├── streamlit_app.py      → Main application
└── SCRAPER_GUIDE.md      → This file
```

## Data Specifications

### Sample Vehicle Record
```json
{
  "id": "tesla_model_3_sr",
  "name": "Tesla Model 3 Standard Range",
  "brand": "Tesla",
  "powertrain": "EV",
  "vehicle_type": "sedan",
  "year": 2024,
  "base_price": 40240,
  "range_km": 438,
  "battery_kwh": 60,
  "dc_charging_kw": 170,
  "zero_to_100_kmh": 6.1,
  "top_speed_kmh": 201,
  "horsepower": 271,
  "torque_nm": 420,
  ...
}
```

## Troubleshooting

### Scraper returns no data
- Check internet connection
- Website may be down or changed structure
- Data automatically falls back to `evdb_sync.json`

### App shows "Built-in vehicles"
- `evdb_sync.json` is missing or empty
- Run `python evdb_scraper.py` to generate it
- App uses 100+ hardcoded vehicles as fallback

### 403 Forbidden Error
- Already handled by the scraper
- Automatic fallback to local cache
- Consider waiting before retrying

## Next Steps

1. **Update Data**: Run `python evdb_scraper.py` periodically
2. **Extend Data**: Add custom fields to vehicle records
3. **Export Data**: Use `evdb_sync.json` for other projects
4. **Schedule Updates**: Set up cron job for automatic updates

---
Last Updated: March 7, 2026
Data Source: ev-database.org via evdb_scraper.py
