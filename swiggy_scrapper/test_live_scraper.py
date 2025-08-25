#!/usr/bin/env python3
"""
Test script for live scraper functionality (coordinate-driven only)
"""

import sys
import pandas as pd
from scraper.live_scraper import get_restaurants_with_menus

def test_live_scraper():
    """Test the live scraper with different coordinates"""
    
    # Test coordinates (user can change these to any Swiggy-linked location)
    test_coords = [
        (12.9716, 77.5946),  # Example: Bangalore
        (13.0827, 80.2707),  # Example: Chennai
        (19.0760, 72.8777),  # Example: Mumbai
    ]
    
    print("🧪 Testing Live Scraper Functionality (coordinate-driven)")
    print("=" * 50)
    
    for lat, lng in test_coords:
        print(f"\n📍 Testing coordinates (lat={lat}, lng={lng})")
        print("-" * 30)
        try:
            restaurants_df, _ = get_restaurants_with_menus(
                lat=lat,
                lng=lng,
                max_restaurants=3,
                include_menus=False
            )
            if not restaurants_df.empty:
                print(f"✅ Found {len(restaurants_df)} restaurants at ({lat}, {lng})")
                for idx, restaurant in restaurants_df.iterrows():
                    print(f"   {idx+1}. {restaurant['name']} - {restaurant['area']}")
            else:
                print(f"❌ No restaurants found at ({lat}, {lng})")
        except Exception as e:
            print(f"❌ Error testing ({lat}, {lng}): {str(e)}")
    print("\n" + "=" * 50)
    print("✅ Live scraper test completed!")
    print("\nTo use the live scraper:")
    print("1. Interactive Dashboard: streamlit run dashboard.py")
    print("2. Command Line: python live_scraper_cli.py --lat 12.9716 --lng 77.5946")
    print("3. Python API: from scraper.live_scraper import get_restaurants_with_menus")

if __name__ == "__main__":
    test_live_scraper() 