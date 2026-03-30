from deep_translator import GoogleTranslator, MyMemoryTranslator
from concurrent.futures import ThreadPoolExecutor
import re
import time
import random

def split_into_chunks(text, max_chars=400):
    """
    Split text into chunks of at most max_chars, trying to split on sentence boundaries.
    Defaulting to 400 for optimal edge-tts and translation performance.
    """
    # Split by common sentence terminators but keep them
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
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
            
            # If the sentence itself is longer than max_chars, split it by length
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

def contains_english(text):
    """Check if the text contains any English alphabet characters."""
    return bool(re.search(r'[a-zA-Z]', text))

def translate_chunk(chunk, max_retries=3):
    """
    Translates a single chunk with retry logic and fallback.
    Ensures translation actually happened by checking for English presence.
    """
    if not chunk or not chunk.strip():
        return ""
    
    # Try GoogleTranslator first, then MyMemory if fails
    translators = [
        GoogleTranslator(source='en', target='hi'),
        MyMemoryTranslator(source='en', target='hi')
    ]
    
    current_text = chunk
    for attempt in range(max_retries):
        try:
            # Use alternating translators on retries
            translator = translators[attempt % len(translators)]
            
            # Stagger slightly to avoid rate limits
            time.sleep(random.uniform(0.1, 0.4)) 
            
            translated = translator.translate(current_text)
            
            if translated and not contains_english(translated):
                return translated
                
            # If English is still there, try one more time with the *translated* result
            current_text = translated if translated else chunk
            time.sleep(1) 
            
        except Exception as e:
            print(f"Translation attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt) 
            
    return current_text # Final best effort

def translate_text(text, max_workers=10):
    """Orchestrates concurrent translation of a large block of text."""
    chunks = split_into_chunks(text, max_chars=1000) # Slightly larger chunks for full-text translation
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        translated_chunks = list(executor.map(translate_chunk, chunks))
    return " ".join([tc for tc in translated_chunks if tc])

