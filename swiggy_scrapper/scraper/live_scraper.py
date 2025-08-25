import requests
import pandas as pd
import time
from scraper.config import headers

def validate_restaurant_response(data, lat, lng, offset):
    """Validate the API response structure. Returns (is_valid, is_unserviceable)"""
    if not isinstance(data, dict):
        print(f"[WARNING] Unexpected response type at lat={lat}, lng={lng}, offset={offset}")
        return False, False
    if "data" not in data or "cards" not in data["data"]:
        print(f"[WARNING] Missing 'data' or 'cards' in response at lat={lat}, lng={lng}, offset={offset}")
        return False, False
    # Check for swiggy_not_present card
    for card in data["data"].get("cards", []):
        try:
            card_data = card['card']['card']
            if card_data.get('id') == 'swiggy_not_present':
                print(f"[INFO] Swiggy not present at lat={lat}, lng={lng}")
                return False, True
        except Exception:
            continue
    return True, False

def scrape_restaurants_by_location(lat, lng, max_restaurants=100, smart_search=False, grid_steps=[0.001, -0.001, 0.002, -0.002]):
    """
    Live scrape restaurants for a specific location. If smart_search is True and no restaurants are found,
    try a small grid around the input coordinates.
    Returns (DataFrame, is_unserviceable: bool, elapsed_time: float)
    """
    start_time = time.time()
    def _scrape(lat, lng):
        print(f"Scraping restaurants for location: lat={lat}, lng={lng}")
        all_restaurants = []
        offset = 0
        is_unserviceable = False
        while len(all_restaurants) < max_restaurants:
            url = f"https://www.swiggy.com/dapi/restaurants/list/v5?lat={lat}&lng={lng}&offset={offset}&sortBy=RELEVANCE&page_type=DESKTOP_WEB_LISTING"
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code != 200:
                    print(f"Failed to fetch data at offset {offset} (Status: {res.status_code})")
                    break
                data = res.json()
                is_valid, is_unserviceable = validate_restaurant_response(data, lat, lng, offset)
                if is_unserviceable:
                    return pd.DataFrame(), True
                if not is_valid:
                    print(f"Invalid response structure at offset {offset}")
                    break
                cards = data.get("data", {}).get("cards", [])
                found_new = False
                for card in cards:
                    try:
                        card_data = card['card']['card']
                        if card_data.get('id') == 'restaurant_grid_listing_v2':
                            restaurants = card_data['gridElements']['infoWithStyle']['restaurants']
                            print(f"Page at offset {offset} returned {len(restaurants)} restaurants")  # DEBUG
                            for r in restaurants:
                                if len(all_restaurants) >= max_restaurants:
                                    break
                                info = r['info']
                                restaurant_data = {
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
                                }
                                existing_ids = [r['id'] for r in all_restaurants]
                                if info['id'] not in existing_ids:
                                    all_restaurants.append(restaurant_data)
                                    found_new = True
                            print(f"Collected restaurant IDs so far: {[r['id'] for r in all_restaurants]}")  # DEBUG
                    except Exception as e:
                        print(f"Error processing restaurant card: {e}")
                        continue
                if not found_new:
                    print(f"No new restaurants found at offset {offset}")
                    break
                offset += 16
                time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                print(f"Network error at offset {offset}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error at offset {offset}: {e}")
                break
        df = pd.DataFrame(all_restaurants)
        print(f"Found {len(df)} restaurants for location lat={lat}, lng={lng}")
        return df, is_unserviceable

    # Strict search first
    df, is_unserviceable = _scrape(lat, lng)
    if not smart_search or not df.empty or is_unserviceable:
        elapsed = time.time() - start_time
        return df, is_unserviceable, elapsed
    # Smart search: try a grid around the input
    print("No restaurants found. Trying smart search (grid around input coordinates)...")
    tried = set()
    for dlat in grid_steps:
        for dlng in grid_steps:
            nlat = round(lat + dlat, 6)
            nlng = round(lng + dlng, 6)
            if (nlat, nlng) == (lat, lng) or (nlat, nlng) in tried:
                continue
            tried.add((nlat, nlng))
            df2, is_unserviceable2 = _scrape(nlat, nlng)
            if is_unserviceable2:
                elapsed = time.time() - start_time
                return df2, True, elapsed
            if not df2.empty:
                print(f"Smart search found restaurants at lat={nlat}, lng={nlng}")
                elapsed = time.time() - start_time
                return df2, False, elapsed
    print("Smart search did not find any restaurants nearby.")
    elapsed = time.time() - start_time
    return df, False, elapsed

