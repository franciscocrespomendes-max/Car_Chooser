import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://ev-database.org/"
LIST_URL = BASE_URL + "carlist.php"


def fetch_ev_list():
    resp = requests.get(LIST_URL)
    resp.raise_for_status()
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

    SYMBOLS = {"BEV": "🔋", "PHEV": "🔌"}

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
        if ptype and ptype in SYMBOLS:
            car_name = f"{SYMBOLS[ptype]} {car_name}"
        cars.append({"name": car_name, "url": car_url, "powertrain": ptype})
    return cars


def fetch_ev_details(car):
    resp = requests.get(car["url"])
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    specs = {}
    # Example: extract some basic specs
    for row in soup.select(".specs tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.text.strip()
            val = td.text.strip()
            specs[key] = val
    car["specs"] = specs
    return car


def main():
    print("Fetching EV list...")
    cars = fetch_ev_list()
    print(f"Found {len(cars)} vehicles. Fetching details (this may take a while)...")
    detailed = []
    for i, car in enumerate(cars):
        try:
            detailed.append(fetch_ev_details(car))
            print(f"[{i+1}/{len(cars)}] {car['name']}")
        except Exception as e:
            print(f"Error fetching {car['name']}: {e}")
    with open("evdb_sync.json", "w", encoding="utf-8") as f:
        json.dump(detailed, f, ensure_ascii=False, indent=2)
    print("Done. Data saved to evdb_sync.json.")

if __name__ == "__main__":
    main()
