from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor
import re
import time
import random

# Project configuration and utilities
import config
import utils
from utils import LRUCache, Timer, hash_text

# In‑memory LRU cache for translated chunks
_translation_cache = LRUCache(capacity=256)

# Standardize Contextual Blocks for High-Accuracy Translation
# Translating in larger chunks ensures better Hindi grammar
TRANSLATION_BLOCK_SIZE = 1000 
TTS_CHUNK_SIZE = 500

def split_into_chunks(text, max_chars=TRANSLATION_BLOCK_SIZE):
    """
    Split text into chunks of at most max_chars, trying to split on sentence boundaries.
    """
    # Split by common sentence terminators (including Hindi purna viram) but keep them
    sentences = re.split(r'(?<=[.!?।॥|])\s+|\n+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            if len(sentence) > max_chars:
                for i in range(0, len(sentence), max_chars):
                    sub = sentence[i:i+max_chars].strip()
                    if sub:
                        chunks.append(sub)
                current_chunk = ""
            else:
                current_chunk = sentence + " "
                
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks

def contains_too_much_english(text, threshold=0.15):
    if not text:
        return False
    eng_chars = len(re.findall(r'[a-zA-Z]', text))
    return (eng_chars / len(text)) > threshold

def translate_chunk(chunk, max_retries=3):
    """
    Translates a single block using Google Translate with high-accuracy contextual logic.
    Thread-safe implementation.
    """
    if not chunk or not chunk.strip():
        return ""
    
    # Check in‑memory cache first
    cache_key = utils.hash_text(chunk)
    cached = _translation_cache.get(cache_key)
    if cached:
        if config.VERBOSE:
            print(f"Cache hit for chunk (hash={cache_key})")
        return cached

    # Initialize a new translator instance per thread to prevent race conditions
    translator = GoogleTranslator(source='en', target='hi')    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(random.uniform(1.0, 2.0)) 
            
            translated = translator.translate(chunk)
            
            if translated and not contains_too_much_english(translated):
                _translation_cache.set(cache_key, translated)
                return translated
            
        except Exception as e:
            print(f"Translation sync error {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) 
            
    # If all attempts fail, return the original English chunk rather than looping or caching
    return chunk


def translate_text(text, max_workers=None):
    """Orchestrates contextual translation before splitting into TTS chunks."""
    # Use larger Contextual Blocks for higher translation accuracy
    context_blocks = split_into_chunks(text, max_chars=TRANSLATION_BLOCK_SIZE) 
    max_workers = max_workers or config.MAX_WORKERS_TRANSLATE
    with Timer("Translation", logger=print if config.VERBOSE else None):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            translated_blocks = list(executor.map(translate_chunk, context_blocks))
    
    # Return the full translated text to be reconsidered for TTS chunks
    return " ".join([tb for tb in translated_blocks if tb])


