import argparse
from scraper.live_scraper import scrape_restaurants_by_location, scrape_menu_for_restaurant
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Swiggy Restaurant Scraper (Lat/Lng Only)')
    parser.add_argument('--lat', type=float, required=True, help='Latitude coordinate')
    parser.add_argument('--lng', type=float, required=True, help='Longitude coordinate')
    parser.add_argument('--max-restaurants', type=int, default=50, help='Maximum number of restaurants to fetch')
    parser.add_argument('--no-menus', action='store_true', help='Skip menu scraping')
    args = parser.parse_args()

    print(f"Fetching restaurants for lat={args.lat}, lng={args.lng} ...")
    restaurants_df = scrape_restaurants_by_location(args.lat, args.lng, max_restaurants=args.max_restaurants)
    if restaurants_df.empty:
        print("No restaurants found for this location.")
        return
    restaurants_df.to_csv("restaurants.csv", index=False)
    print(f"Saved {len(restaurants_df)} restaurants to restaurants.csv")

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
            menus_df.to_csv("menus.csv", index=False)
            print(f"Saved {len(menus_df)} menu items to menus.csv")
        else:
            print("No menu items found.")
    else:
        print("Menu scraping skipped.")

if __name__ == "__main__":
    main()