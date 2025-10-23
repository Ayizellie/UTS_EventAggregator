from collections import deque
import logging
import threading

class EventQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()  # 🔒 mencegah race condition

    def add_event(self, event):
        """Menambahkan event ke dalam queue."""
        with self.lock:
            self.queue.append(event)
            logging.info(f"🟢 Event dimasukkan ke queue: {event}")

    def get_event(self):
        """Mengambil satu event dari queue (FIFO)."""
        with self.lock:
            if self.queue:
                event = self.queue.popleft()
                logging.info(f"📤 Event diambil dari queue: {event}")
                return event
            return None

    def get_all_events(self):
        """Melihat semua event di queue tanpa menghapus."""
        with self.lock:
            return list(self.queue)

    def __len__(self):
        """Agar bisa dipanggil len(queue)."""
        with self.lock:
            return len(self.queue)