def scrape_menu_for_restaurant(restaurant_id, lat, lng):
    """
    Scrape menu for a specific restaurant
    
    Args:
        restaurant_id (str): Restaurant ID
        lat (float): Latitude coordinate
        lng (float): Longitude coordinate
    
    Returns:
        pandas.DataFrame: DataFrame containing menu items
    """
    url = f"https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat={lat}&lng={lng}&restaurantId={restaurant_id}"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"Failed to fetch menu for restaurant {restaurant_id}")
            return pd.DataFrame()
            
        data = res.json()
        if not validate_restaurant_response(data, lat, lng, 0):
            print(f"Invalid menu response structure for restaurant {restaurant_id}")
            return pd.DataFrame()
            
        menu_items = []
        cards = data.get('data', {}).get('cards', [])
        
        for card in cards:
            if 'groupedCard' in card:
                try:
                    regular_cards = card['groupedCard']['cardGroupMap']['REGULAR']['cards']
                    for section in regular_cards:
                        item_cards = section['card']['card'].get('itemCards', [])
                        for item in item_cards:
                            info = item['card']['info']
                            menu_items.append({
                                'restaurant_id': restaurant_id,
                                'item_name': info.get('name'),
                                'price': (info.get('price') or info.get('defaultPrice', 0)) / 100,
                                'veg': 'Veg' if info.get('isVeg') == 1 else 'Non-Veg',
                                'category': info.get('category', ''),
                                'description': info.get('description', '')
                            })
                except Exception as e:
                    print(f"Error processing menu section: {e}")
                    continue
        
        df = pd.DataFrame(menu_items)
        print(f"Found {len(df)} menu items for restaurant {restaurant_id}")
        return df
        
    except Exception as e:
        print(f"Error fetching menu for restaurant {restaurant_id}: {e}")
        return pd.DataFrame()

def get_restaurants_with_menus(lat, lng, max_restaurants=50, include_menus=True):
    """
    Get restaurants with optional menu data for a specific location
    
    Args:
        lat (float): Latitude coordinate
        lng (float): Longitude coordinate
        max_restaurants (int): Maximum number of restaurants to fetch
        include_menus (bool): Whether to include menu data
    
    Returns:
        tuple: (restaurants_df, menus_df)
    """
    # Scrape restaurants
    restaurants_df, is_unserviceable, elapsed = scrape_restaurants_by_location(lat, lng, max_restaurants)
    
    if restaurants_df.empty or is_unserviceable:
        return restaurants_df, pd.DataFrame()
    
    # Scrape menus if requested
    menus_df = pd.DataFrame()
    if include_menus:
        all_menus = []
        for idx, restaurant in restaurants_df.iterrows():
            print(f"Fetching menu for {restaurant['name']} ({idx+1}/{len(restaurants_df)})")
            menu_df = scrape_menu_for_restaurant(restaurant['id'], lat, lng)
            if not menu_df.empty:
                menu_df['restaurant_name'] = restaurant['name']
                all_menus.append(menu_df)
            time.sleep(0.5)  # Rate limiting
        
        if all_menus:
            menus_df = pd.concat(all_menus, ignore_index=True)
    
    return restaurants_df, menus_df 