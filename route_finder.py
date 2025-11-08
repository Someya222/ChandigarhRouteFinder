# route_finder.py (Enhanced Version)
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# configure osmnx
ox.settings.log_console = False
ox.settings.use_cache = True

geolocator = Nominatim(user_agent="route_optimizer_app")

def geocode_place(place_name, retries=3):
    """
    Return (lat, lon) tuple for a place string using geopy / Nominatim.
    Includes retry logic for better reliability.
    """
    for attempt in range(retries):
        try:
            location = geolocator.geocode(place_name, timeout=10)
            if location is None:
                raise ValueError(f"Could not find location: '{place_name}'. Please try a more specific address.")
            return (location.latitude, location.longitude)
        except GeocoderTimedOut:
            if attempt < retries - 1:
                time.sleep(1)  # Wait before retry
                continue
            raise ValueError(f"Geocoding timed out for: {place_name}")
        except GeocoderServiceError as e:
            raise ValueError(f"Geocoding service error: {str(e)}")
    
    raise ValueError(f"Failed to geocode after {retries} attempts: {place_name}")


def load_graph_for_place(place_name, network_type="drive", dist=None, simplify=True):
    """
    Load (and cache via osmnx internal cache) a road network graph for the given place.
    
    Args:
        place_name: e.g. "Chandigarh, India" or polygon query
        network_type: "drive", "walk", "bike", "all", "all_private"
        dist: radius in meters if loading by distance from point
        simplify: If False, preserves all nodes (more accurate but slower)
    
    Returns:
        NetworkX MultiDiGraph with road network
    """
    try:
        if dist:
            # Load graph by radius around a point
            lat, lon = geocode_place(place_name)
            G = ox.graph_from_point((lat, lon), dist=dist, network_type=network_type, simplify=simplify)
        else:
            # Load graph for entire place
            G = ox.graph_from_place(place_name, network_type=network_type, simplify=simplify)
        
        # Verify graph has edges
        if len(G.edges) == 0:
            raise ValueError(f"No road network found for '{place_name}' with network type '{network_type}'")
        
        # Project graph to UTM for accurate distance calculations
        G = ox.project_graph(G)
        
        return G
    
    except Exception as e:
        if "nominatim" in str(e).lower() or "http" in str(e).lower():
            raise ValueError(f"Network error loading map data. Please check your internet connection.")
        raise ValueError(f"Error loading graph: {str(e)}")


def nearest_node_for_point(G, lat, lon):
    """
    Return nearest node id in G for given lat, lon.
    Note: ox.distance.nearest_nodes expects (G, X, Y) => (lon, lat).
    """
    try:
        node = ox.distance.nearest_nodes(G, lon, lat)
        return node
    except Exception as e:
        raise ValueError(f"Error finding nearest node at ({lat}, {lon}): {str(e)}")


def get_route_length_meters(G, route):
    """
    Sum lengths (in meters) for route (list of nodes).
    
    Args:
        G: NetworkX graph
        route: List of node IDs
    
    Returns:
        Total length in meters
    """
    if not route or len(route) < 2:
        return 0.0
    
    length = 0.0
    for u, v in zip(route[:-1], route[1:]):
        # edges can be multi; get 'length' attribute for the first edge
        data = G.get_edge_data(u, v)
        if data:
            # pick the first key
            edge_attrs = data[list(data.keys())[0]]
            length += edge_attrs.get("length", 0.0)
        else:
            # Edge doesn't exist - this shouldn't happen in a valid route
            print(f"Warning: No edge found between {u} and {v}")
    
    return length


def validate_route_exists(G, start_node, end_node):
    """
    Check if a path exists between start and end nodes.
    
    Returns:
        (bool, str): (path_exists, message)
    """
    try:
        # Quick check using NetworkX
        if nx.has_path(G, start_node, end_node):
            return True, "Path exists"
        else:
            return False, "No path exists between these locations in the road network"
    except Exception as e:
        return False, f"Error checking path: {str(e)}"


def get_route_statistics(G, route):
    """
    Calculate various statistics for a route.
    
    Returns:
        dict with distance, number of turns, etc.
    """
    if not route or len(route) < 2:
        return {"distance_m": 0, "distance_km": 0, "num_nodes": 0}
    
    distance_m = get_route_length_meters(G, route)
    
    return {
        "distance_m": distance_m,
        "distance_km": distance_m / 1000,
        "num_nodes": len(route),
        "num_segments": len(route) - 1
    }