import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict

BASE_URL = "https://ev-database.org/"
LIST_URL = BASE_URL + "carlist.php"

# HTTP headers to avoid 403 Forbidden
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def fetch_ev_list() -> List[Dict]:
    """Fetch the list of electric vehicles from ev-database.org"""
    try:
        resp = requests.get(LIST_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch EV list: {e}")
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    cars = []
    
    def detect_powertrain(row):
        """Try to detect whether the row represents a BEV or PHEV.
        Returns 'BEV', 'PHEV' or None.
        """
        # look for images/icons with alt/title text
        for img in row.select("img"):
            for attr in ("alt", "title", "class"):
                txt = img.get(attr)
                if not txt:
                    continue
                txt = str(txt).lower()
                if "plug" in txt or "phev" in txt or "plugin" in txt or "plug-in" in txt:
                    return "PHEV"
                if "battery" in txt or "bev" in txt or "electric" in txt:
                    return "BEV"
        # fallback: search the row text for keywords
        txt = row.get_text(separator=" ").lower()
        if "plug-in" in txt or "phev" in txt or "plug in" in txt:
            return "PHEV"
        if "battery" in txt or "bev" in txt or "electric" in txt:
            return "BEV"
        return None

    for row in soup.select("#evdb-table tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        link = cols[1].find("a")
        if not link:
            continue
        car_url = BASE_URL + link['href']
        car_name = link.text.strip()
        ptype = detect_powertrain(row)
        cars.append({"name": car_name, "url": car_url, "powertrain": ptype})
    
    return cars


def fetch_ev_details(car: Dict) -> Dict:
    """Fetch detailed specifications for a single EV"""
    try:
        resp = requests.get(car["url"], headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch details for {car['name']}: {e}")
        return car
    
    soup = BeautifulSoup(resp.text, "html.parser")
    specs = {}
    
    # Extract specs from various table structures
    for row in soup.select(".specs tr, table tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.text.strip()
            val = td.text.strip()
            if key and val:
                specs[key] = val
    
    car["specs"] = specs
    time.sleep(1)  # Be respectful to the server
    return car


def fetch_from_local_json(filename: str = "evdb_sync.json") -> List[Dict]:
    """Load vehicle data from local JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Local file {filename} not found")
        return []


def main():
    print("Fetching EV list...")
    cars = fetch_ev_list()
    
    if not cars:
        print("Failed to fetch from website, attempting to load from local data...")
        cars = fetch_from_local_json()
        if cars:
            print(f"Loaded {len(cars)} vehicles from local cache")
        else:
            print("No data available")
            return
    
    print(f"Found {len(cars)} vehicles. Fetching details (this may take a while)...")
    detailed = []
    for i, car in enumerate(cars):
        try:
            detailed.append(fetch_ev_details(car))
            print(f"[{i+1}/{len(cars)}] {car['name']}")
        except Exception as e:
            print(f"Error fetching {car['name']}: {e}")
            detailed.append(car)
    
    with open("evdb_sync.json", "w", encoding="utf-8") as f:
        json.dump(detailed, f, ensure_ascii=False, indent=2)
    print(f"Done. Data saved to evdb_sync.json ({len(detailed)} vehicles).")


if __name__ == "__main__":
    main()
