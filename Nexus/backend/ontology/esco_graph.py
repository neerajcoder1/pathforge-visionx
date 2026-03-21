import json
import networkx as nx
import pickle
import os
import random

def build_esco_graph(json_path: str, output_pkl: str) -> nx.DiGraph:
    """
    Load ESCO JSON, Build NetworkX DiGraph, Add nodes + edges, Save pickle.
    Generates a mock graph of 100 nodes if not present or small.
    """
    print(f"Loading ESCO data from {json_path}...")
    
    graph = nx.DiGraph()
    
    esco_data = []
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                esco_data = json.load(f)
            except json.JSONDecodeError:
                pass
                
    if len(esco_data) < 50:
        print("Generating mock ESCO graph with 100 nodes as requested...")
        # Add 100 mock nodes
        for i in range(1, 101):
            skill_id = f"esco:{i}"
            graph.add_node(
                skill_id,
                label=f"Mock Skill {i}",
                criticality=1.0,
                decay_weight=0.1
            )
            
        # Add random edges (PREREQUISITE_OF, REQUIRES, SIMILAR_TO)
        edge_types = ["PREREQUISITE_OF", "REQUIRES", "SIMILAR_TO"]
        for i in range(1, 101):
            num_edges = random.randint(1, 3)
            for _ in range(num_edges):
                target = random.randint(1, 100)
                if target != i:
                    graph.add_edge(f"esco:{i}", f"esco:{target}", type=random.choice(edge_types))
    else:
        # Add Nodes
        for item in esco_data:
            skill_id = item.get("id")
            title = item.get("title", "")
            graph.add_node(
                skill_id, 
                label=title,
                criticality=1.0, # default, update later with O*NET
                decay_weight=0.1
            )
            
        # Mocking some relationships
        for i in range(len(esco_data) - 1):
            graph.add_edge(esco_data[i]['id'], esco_data[i+1]['id'], type="REQUIRES")
        
    print(f"Built graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
    
    # Save to pickle
    os.makedirs(os.path.dirname(output_pkl), exist_ok=True)
    with open(output_pkl, 'wb') as f:
        pickle.dump(graph, f)
        
    print(f"Saved graph to {output_pkl}")
    return graph

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    json_path = os.path.join(base_dir, "data", "esco_v1.2.json")
    pkl_path = os.path.join(base_dir, "data", "esco_graph.pkl")
    build_esco_graph(json_path, pkl_path)
