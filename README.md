# 🍽️ Live Swiggy Restaurant Scraper

A Python-based web scraper for Swiggy restaurant and menu data. **Just provide latitude and longitude** to get restaurants for any location.

## 📋 Features

- **Live scraping**: Enter any lat/lon coordinates
- **Batch scraping**: Use lat/lon for any location
- **No city or grid logic**: Only coordinates required
- **Menu scraping**: Optional, for each restaurant
- **Data storage**: Saves results to CSV files (optional)
- **Dashboard**: Streamlit interface for browsing scraped data
- **Rate-limited requests**: Respectful scraping with delays

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Live Scraping (Recommended)

#### 1. Interactive Dashboard
```bash
streamlit run dashboard.py
```
- Enter latitude and longitude coordinates
- Click "Search Restaurants" for live results
- Use filters to narrow down results

#### 2. Command Line Interface
```bash
python live_scraper_cli.py --lat 12.9716 --lng 77.5946 --max-restaurants 10
```

#### 3. Python API
```python
from scraper.live_scraper import get_restaurants_with_menus

restaurants_df, menus_df = get_restaurants_with_menus(
    lat=12.9716,  # Latitude
    lng=77.5946,  # Longitude
    max_restaurants=50,
    include_menus=True
)
```

### Batch Scraping (Lat/Lng Only)

#### 1. Batch Scraper
```bash
python batch_scraper.py --lat 12.9716 --lng 77.5946 --max-restaurants 20
```

#### 2. Main Script (also lat/lng only)
```bash
python main.py --lat 12.9716 --lng 77.5946 --max-restaurants 20
```

#### 3. View Dashboard
```bash
streamlit run dashboard.py
```

## 📍 Example Usage

- Use the coordinates of any Swiggy-linked restaurant or delivery area for best results.
- If you get 0 results, try a nearby coordinate or a more central location.
- This tool is 100% coordinate-driven—no city or area selection required.

## 🔧 Configuration

### Configuration File (scraper/config.py)
The configuration is now flexible and supports any location:

```python
# Only coordinates required
DEFAULT_LAT = "12.9716"  # Example default
DEFAULT_LNG = "77.5946"  # Example default

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36..."
}

REQUEST_DELAY = 0.5  # seconds between requests
REQUEST_TIMEOUT = 10  # seconds timeout for requests
RESTAURANT_API_URL = "https://www.swiggy.com/dapi/restaurants/list/v5"
MENU_API_URL = "https://www.swiggy.com/dapi/menu/pl"
```

## 📊 Data Structure

### Restaurant Data
```python
{
    'id': 'restaurant_id',
    'name': 'Restaurant Name',
    'cuisines': 'North Indian, Chinese',
    'area': 'Area Name',
    'rating': 4.2,
    'delivery_time': 30,
    'cost_for_two': '₹400 for two',
    'address': 'Locality',
    'restaurant_type': 'Restaurant Type',
    'lat': 12.9716,
    'lng': 77.5946
}
```

### Menu Data
```python
{
    'restaurant_id': 'restaurant_id',
    'restaurant_name': 'Restaurant Name',
    'item_name': 'Dish Name',
    'price': 150.0,
    'veg': 'Veg',
    'category': 'Main Course',
    'description': 'Dish description'
}
```

## ⚠️ Notes
- **No city or grid logic**: Just provide lat/lon for any location
- **If no restaurants are found**: Try a nearby coordinate or a more central location
- **Respect Swiggy's terms of service**

## 🙏 Acknowledgments
- Built with Python, Streamlit, and pandas
- Uses Swiggy's unofficial API 
