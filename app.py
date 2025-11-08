import streamlit as st
from route_finder import load_graph_for_place, nearest_node_for_point
from dijkstra_algorithm import dijkstra_with_steps
from locations_config import CHANDIGARH_LOCATIONS
from streamlit_folium import folium_static
import folium
import osmnx as ox

# Page configuration
st.set_page_config(
    page_title="Chandigarh Route Optimizer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.75rem;
        border: none;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    h1 {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    h2 {
        font-weight: 500;
        color: #2c2c2c;
        font-size: 1.3rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }
    div[data-testid="stSelectbox"] > label {
        font-weight: 500;
        color: #2c2c2c;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
session_keys = ["G", "start_node", "end_node", "start_latlon", "end_latlon", "start_name", "end_name"]
for key in session_keys:
    if key not in st.session_state:
        st.session_state[key] = None

# Header
st.title("Chandigarh Route Optimizer")
st.markdown('<p class="subtitle">Find the shortest route between any two locations in Chandigarh</p>', unsafe_allow_html=True)

# Location Selection
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### Start Location")
    start_location = st.selectbox(
        "Choose starting point",
        options=["Choose starting point..."] + sorted(CHANDIGARH_LOCATIONS.keys()),
        key="start_select",
        index=0
    )
    if start_location == "Choose starting point...":
        st.stop()
    start_latlon = CHANDIGARH_LOCATIONS[start_location]

with col2:
    st.markdown("### Destination")
    end_location = st.selectbox(
        "Choose destination",
        options=["Choose destination..."] + sorted(CHANDIGARH_LOCATIONS.keys()),
        key="end_select",
        index=0
    )
    if end_location == "Choose destination...":
        st.stop()
    end_latlon = CHANDIGARH_LOCATIONS[end_location]

# Validation
if start_location == end_location:
    st.error("Please select different start and destination locations")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)

# Find Route Button
if st.button("Find Shortest Route"):
    
    try:
        # Load Graph without simplification for accurate distances
        if st.session_state.G is None:
            with st.spinner("Loading road network data..."):
                G = ox.graph_from_place(
                    "Chandigarh, India",
                    network_type="drive",
                    simplify=False  # Don't simplify - keep all nodes
                )
                st.session_state.G = G
        else:
            G = st.session_state.G
        
        # Find Nearest Nodes
        with st.spinner("Locating positions on road network..."):
            start_node = nearest_node_for_point(G, start_latlon[0], start_latlon[1])
            end_node = nearest_node_for_point(G, end_latlon[0], end_latlon[1])
            
            if start_node not in G.nodes or end_node not in G.nodes:
                st.error("Unable to locate positions on road network")
                st.stop()
        
        # Save to session
        st.session_state.start_node = start_node
        st.session_state.end_node = end_node
        st.session_state.start_latlon = start_latlon
        st.session_state.end_latlon = end_latlon
        st.session_state.start_name = start_location
        st.session_state.end_name = end_location
        
        # Run Dijkstra's Algorithm  
        with st.spinner("Computing shortest path..."):
            import networkx as nx
            
            # Use NetworkX shortest path (most reliable)
            try:
                route = nx.shortest_path(G, start_node, end_node, weight='length')
            except nx.NetworkXNoPath:
                st.error("No route found between these locations")
                st.stop()
            except Exception as e:
                st.error(f"Error finding route: {str(e)}")
                st.stop()
        
        # Check if route found
        if not route or len(route) < 2:
            st.error("No route found between these locations")
            st.stop()
        
        # Calculate actual distance by summing edge lengths
        actual_distance_meters = 0
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            # Get edge data
            edge_data = G.get_edge_data(u, v)
            if edge_data:
                # Handle MultiDiGraph - get first edge
                if isinstance(edge_data, dict) and len(edge_data) > 0:
                    first_key = min(edge_data.keys())
                    edge_attrs = edge_data[first_key]
                    edge_length = edge_attrs.get('length', 0)
                    actual_distance_meters += edge_length
        
        # Convert to km
        distance_km = actual_distance_meters / 1000
        
        # Realistic time calculation
        # Base speed calculation
        if distance_km < 5:
            base_speed = 25
        elif distance_km < 15:
            base_speed = 28
        else:
            base_speed = 32
            
        # Calculate base time
        base_time_min = (distance_km / base_speed) * 60
        
        # Add realistic delays
        num_intersections = len(route) - 1
        intersection_delay = num_intersections * 0.3  # 18 seconds per intersection avg
        
        estimated_time_min = base_time_min + intersection_delay
        
        # Display Results
        st.markdown("## Route Details")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <p class="metric-value">{distance_km:.2f} km</p>
                    <p class="metric-label">Total Distance</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <p class="metric-value">{int(estimated_time_min)} min</p>
                    <p class="metric-label">Estimated Time</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-container">
                    <p class="metric-value">{len(route)}</p>
                    <p class="metric-label">Route Points</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create Map Visualization
        st.markdown("## Route Map")
        
        route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
        center_lat = sum(lat for lat, _ in route_coords) / len(route_coords)
        center_lon = sum(lon for _, lon in route_coords) / len(route_coords)
        
        # Create map
        route_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add route line
        folium.PolyLine(
            route_coords,
            color="#0066cc",
            weight=5,
            opacity=0.8
        ).add_to(route_map)
        
        # Add start marker
        folium.Marker(
            start_latlon,
            popup=f"<b>Start:</b> {start_location}",
            icon=folium.Icon(color="green", icon="circle", prefix='fa')
        ).add_to(route_map)
        
        # Add end marker
        folium.Marker(
            end_latlon,
            popup=f"<b>Destination:</b> {end_location}",
            icon=folium.Icon(color="red", icon="circle", prefix='fa')
        ).add_to(route_map)
        
        # Display map
        folium_static(route_map, width=1100, height=600)
        
        # Route Summary
        st.markdown("## Summary")
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown(f"""
                **From:** {start_location}  
                **To:** {end_location}
            """)
        
        with summary_col2:
            st.markdown(f"""
                **Distance:** {distance_km:.2f} km  
                **Travel Time:** {int(estimated_time_min)} minutes
            """)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        with st.expander("Error Details"):
            import traceback
            st.code(traceback.format_exc())

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: #999; padding: 2rem 0; border-top: 1px solid #eee; margin-top: 3rem;'>
        <p style='margin: 0;'>Powered by Dijkstra's Algorithm | Data from OpenStreetMap</p>
    </div>
""", unsafe_allow_html=True)