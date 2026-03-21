from typing import Dict
import networkx as nx

def apply_crosswalk(graph: nx.DiGraph, onet_importance_map: Dict[str, float]) -> nx.DiGraph:
    """
    ESCO <-> O*NET mapping.
    Updates the ESCO graph nodes with criticality derived from O*NET importance.
    """
    print("Applying ESCO <-> O*NET crosswalk...")
    
    updated_count = 0
    for node_id, data in graph.nodes(data=True):
        label = str(data.get("label", "")).strip().lower()
        
        # If the label exists in our O*NET map, update criticality
        if label in onet_importance_map:
            graph.nodes[node_id]["criticality"] = onet_importance_map[label]
            updated_count += 1
            
    print(f"Updated criticality for {updated_count} nodes.")
    return graph
