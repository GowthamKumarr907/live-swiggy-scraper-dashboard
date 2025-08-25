import requests
from scraper.config import headers
import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python test_offset_debug.py <lat> <lng> <offset>")
        sys.exit(1)
    lat = float(sys.argv[1])
    lng = float(sys.argv[2])
    offset = int(sys.argv[3])

    url = f"https://www.swiggy.com/dapi/restaurants/list/v5?lat={lat}&lng={lng}&offset={offset}&sortBy=RELEVANCE&page_type=DESKTOP_WEB_LISTING"
    print(f"Requesting Swiggy API with offset={offset}...")
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        print(f"Failed to fetch data (Status: {res.status_code})")
        sys.exit(1)
    data = res.json()
    # Find the restaurant grid card
    found = False
    for card in data.get("data", {}).get("cards", []):
        try:
            card_data = card['card']['card']
            if card_data.get('id') == 'restaurant_grid_listing_v2':
                restaurants = card_data['gridElements']['infoWithStyle']['restaurants']
                print(f"Offset {offset}: {len(restaurants)} restaurants returned.")
                print("Restaurant IDs:", [r['info']['id'] for r in restaurants])
                found = True
        except Exception:
            continue
    if not found:
        print(f"No restaurant grid found at offset {offset}.") 