# dijkstra_algorithm.py
import heapq

def dijkstra_with_steps(G, start, end):
    """
    Dijkstra algorithm generator that yields progress steps.
    Uses edge 'length' attribute from OSM data for accurate distance calculation.
    """
    pq = [(0, start, [])]
    visited = set()
    distances = {start: 0}
    nodes_explored = 0

    while pq:
        (dist, node, path) = heapq.heappop(pq)
        
        if node in visited:
            continue

        visited.add(node)
        path = path + [node]
        nodes_explored += 1

        # Yield progress step
        yield {
            "current_node": node,
            "distance": dist,
            "visited": list(visited),
            "path": path,
            "nodes_explored": nodes_explored,
            "queue_size": len(pq)
        }

        # Check if destination reached
        if node == end:
            yield {
                "done": True,
                "path": path,
                "total_distance": dist,
                "nodes_explored": nodes_explored
            }
            return

        # Explore neighbors
        for neighbor in G.neighbors(node):
            if neighbor in visited:
                continue
            
            # Get edge data - handle MultiDiGraph properly
            edge_data = G.get_edge_data(node, neighbor)
            if edge_data:
                # For MultiDiGraph, edge_data is a dict of dicts
                # Get the first edge's length
                if isinstance(edge_data, dict):
                    first_edge = edge_data[list(edge_data.keys())[0]]
                    weight = first_edge.get('length', 1)
                else:
                    weight = edge_data.get('length', 1)
            else:
                weight = 1
            
            new_dist = dist + weight
            
            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor, path))

    # No path found
    yield {
        "done": True,
        "path": [],
        "total_distance": float('inf'),
        "nodes_explored": nodes_explored,
        "error": "No path found"
    }


def dijkstra_shortest_path(G, start, end):
    """
    Standard Dijkstra algorithm without step-by-step yields.
    Returns the shortest path and its distance.
    
    Returns:
        (path, distance) or (None, float('inf')) if no path exists
    """
    pq = [(0, start, [])]
    visited = set()
    distances = {start: 0}

    while pq:
        (dist, node, path) = heapq.heappop(pq)
        
        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == end:
            return path, dist

        for neighbor in G.neighbors(node):
            if neighbor in visited:
                continue
            
            edge_data = G.get_edge_data(node, neighbor)
            if edge_data:
                if isinstance(edge_data, dict):
                    first_edge = edge_data[list(edge_data.keys())[0]]
                    weight = first_edge.get('length', 1)
                else:
                    weight = edge_data.get('length', 1)
            else:
                weight = 1
            
            new_dist = dist + weight
            
            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor, path))

    return None, float('inf')