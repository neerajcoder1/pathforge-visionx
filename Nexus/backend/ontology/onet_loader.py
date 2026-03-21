import pandas as pd
import os
import random
from typing import Dict

def load_onet_data(csv_path: str) -> Dict[str, float]:
    """
    Load O*NET CSV and map importance weights.
    Returns a dictionary mapping O*NET concept to importance value.
    """
    print(f"Loading O*NET data from {csv_path}...")
    importance_map = {}
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                name = str(row.get("mock_name", "")).strip().lower()
                importance = float(row.get("importance", 0.8))
                if name:
                    importance_map[name] = importance
        except Exception as e:
            print(f"Could not load csv: {e}")
    else:
        print(f"Warning: {csv_path} not found. Using default mapping.")
        
    # Add mock data
    importance_map.update({
        "python programming": 0.95,
        "kubernetes": 0.90,
        "machine learning": 0.92,
        "data analysis": 0.85,
        "project management": 0.80
    })
    
    # Mock data to match ESCO graph node labels
    for i in range(1, 101):
        importance_map[f"mock skill {i}"] = round(random.uniform(0.5, 1.0), 2)
    
    print(f"Loaded {len(importance_map)} O*NET importance records.")
    return importance_map

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(base_dir, "data", "onet.csv")
    load_onet_data(csv_path)
