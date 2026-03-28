from deep_translator import GoogleTranslator, MyMemoryTranslator
from concurrent.futures import ThreadPoolExecutor
import re
import time
import random

def split_into_chunks(text, max_chars=4000):
    """Split text into chunks of at most max_chars, trying to split on sentence boundaries."""
    # Split by common sentence terminators but keep them
    sentences = re.split(r'(?<=[.!?]) +|\n+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks

def contains_english(text):
    """Check if the text contains any English alphabet characters."""
    return bool(re.search(r'[a-zA-Z]', text))

def translate_chunk(chunk, max_retries=2):
    if not chunk.strip():
        return ""
    
    current_text = chunk
    translator = MyMemoryTranslator(source='en', target='hi')
    
    for attempt in range(max_retries + 1):
        try:
            # Let workers stagger slightly to avoid hitting API exactly at the same millisecond
            time.sleep(random.uniform(0.1, 0.5)) 
            
            translated = translator.translate(current_text)
            
            # If no English is left, we are good to go!
            if not contains_english(translated):
                return translated
                
            # If English is still there, try translating the *translated* text again
            current_text = translated 
            print(f"Attempt {attempt + 1}: English text still detected. Retrying translation...")
            time.sleep(1 + attempt)  # Give API a short cooldown
            
        except Exception as e:
            print(f"Translation failed for chunk on attempt {attempt + 1}: {e}")
            time.sleep(2 ** (attempt + 1))  # Exponential backoff on real failure: sleep 2, 4, 8 secs
            
    # Return best effort if all retries exhausted
    return current_text

def translate_text(text, max_workers=10):
    """Translates a large block of text concurrently."""
    chunks = split_into_chunks(text)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        translated_chunks = list(executor.map(translate_chunk, chunks))
    return " ".join(translated_chunks)
