import requests
import pandas as pd
import time
from scraper.config import headers, REQUEST_DELAY, REQUEST_TIMEOUT, MENU_API_URL, DEFAULT_LAT, DEFAULT_LNG

def validate_menu_response(data, rest_id, rest_name):
    if not isinstance(data, dict):
        print(f"[WARNING] Unexpected menu response type for {rest_name} (ID: {rest_id})")
        return False
    if "data" not in data or "cards" not in data["data"]:
        print(f"[WARNING] Missing 'data' or 'cards' in menu response for {rest_name} (ID: {rest_id})")
        return False
    return True

def fetch_all_menus(restaurant_csv='data/coimbatore_restaurants.csv', lat=None, lng=None):
    """
    Fetch menus for all restaurants in a CSV file
    
    Args:
        restaurant_csv (str): Path to restaurant CSV file
        lat, lng (float): Coordinates for menu fetching (uses restaurant coordinates if None)
    """
    df = pd.read_csv(restaurant_csv)
    menu_data = []

    for i, row in df.iterrows():
        rest_id = row['id']
        rest_name = row['name']
        
        # Use provided coordinates or restaurant coordinates
        menu_lat = lat if lat is not None else row.get('lat', DEFAULT_LAT)
        menu_lng = lng if lng is not None else row.get('lng', DEFAULT_LNG)

        url = f"{MENU_API_URL}?page-type=REGULAR_MENU&complete-menu=true&lat={menu_lat}&lng={menu_lng}&restaurantId={rest_id}"
        
        try:
            res = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

            if res.status_code != 200:
                print(f"Failed to fetch menu for {rest_name} (ID: {rest_id}) - Status: {res.status_code}")
                continue

            data = res.json()
            if not validate_menu_response(data, rest_id, rest_name):
                print(f"  [WARNING] Menu API structure changed or error for {rest_name} (ID: {rest_id})")
                continue
            cards = data.get('data', {}).get('cards', [])
            for card in cards:
                if 'groupedCard' in card:
                    regular_cards = card['groupedCard']['cardGroupMap']['REGULAR']['cards']
                    for section in regular_cards:
                        try:
                            item_cards = section['card']['card'].get('itemCards', [])
                            for item in item_cards:
                                info = item['card']['info']
                                menu_data.append({
                                    'restaurant_id': rest_id,
                                    'restaurant_name': rest_name,
                                    'item_name': info.get('name'),
                                    'price': (info.get('price') or info.get('defaultPrice', 0)) / 100,
                                    'veg': 'Veg' if info.get('isVeg') == 1 else 'Non-Veg',
                                    'category': info.get('category', ''),
                                    'description': info.get('description', '')
                                })
                        except Exception as e:
                            print(f"Error processing menu section for {rest_name}: {e}")
                            continue
            print(f"[{i+1}/{len(df)}] Done: {rest_name}")
            time.sleep(REQUEST_DELAY)
        except requests.exceptions.RequestException as e:
            print(f"Network error for {rest_name}: {e}")
            continue
        except Exception as e:
            print(f"Error for {rest_name}: {e}")
            continue

    df_menu = pd.DataFrame(menu_data)
    output_file = restaurant_csv.replace('_restaurants.csv', '_menus.csv')
    df_menu.to_csv(output_file, index=False)
    print(f"Saved {len(df_menu)} menu items to {output_file}")
    return df_menu
