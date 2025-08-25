import streamlit as st
import pandas as pd
import numpy as np
import re
from scraper.live_scraper import get_restaurants_with_menus, scrape_restaurants_by_location

st.set_page_config(page_title="Live Swiggy Restaurant Finder", layout="wide")
st.title("🍽️ Swiggy Restaurant & Food Finder (LIVE)")

# Sidebar for location input
st.sidebar.header("📍 Location Settings")
st.sidebar.write("Enter latitude and longitude to find restaurants in that area:")

col1, col2 = st.sidebar.columns(2)
with col1:
    lat = st.number_input("Latitude", value=12.9716, format="%.6f", help="Enter latitude coordinate")
with col2:
    lng = st.number_input("Longitude", value=77.5946, format="%.6f", help="Enter longitude coordinate")

include_menus = st.sidebar.checkbox("Include Menu Data", value=True, help="Fetch menu items for each restaurant")
smart_search = st.sidebar.checkbox("Smart Search (try nearby if 0 results)", value=True, help="Try a grid around the input if no restaurants are found")

scraping_time = None

# Search button
if st.sidebar.button("🔍 Search Restaurants", type="primary"):
    with st.spinner("Searching for restaurants..."):
        try:
            restaurants_df, is_unserviceable, scraping_time = scrape_restaurants_by_location(
                lat=lat, 
                lng=lng, 
                max_restaurants=100,  # Always fetch up to 100
                smart_search=smart_search
            )
            menus_df = pd.DataFrame()
            if is_unserviceable:
                st.error("🚫 Swiggy does not deliver to this location. Please try a different coordinate or a nearby city center.")
                st.session_state.data_loaded = False
            elif not restaurants_df.empty:
                st.success(f"✅ Found {len(restaurants_df)} restaurants!")
                if include_menus:
                    all_menus = []
                    for idx, row in restaurants_df.iterrows():
                        menu_df = get_restaurants_with_menus(row['lat'], row['lng'], 1, True)[1]
                        if not menu_df.empty:
                            menu_df['restaurant_name'] = row['name']
                            all_menus.append(menu_df)
                    if all_menus:
                        menus_df = pd.concat(all_menus, ignore_index=True)
                st.session_state.restaurants_df = restaurants_df
                st.session_state.menus_df = menus_df
                st.session_state.data_loaded = True
            else:
                st.error("❌ No restaurants found for this location. Try a nearby coordinate or check if Swiggy serves this area.")
                st.session_state.data_loaded = False
        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)}")
            st.session_state.data_loaded = False
    if scraping_time is not None:
        st.info(f"⏱️ Live scraping time: {scraping_time:.2f} seconds")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if st.session_state.data_loaded:
    restaurants_df = st.session_state.restaurants_df
    menus_df = st.session_state.menus_df
    def parse_cost_for_two(val):
        if pd.isnull(val):
            return np.nan
        match = re.search(r'([\d,]+)', str(val))
        if match:
            return float(match.group(1).replace(',', ''))
        return np.nan
    restaurants_df['cost_for_two_clean'] = restaurants_df['cost_for_two'].apply(parse_cost_for_two)
    st.header("🏪 Restaurant Search")
    col1, col2, col3 = st.columns(3)
    with col1:
        name_query = st.text_input("Search restaurant by name")
    with col2:
        cuisine_options = sorted(list(set(c for cs in restaurants_df['cuisines'].dropna() for c in cs.split(', '))))
        cuisine_filter = st.multiselect("Cuisine", cuisine_options)
    with col3:
        area_options = sorted(list(restaurants_df['area'].dropna().unique()))
        area_filter = st.multiselect("Area", area_options)
    col1, col2 = st.columns(2)
    with col1:
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.0, 0.1)
    with col2:
        sort_by = st.selectbox("Sort restaurants by", ["Best Rated", "Lowest Price for Two", "Fastest Delivery"])
    filtered_rest = restaurants_df.copy()
    if name_query:
        filtered_rest = filtered_rest[filtered_rest['name'].str.contains(name_query, case=False, na=False)].copy()
    if cuisine_filter:
        filtered_rest = filtered_rest[filtered_rest['cuisines'].apply(
            lambda x: any(c in x for c in cuisine_filter) if pd.notnull(x) else False
        )].copy()
    if area_filter:
        filtered_rest = filtered_rest[filtered_rest['area'].isin(area_filter)].copy()
    filtered_rest = filtered_rest[filtered_rest['rating'].fillna(0).astype(float) >= min_rating].copy()
    if sort_by == "Best Rated":
        filtered_rest = filtered_rest.sort_values(by="rating", ascending=False).copy()
    elif sort_by == "Lowest Price for Two":
        filtered_rest = filtered_rest.sort_values(by="cost_for_two_clean", ascending=True).copy()
    else:
        filtered_rest = filtered_rest.sort_values(by="delivery_time", ascending=True).copy()
    st.subheader(f"Restaurants found: {len(filtered_rest)}")
    if not filtered_rest.empty:
        for idx, restaurant in filtered_rest.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{restaurant['name']}**")
                    st.caption(f"📍 {restaurant['area']} • {restaurant['cuisines']}")
                with col2:
                    if pd.notna(restaurant['rating']):
                        st.metric("Rating", f"{restaurant['rating']:.1f}⭐")
                    else:
                        st.metric("Rating", "N/A")
                with col3:
                    if pd.notna(restaurant['delivery_time']):
                        st.metric("Delivery", f"{restaurant['delivery_time']} min")
                    else:
                        st.metric("Delivery", "N/A")
                st.divider()
        with st.expander("📊 Detailed Table View"):
            display_cols = ["name", "cuisines", "area", "rating", "cost_for_two", "delivery_time"]
            st.dataframe(filtered_rest[display_cols], use_container_width=True)
    else:
        st.info("No restaurants match your filters. Try adjusting your search criteria.")
    if not menus_df.empty:
        st.header("🍽️ Menu Item Search")
        col1, col2, col3 = st.columns(3)
        with col1:
            menu_name_query = st.text_input("Search food by name", key="menu_search")
        with col2:
            min_menu_price, max_menu_price = st.slider(
                "Menu Price (₹)", 
                0, 
                int(menus_df['price'].max()) if not menus_df.empty else 1000, 
                (0, 500), 
                10
            )
        with col3:
            veg_filter = st.selectbox("Veg/Non-Veg", ["All", "Veg", "Non-Veg"])
        filtered_menu = menus_df.copy()
        if menu_name_query:
            filtered_menu = filtered_menu[filtered_menu['item_name'].str.contains(menu_name_query, case=False, na=False)].copy()
        filtered_menu = filtered_menu[
            (filtered_menu['price'].fillna(0).astype(float) >= min_menu_price) & 
            (filtered_menu['price'].fillna(0).astype(float) <= max_menu_price)
        ].copy()
        if veg_filter != "All":
            filtered_menu = filtered_menu[filtered_menu['veg'] == veg_filter].copy()
        filtered_menu = filtered_menu.sort_values(by=["price", "item_name"]).copy()
        st.subheader(f"Menu items found: {len(filtered_menu)}")
        if not filtered_menu.empty:
            for restaurant_name in filtered_menu['restaurant_name'].unique():
                restaurant_menu = filtered_menu[filtered_menu['restaurant_name'] == restaurant_name]
                with st.expander(f"🍽️ {restaurant_name} ({len(restaurant_menu)} items)"):
                    for idx, item in restaurant_menu.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"**{item['item_name']}**")
                            if item['description']:
                                st.caption(item['description'])
                        with col2:
                            st.metric("Price", f"₹{item['price']:.0f}")
                        with col3:
                            st.metric("Type", item['veg'])
                        st.divider()
            with st.expander("📊 Menu Table View"):
                display_cols = ["restaurant_name", "item_name", "price", "veg", "category"]
                st.dataframe(filtered_menu[display_cols], use_container_width=True)
        else:
            st.info("No menu items match your filters.")
    st.sidebar.divider()
    st.sidebar.subheader("📍 Current Location")
    st.sidebar.write(f"Latitude: {lat}")
    st.sidebar.write(f"Longitude: {lng}")
    if st.sidebar.button("🗑️ Clear Data"):
        st.session_state.data_loaded = False
        st.rerun()
else:
    st.markdown("""
    ## Welcome to Swiggy Restaurant Finder! 🍽️
    
    **How to use:**
    1. Enter the latitude and longitude coordinates in the sidebar
    2. Choose whether to include menu data
    3. (Optional) Enable smart search to try nearby coordinates if 0 results
    4. Click "Search Restaurants" to get live results
    
    **Tip:**
    - Use the coordinates of any Swiggy-linked restaurant or delivery area for best results.
    - If you get 0 results, try a nearby coordinate or a more central location.
    - This tool is 100% coordinate-driven—no city or area selection required.
    
    **Features:**
    - ✅ Real-time restaurant data
    - ✅ Live menu scraping
    - ✅ Advanced filtering and search
    - ✅ No data storage (privacy-friendly)
    - ✅ Rate-limited requests (respectful scraping)
    """)

st.caption("Built with Streamlit | Live data from Swiggy (Unofficial API) | Rate-limited for respectful scraping") 