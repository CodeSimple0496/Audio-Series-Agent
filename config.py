# Configuration module for Audio Series Agent

# Translation and TTS chunk sizes (characters)
TRANSLATION_BLOCK_SIZE = 1000
TTS_CHUNK_SIZE = 500

# Worker pool sizes – tuned for typical workloads on a Windows desktop.
# Adjust these values via a config override if needed.
MAX_WORKERS_TRANSLATE = 10  # ThreadPool for translation (I/O bound)
MAX_WORKERS_TTS = 10        # ThreadPool for TTS synthesis (I/O bound)
MAX_WORKERS_SCRAPER = 5     # Concurrency for asynchronous scraping

# Verbose logging flag – set to True for detailed timing/progress output.
VERBOSE = False
