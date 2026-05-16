import time
import threading
import hashlib
import json
from collections import OrderedDict

class Timer:
    """Context manager for timing a code block."""
    def __init__(self, name: str = "Block", logger=None):
        self.name = name
        self.logger = logger
        self.start = None
        self.elapsed = None
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        msg = f"{self.name} took {self.elapsed:.3f}s"
        if self.logger:
            self.logger(msg)
        else:
            print(msg)

class LRUCache:
    """Simple thread‑safe LRU cache.
    Stores up to *capacity* items; evicts least‑recently used on overflow.
    """
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            return self.cache[key]
    def set(self, key, value):
        with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    def clear(self):
        with self.lock:
            self.cache.clear()

def hash_text(text: str) -> str:
    """Return a short SHA256 hash of the given text for caching purposes."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

def load_json(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(path: str, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
