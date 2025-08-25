#!/usr/bin/env python3
"""
Command-line interface for live Swiggy restaurant scraper (coordinate-driven only)
"""

import argparse
import sys
from scraper.live_scraper import scrape_restaurants_by_location, get_restaurants_with_menus
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Live Swiggy Restaurant Scraper (coordinate-driven only)')
    parser.add_argument('--lat', type=float, required=True, help='Latitude coordinate (e.g., 12.9716)')
    parser.add_argument('--lng', type=float, required=True, help='Longitude coordinate (e.g., 77.5946)')
    parser.add_argument('--max-restaurants', type=int, default=20, help='Maximum number of restaurants to fetch (default: 20)')
    parser.add_argument('--no-menus', action='store_true', help='Skip menu scraping')
    parser.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='Output format (default: table)')
    parser.add_argument('--smart-search', action='store_true', help='Try a grid around the input if no restaurants are found (smart search fallback)')
    
    args = parser.parse_args()
    
    print(f"🔍 Searching for restaurants at lat={args.lat}, lng={args.lng}")
    print(f"📊 Max restaurants: {args.max_restaurants}")
    print(f"🍽️ Include menus: {not args.no_menus}")
    print(f"🔎 Search mode: {'Smart' if args.smart_search else 'Strict'}")
    print("-" * 50)
    
    try:
        # Use the new smart_search flag
        restaurants_df, is_unserviceable, elapsed = scrape_restaurants_by_location(
            lat=args.lat,
            lng=args.lng,
            max_restaurants=args.max_restaurants,
            smart_search=args.smart_search
        )
        menus_df = None
        if is_unserviceable:
            print("🚫 Swiggy does not deliver to this location. Please try a different coordinate or a nearby city center.")
            print(f"⏱️ Live scraping time: {elapsed:.2f} seconds")
            return 1
        if not args.no_menus and not restaurants_df.empty:
            # Use the same coordinates for menu scraping
            menus_df = []
            for idx, row in restaurants_df.iterrows():
                menu_df = get_restaurants_with_menus(row['lat'], row['lng'], 1, True)[1]
                if not menu_df.empty:
                    menu_df['restaurant_name'] = row['name']
                    menus_df.append(menu_df)
            if menus_df:
                menus_df = pd.concat(menus_df, ignore_index=True)
            else:
                menus_df = pd.DataFrame()
        else:
            menus_df = pd.DataFrame()
        
        if restaurants_df.empty:
            print("❌ No restaurants found for this location. Try a nearby coordinate or check if Swiggy serves this area.")
            print(f"⏱️ Live scraping time: {elapsed:.2f} seconds")
            return 1
        
        print(f"✅ Found {len(restaurants_df)} restaurants!")
        print(f"⏱️ Live scraping time: {elapsed:.2f} seconds")
        
        if args.output == 'table':
            print("\n🏪 RESTAURANTS:")
            print("=" * 80)
            for idx, restaurant in restaurants_df.iterrows():
                print(f"{idx+1:2d}. {restaurant['name']}")
                print(f"    📍 {restaurant['area']} • {restaurant['cuisines']}")
                print(f"    ⭐ Rating: {restaurant['rating']} • 🕐 Delivery: {restaurant['delivery_time']} min")
                print(f"    💰 Cost for two: {restaurant['cost_for_two']}")
                print(f"    (lat={restaurant['lat']}, lng={restaurant['lng']})")
                print()
            if menus_df is not None and not menus_df.empty:
                print("\n🍽️ MENU ITEMS:")
                print("=" * 80)
                for restaurant_name in menus_df['restaurant_name'].unique():
                    restaurant_menu = menus_df[menus_df['restaurant_name'] == restaurant_name]
                    print(f"\n📋 {restaurant_name} ({len(restaurant_menu)} items):")
                    for idx, item in restaurant_menu.head(5).iterrows():
                        print(f"    • {item['item_name']} - ₹{item['price']:.0f} ({item['veg']})")
                    if len(restaurant_menu) > 5:
                        print(f"    ... and {len(restaurant_menu) - 5} more items")
        elif args.output == 'json':
            import json
            result = {
                'location': {'lat': args.lat, 'lng': args.lng},
                'restaurants': restaurants_df.to_dict('records'),
                'menus': menus_df.to_dict('records') if menus_df is not None and not menus_df.empty else [],
                'scraping_time_seconds': elapsed
            }
            print(json.dumps(result, indent=2))
        elif args.output == 'csv':
            restaurants_df.to_csv('restaurants.csv', index=False)
            if menus_df is not None and not menus_df.empty:
                menus_df.to_csv('menus.csv', index=False)
            print("📁 Data saved to restaurants.csv and menus.csv")
            print(f"⏱️ Live scraping time: {elapsed:.2f} seconds")
        return 0
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 