# locations_config.py
"""
Configuration file for predefined locations in Chandigarh.
Add or modify locations here with their exact GPS coordinates.
"""

# Chandigarh Locations with verified coordinates
CHANDIGARH_LOCATIONS = {
    # Educational Institutions
    "Punjab University": (30.7600, 76.7689),
    "Panjab University SSC": (30.7565, 76.7686),
    "Chandigarh University": (30.5129, 76.6575),
    "IISER Mohali": (30.6639, 76.7294),
    
    # Shopping & Entertainment
    "Elante Mall": (30.7057, 76.8011),
    "Sector 17 Plaza": (30.7411, 76.7807),
    
    # Tourist Attractions
    "Rock Garden": (30.7520, 76.7394),
    "Sukhna Lake": (30.7421, 76.8188),
    "Rose Garden": (30.7479, 76.7580),
    "Leisure Valley": (30.7338, 76.7805),
    "Government Museum": (30.7579, 76.7850),
    
    # Healthcare
    "PGI Hospital": (30.7664, 76.7757),
    
    # Transportation
    "ISBT Chandigarh": (30.7119, 76.8025),
    "Chandigarh Railway Station": (30.6912, 76.8636),
    "Chandigarh Airport": (30.6735, 76.7885),
    
    # Sports & Recreation
    "Mohali Cricket Stadium": (30.6900, 76.7371),
    
    # Government & Admin
    "Secretariat Chandigarh": (30.7625, 76.7738),
    "Capitol Complex": (30.7594, 76.8083),
}

# You can add more cities here
LUDHIANA_LOCATIONS = {
    "Ludhiana Railway Station": (30.9049, 75.8507),
    "Punjab Agricultural University": (30.9010, 75.8573),
    "MBD Mall": (30.9003, 75.8632),
    "Maharaja Ranjit Singh Punjab Technical University": (30.8093, 75.8519),
}

AMRITSAR_LOCATIONS = {
    "Golden Temple": (31.6200, 74.8765),
    "Jallianwala Bagh": (31.6210, 74.8795),
    "Amritsar Railway Station": (31.6346, 74.8739),
    "Wagah Border": (31.6045, 74.5731),
}

def get_locations_for_city(city_name):
    """
    Get predefined locations for a specific city.
    
    Args:
        city_name: str - Name of the city ('chandigarh', 'ludhiana', 'amritsar')
    
    Returns:
        dict - Dictionary of location names and coordinates
    """
    city_map = {
        'chandigarh': CHANDIGARH_LOCATIONS,
        'ludhiana': LUDHIANA_LOCATIONS,
        'amritsar': AMRITSAR_LOCATIONS,
    }
    
    city_key = city_name.lower()
    if city_key not in city_map:
        raise ValueError(f"City '{city_name}' not found. Available cities: {list(city_map.keys())}")
    
    return city_map[city_key]


def add_location(city_locations, name, latitude, longitude):
    """
    Add a new location to the dictionary.
    
    Args:
        city_locations: dict - The locations dictionary to update
        name: str - Name of the location
        latitude: float - Latitude coordinate
        longitude: float - Longitude coordinate
    
    Returns:
        dict - Updated locations dictionary
    """
    city_locations[name] = (latitude, longitude)
    return city_locations


def validate_coordinates(lat, lon):
    """
    Validate if coordinates are reasonable.
    
    Args:
        lat: float - Latitude
        lon: float - Longitude
    
    Returns:
        bool - True if valid, False otherwise
    """
    # Chandigarh area bounds (approximate)
    if 30.5 <= lat <= 31.0 and 76.5 <= lon <= 77.0:
        return True
    return False


def print_locations(city_locations):
    """
    Pretty print all locations with their coordinates.
    """
    print(f"\n{'Location Name':<40} {'Latitude':<12} {'Longitude':<12}")
    print("-" * 64)
    for name, (lat, lon) in sorted(city_locations.items()):
        print(f"{name:<40} {lat:<12.4f} {lon:<12.4f}")
    print(f"\nTotal locations: {len(city_locations)}")


if __name__ == "__main__":
    # Example usage
    print("=== Chandigarh Locations ===")
    print_locations(CHANDIGARH_LOCATIONS)
    
    print("\n=== Ludhiana Locations ===")
    print_locations(LUDHIANA_LOCATIONS)
    
    print("\n=== Amritsar Locations ===")
    print_locations(AMRITSAR_LOCATIONS)