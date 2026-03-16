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
