import numpy as np
import requests
import pandas as pd
import time
from scraper.config import headers, REQUEST_DELAY, REQUEST_TIMEOUT, RESTAURANT_API_URL
import json

def generate_grid(min_lat, max_lat, min_lng, max_lng, step=0.005):
    lats = np.arange(min_lat, max_lat, step)
    lngs = np.arange(min_lng, max_lng, step)
    return [(round(lat, 6), round(lng, 6)) for lat in lats for lng in lngs]

def validate_restaurant_response(data, lat, lng, offset):
    if not isinstance(data, dict):
        print(f"[WARNING] Unexpected response type at lat={lat}, lng={lng}, offset={offset}")
        with open("debug_sw_res.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return False
    # More robust: check if 'data' exists and 'cards' is a list (can be empty)
    if "data" not in data or not isinstance(data["data"], dict):
        print(f"[WARNING] Missing or invalid 'data' in response at lat={lat}, lng={lng}, offset={offset}")
        with open("debug_sw_res.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return False
    cards = data["data"].get("cards", None)
    if cards is None or not isinstance(cards, list):
        print(f"[WARNING] Missing or invalid 'cards' in response at lat={lat}, lng={lng}, offset={offset}")
        with open("debug_sw_res.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return False
    return True

def fetch_restaurants_by_area(city_name="Coimbatore", min_lat=10.88, max_lat=11.15, min_lng=76.85, max_lng=77.10):
    """
    Fetch all restaurants in a specified area using grid-based scraping
    
    Args:
        city_name (str): Name of the city for output file naming
        min_lat, max_lat, min_lng, max_lng (float): Bounding box coordinates
    """
    grid_points = generate_grid(min_lat, max_lat, min_lng, max_lng, step=0.005)
    print(f"Sweeping {len(grid_points)} locations across {city_name}...")

    all_restaurants = []
    seen_ids = set()
    for idx, (lat, lng) in enumerate(grid_points):
        offset = 0
        print(f"[{idx+1}/{len(grid_points)}] Fetching for lat={lat}, lng={lng}")
        while True:
            url = f"{RESTAURANT_API_URL}?lat={lat}&lng={lng}&offset={offset}&sortBy=RELEVANCE&page_type=DESKTOP_WEB_LISTING"
            try:
                res = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                if res.status_code != 200:
                    print(f"  Failed at offset {offset} (Status: {res.status_code})")
                    break
                data = res.json()
                if not validate_restaurant_response(data, lat, lng, offset):
                    print(f"  [WARNING] API structure changed or error at lat={lat}, lng={lng}, offset={offset}")
                    break
                cards = data.get("data", {}).get("cards", [])
                found = False
                for card in cards:
                    try:
                        card_data = card['card']['card']
                        if card_data.get('id') == 'restaurant_grid_listing_v2':
                            restaurants = card_data['gridElements']['infoWithStyle']['restaurants']
                            for r in restaurants:
                                info = r['info']
                                if info['id'] not in seen_ids:
                                    found = True
                                    seen_ids.add(info['id'])
                                    all_restaurants.append({
                                        'id': info.get('id'),
                                        'name': info.get('name'),
                                        'cuisines': ", ".join(info.get('cuisines', [])),
                                        'area': info.get('areaName'),
                                        'rating': info.get('avgRating'),
                                        'delivery_time': info.get('sla', {}).get('deliveryTime'),
                                        'cost_for_two': info.get('costForTwo'),
                                        'address': info.get('locality'),
                                        'restaurant_type': info.get('restaurantType', 'N/A'),
                                        'lat': lat,
                                        'lng': lng
                                    })
                    except Exception:
                        continue
                if not found:
                    break
                offset += 16
                time.sleep(REQUEST_DELAY)
            except requests.exceptions.RequestException as e:
                print(f"  Network error at offset {offset}: {e}")
                break
            except Exception as e:
                print(f"  Unexpected error at offset {offset}: {e}")
                break
        time.sleep(REQUEST_DELAY)
    
    df = pd.DataFrame(all_restaurants)
    output_file = f"data/{city_name.lower().replace(' ', '_')}_restaurants.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} unique restaurants to {output_file}")
    return df

# Legacy function for backward compatibility
def fetch_all_restaurants():
    """Legacy function that scrapes Coimbatore area (for backward compatibility)"""
    return fetch_restaurants_by_area("Coimbatore", 10.88, 11.15, 76.85, 77.10)
