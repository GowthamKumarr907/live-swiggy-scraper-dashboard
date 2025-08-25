#!/usr/bin/env python3
"""
Batch scraper for Swiggy using only latitude and longitude input. Prints results live to terminal.
"""

import argparse
from scraper.live_scraper import scrape_restaurants_by_location, scrape_menu_for_restaurant
import pandas as pd


def print_restaurants_table(df):
    if df.empty:
        print("No restaurants found.")
        return
    print("\n🏪 RESTAURANTS:")
    print("=" * 80)
    for idx, row in df.iterrows():
        print(f"{idx+1:2d}. {row['name']}")
        print(f"    📍 {row['area']} • {row['cuisines']}")
        print(f"    ⭐ Rating: {row['rating']} • 🕐 Delivery: {row['delivery_time']} min")
        print(f"    💰 Cost for two: {row['cost_for_two']}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Swiggy Batch Scraper (Lat/Lng Only, Live Output)')
    parser.add_argument('--lat', type=float, required=True, help='Latitude coordinate')
    parser.add_argument('--lng', type=float, required=True, help='Longitude coordinate')
    parser.add_argument('--max-restaurants', type=int, default=50, help='Maximum number of restaurants to fetch')
    parser.add_argument('--no-menus', action='store_true', help='Skip menu scraping')
    parser.add_argument('--output', choices=['csv', 'table'], default='table', help='Output format (default: table)')
    args = parser.parse_args()

    print(f"Batch scraping restaurants for lat={args.lat}, lng={args.lng} ...")
    restaurants_df = scrape_restaurants_by_location(args.lat, args.lng, max_restaurants=args.max_restaurants)
    if restaurants_df.empty:
        print("No restaurants found for this location.")
        return

    if args.output == 'csv':
        restaurants_df.to_csv("restaurants.csv", index=False)
        print(f"Saved {len(restaurants_df)} restaurants to restaurants.csv")
    else:
        print_restaurants_table(restaurants_df)

    if not args.no_menus:
        print("Fetching menus for each restaurant...")
        all_menus = []
        for idx, row in restaurants_df.iterrows():
            menu_df = scrape_menu_for_restaurant(row['id'], args.lat, args.lng)
            if not menu_df.empty:
                menu_df['restaurant_name'] = row['name']
                all_menus.append(menu_df)
        if all_menus:
            menus_df = pd.concat(all_menus, ignore_index=True)
            if args.output == 'csv':
                menus_df.to_csv("menus.csv", index=False)
                print(f"Saved {len(menus_df)} menu items to menus.csv")
            else:
                print("\n🍽️ MENU ITEMS:")
                print("=" * 80)
                for restaurant_name in menus_df['restaurant_name'].unique():
                    restaurant_menu = menus_df[menus_df['restaurant_name'] == restaurant_name]
                    print(f"\n📋 {restaurant_name} ({len(restaurant_menu)} items):")
                    for idx, item in restaurant_menu.head(5).iterrows():
                        print(f"    • {item['item_name']} - ₹{item['price']:.0f} ({item['veg']})")
                    if len(restaurant_menu) > 5:
                        print(f"    ... and {len(restaurant_menu) - 5} more items")
        else:
            print("No menu items found.")
    else:
        print("Menu scraping skipped.")

if __name__ == "__main__":
    main() 