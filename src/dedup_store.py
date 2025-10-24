import sqlite3
import os
import threading

class DedupStore:
    def __init__(self, db_path='data/dedup_store.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dedup (
                    topic TEXT,
                    event_id TEXT,
                    PRIMARY KEY (topic, event_id)
                )
            """)
            conn.commit()

    def add_event(self, topic, event_id):
        """Return True kalau baru, False kalau duplicate"""
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO dedup (topic, event_id) VALUES (?, ?)",
                (topic, event_id)
            )
            return cur.rowcount == 1

    def get_all_events(self, topic=None):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            if topic:
                rows = conn.execute(
                    "SELECT topic, event_id FROM dedup WHERE topic=?", (topic,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT topic, event_id FROM dedup").fetchall()
            return rows  

    def get_topics(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            return [row[0] for row in conn.execute("SELECT DISTINCT topic FROM dedup")]
        
    def set_db_path(self, new_path):
        """Ubah lokasi database untuk keperluan testing."""
        with self.lock:
            self.db_path = new_path
            self._ensure_db_exists()

    def is_duplicate(self, topic, event_id):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT 1 FROM dedup WHERE topic=? AND event_id=?", (topic, event_id))
            return cur.fetchone() is not None

