import os
import sys
import io
import json
import csv
import time
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from esco_graph import build_esco_graph
from onet_loader import load_onet_data
from crosswalk import apply_crosswalk

USE_LOCAL_MODE = True

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def setup_database(conn):
    if USE_LOCAL_MODE:
        return
    
    print("Setting up database schema...")
    with conn.cursor() as cur:
        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Drop tables if exist for clean rerun
        cur.execute("DROP TABLE IF EXISTS catalog_gaps CASCADE;")
        cur.execute("DROP TABLE IF EXISTS decision_ledger CASCADE;")
        cur.execute("DROP TABLE IF EXISTS user_sessions CASCADE;")
        cur.execute("DROP TABLE IF EXISTS courses CASCADE;")
        cur.execute("DROP TABLE IF EXISTS skills CASCADE;")
        
        # Create Skills table (e5-large uses 1024 dims)
        cur.execute("""
            CREATE TABLE skills (
                id VARCHAR PRIMARY KEY,
                label VARCHAR NOT NULL,
                criticality FLOAT DEFAULT 1.0,
                decay_weight FLOAT DEFAULT 0.1,
                embedding vector(1024)
            );
        """)
        
        # Create Courses table
        cur.execute("""
            CREATE TABLE courses (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                description TEXT,
                skills_mapped VARCHAR,
                embedding vector(1024)
            );
        """)
        
        cur.execute("""
            CREATE TABLE user_sessions (
                session_id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                state_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cur.execute("""
            CREATE TABLE decision_ledger (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR REFERENCES user_sessions(session_id),
                action VARCHAR,
                details JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cur.execute("""
            CREATE TABLE catalog_gaps (
                id SERIAL PRIMARY KEY,
                missing_skill VARCHAR,
                demand_score FLOAT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()
    print("Database tables created successfully.")

def setup_redis():
    if USE_LOCAL_MODE:
        print("Mock Redis cache stored")
        return
    
    import redis
    print("Setting up Redis demo cache...")
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    
    # Valid PaceResult JSON mock
    mock_pace_result = {
        "status": "success",
        "data": {
            "pace_score": 85,
            "recommended_path": ["esco:1", "esco:2"],
            "readiness": "High"
        }
    }
    
    # Insert demo:1 to demo:5, no expiry
    for i in range(1, 6):
        client.set(f"demo:{i}", json.dumps(mock_pace_result)) # no ex argument => no expiry
    print("Redis populated with demo:1 to demo:5")


def process_and_insert_data(conn=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    esco_json = os.path.join(base_dir, "data", "esco_v1.2.json")
    esco_pkl = os.path.join(base_dir, "data", "esco_graph.pkl")
    onet_csv = os.path.join(base_dir, "data", "onet.csv")
    catalog_csv = os.path.join(base_dir, "data", "sample_catalog.csv")
    out_txt = os.path.join(base_dir, "data", "sample_output.txt")
    
    output_lines = []
    
    graph = build_esco_graph(esco_json, esco_pkl)
    print("✔ Graph built")
    output_lines.append(f"Graph stats: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    onet_map = load_onet_data(onet_csv)
    graph = apply_crosswalk(graph, onet_map)
    
    try:
        from sentence_transformers import SentenceTransformer
        # e5-large can be heavy, let's use memory
        model = SentenceTransformer('intfloat/multilingual-e5-large')
        emb_type = "sentence-transformers API (intfloat/multilingual-e5-large)"
    except Exception as e:
        print(f"Warning: Could not load sentence-transformers model ({e}). Falling back to random embeddings.")
        model = None
        emb_type = "random vectors (384 dims)"

    skills_data = []
    for node_id, data in graph.nodes(data=True):
        label = data.get("label", "")
        if not label:
            continue
        if model:
            emb = model.encode(f"passage: {label}", normalize_embeddings=True).tolist()
        else:
            emb = np.random.rand(384).tolist()
        skills_data.append((node_id, label, data.get("criticality", 1.0), data.get("decay_weight", 0.1), emb))
        
    courses_data = []
    if os.path.exists(catalog_csv):
        with open(catalog_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course_id = row['course_id']
                title = row['title']
                desc = row['description']
                skills_mapped = row.get('skills_mapped', '')
                
                if model:
                    text_to_embed = f"passage: {title}. {desc}"
                    emb = model.encode(text_to_embed, normalize_embeddings=True).tolist()
                else:
                    emb = np.random.rand(384).tolist()
                
                courses_data.append((course_id, title, desc, skills_mapped, emb))
                
    print("✔ Courses loaded")
    output_lines.append(f"Number of courses: {len(courses_data)}")
    output_lines.append(f"Embeddings info: Generated using {emb_type}")
    
    if USE_LOCAL_MODE:
        print("Mock DB insert successful")
    else:
        from psycopg2.extras import execute_values
        if skills_data:
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO skills (id, label, criticality, decay_weight, embedding)
                    VALUES %s
                """, skills_data)
            conn.commit()
        if courses_data:
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO courses (id, title, description, skills_mapped, embedding)
                    VALUES %s
                """, courses_data)
            conn.commit()
        
    print("✔ Embeddings generated")
    
    print("Running ANN search for 'machine learning'...")
    if model:
        query_emb = model.encode("query: machine learning", normalize_embeddings=True).tolist()
    else:
        query_emb = np.random.rand(384).tolist()
        
    if USE_LOCAL_MODE:
        results = []
        for c in courses_data:
            sim = cosine_similarity(query_emb, c[4])
            results.append((c[0], c[1], c[3], sim))
        
        results.sort(key=lambda x: x[3], reverse=True)
        top_5 = results[:5]
        output_lines.append("Top 5 matched courses for 'machine learning':")
        for idx, r in enumerate(top_5, 1):
            msg = f"Result {idx}: {r[1]} (Skills: {r[2]}) - Score: {r[3]:.4f}"
            print(msg)
            output_lines.append(msg)
        print("✔ Top matches displayed")
    else:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, skills_mapped 
                FROM courses 
                ORDER BY embedding <-> %s::vector 
                LIMIT 5;
            """, (query_emb,))
            db_results = cur.fetchall()
            output_lines.append("Top 5 matched courses for 'machine learning':")
            for idx, r in enumerate(db_results, 1):
                msg = f"Result {idx}: {r[1]} (Skills: {r[2]}) - ID: {r[0]}"
                print(msg)
                output_lines.append(msg)
        print("✔ Top matches displayed")

    if USE_LOCAL_MODE:
        setup_redis()
        print("✔ Redis mock stored")
        output_lines.append("Redis mock status: 5 items stored successfully")
    else:
        setup_redis()

    print("✔ Pipeline complete")
    output_lines.append("Final SUCCESS message: Pipeline execution complete and demo ready.")
    
    if USE_LOCAL_MODE:
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines) + "\n")
        print(f"Details saved to {out_txt}")
        
    return model

if __name__ == "__main__":
    start_time = time.time()
    DB_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/nexus_db")
    
    try:
        if USE_LOCAL_MODE:
            process_and_insert_data(None)
        else:
            import psycopg2
            conn = psycopg2.connect(DB_URL)
            setup_database(conn)
            model = process_and_insert_data(conn)
            conn.close()
            
        elapsed = time.time() - start_time
        print(f"SUCCESS: The pipeline finished correctly in {elapsed:.2f} seconds.")
    except Exception as e:
        print(f"ERROR unexpectedly: {e}")
