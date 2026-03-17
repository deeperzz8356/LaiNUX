import sqlite3
import time
from ..utils.logger import logger

class MemoryStore:
    def __init__(self, db_path="agent_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wisdom (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learned_lesson TEXT,
                embedding BOLB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                step TEXT,
                result TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
        ''')
        conn.commit()
        conn.close()
        
        # Initialize RAG Model (The 'Synaptic' Layer)
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            import numpy as np
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = None # Will build on query if empty
            logger.info("Synaptic RAG Layer: Active (Vector Memory Enabled)")
        except ImportError:
            self.embedder = None
            logger.warning("RAG Mode: Dependencies missing. Falling back to linear memory.")

    def record_task(self, goal):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (goal, status) VALUES (?, ?)", (goal, "pending"))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def update_task_status(self, task_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()
        conn.close()

    def add_history(self, task_id, step, result):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (task_id, step, result) VALUES (?, ?, ?)", (task_id, step, result))
        conn.commit()
        conn.close()

    def record_wisdom(self, lesson):
        """Saves a learned lesson and generates its neural embedding."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        embedding_blob = None
        if self.embedder:
            try:
                import pickle
                vec = self.embedder.encode([lesson])[0]
                embedding_blob = pickle.dumps(vec)
            except Exception: pass
            
        cursor.execute("INSERT INTO wisdom (learned_lesson, embedding) VALUES (?, ?)", 
                      (lesson, sqlite3.Binary(embedding_blob) if embedding_blob else None))
        conn.commit()
        conn.close()

    def get_wisdom(self, query=None, limit=5):
        """Retrieves historical wisdom. If query is provided, uses semantic search (RAG)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if query and self.embedder:
            try:
                import pickle
                import numpy as np
                import faiss
                
                # Retrieve all embeddings from DB
                cursor.execute("SELECT learned_lesson, embedding FROM wisdom WHERE embedding IS NOT NULL")
                rows = cursor.fetchall()
                if not rows: return []
                
                lessons = [r[0] for r in rows]
                embeddings = np.array([pickle.loads(r[1]) for r in rows]).astype('float32')
                
                # Build temporary index
                d = embeddings.shape[1]
                idx = faiss.IndexFlatL2(d)
                idx.add(embeddings)
                
                # Search
                q_vec = self.embedder.encode([query]).astype('float32')
                distances, indices = idx.search(q_vec, min(limit, len(lessons)))
                
                results = [lessons[i] for i in indices[0] if i != -1]
                conn.close()
                return results
            except Exception as e:
                logger.error(f"RAG Retrieval failed: {e}")
        
        # Fallback to simple recent retrieve
        cursor.execute("SELECT learned_lesson FROM wisdom ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

