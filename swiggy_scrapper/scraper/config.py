# Default coordinates (can be overridden by user input)
DEFAULT_LAT = "19.0760"  # Mumbai latitude (example default)
DEFAULT_LNG = "72.8777"  # Mumbai longitude (example default)

# Request headers for Swiggy API
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}

# Rate limiting settings
REQUEST_DELAY = 0.5  # seconds between requests
REQUEST_TIMEOUT = 10  # seconds timeout for requests

# API endpoints
RESTAURANT_API_URL = "https://www.swiggy.com/dapi/restaurants/list/v5"
MENU_API_URL = "https://www.swiggy.com/dapi/menu/pl"

# Default scraping settings
DEFAULT_MAX_RESTAURANTS = 50
DEFAULT_INCLUDE_MENUS = True