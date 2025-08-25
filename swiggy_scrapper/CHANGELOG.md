# Changelog

## [2.0.0] - 2024-01-XX - Flexible Location Support

### 🎉 Major Changes

#### Configuration Flexibility
- **Removed hardcoded Coimbatore coordinates** from `config.py`
- **Added flexible configuration** with default coordinates that can be overridden
- **Centralized API endpoints** and rate limiting settings
- **Added timeout and error handling** improvements

#### New Features
- **Live scraping for any location**: Enter any lat/lon coordinates
- **Batch scraping for multiple cities**: Predefined coordinates for major Indian cities
- **Interactive batch scraper**: Easy-to-use menu for city selection
- **Command-line flexibility**: Custom coordinates for any area

### 🔧 Technical Improvements

#### Configuration (`scraper/config.py`)
```python
# Before (hardcoded)
lat = "11.017295" # Coimbatore latitude
lng = "76.971843" # Coimbatore longitude

# After (flexible)
DEFAULT_LAT = "19.0760"  # Mumbai latitude (example default)
DEFAULT_LNG = "72.8777"  # Mumbai longitude (example default)
REQUEST_DELAY = 0.5  # seconds between requests
REQUEST_TIMEOUT = 10  # seconds timeout for requests
RESTAURANT_API_URL = "https://www.swiggy.com/dapi/restaurants/list/v5"
MENU_API_URL = "https://www.swiggy.com/dapi/menu/pl"
```

#### New Files Added
- `scraper/live_scraper.py` - Live scraping functionality
- `live_dashboard.py` - Interactive live scraping dashboard
- `live_scraper_cli.py` - Command-line interface for live scraping
- `batch_scraper.py` - Interactive batch scraper for multiple cities
- `test_live_scraper.py` - Test script for live scraping
- `README.md` - Comprehensive documentation
- `CHANGELOG.md` - This changelog

#### Updated Files
- `scraper/restaurant_list.py` - Added flexible area scraping
- `scraper/menu_scraper.py` - Improved error handling and flexibility
- `main.py` - Added command-line arguments for custom areas

### 📍 Supported Cities (Batch Scraping)
- Mumbai
- Delhi
- Bangalore
- Chennai
- Kolkata
- Hyderabad
- Pune
- Ahmedabad
- Coimbatore

### 🚀 Usage Examples

#### Live Scraping (Any Location)
```bash
# Interactive dashboard
streamlit run live_dashboard.py

# Command line
python live_scraper_cli.py --lat 19.0760 --lng 72.8777

# Python API
from scraper.live_scraper import get_restaurants_with_menus
restaurants_df, menus_df = get_restaurants_with_menus(lat=19.0760, lng=72.8777)
```

#### Batch Scraping (Multiple Cities)
```bash
# Interactive menu
python batch_scraper.py

# Command line with custom coordinates
python main.py --city "My Area" --min-lat 19.0 --max-lat 19.1 --min-lng 72.8 --max-lng 72.9
```

### 🔄 Backward Compatibility
- Original `main.py` still works with default Coimbatore coordinates
- All existing CSV files remain compatible
- Dashboard functionality unchanged

### ⚠️ Breaking Changes
- `config.py` structure changed (but backward compatible)
- `restaurant_list.py` function signature updated (legacy function maintained)

### 🐛 Bug Fixes
- Improved error handling for network issues
- Better timeout management
- More robust API response validation
- Fixed menu scraping coordinate handling

### 📈 Performance Improvements
- Centralized rate limiting configuration
- Optimized request handling
- Better memory management for large datasets 