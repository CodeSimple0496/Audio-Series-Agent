from deep_translator import GoogleTranslator, MyMemoryTranslator
from concurrent.futures import ThreadPoolExecutor
import re
import time
import random

# Reuse translator instances to save resources
GOOGLE = GoogleTranslator(source='en', target='hi')
MYMEMORY = MyMemoryTranslator(source='en', target='hi')

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

def contains_too_much_english(text, threshold=0.15):
    """
    Returns True if more than threshold% of the text is English characters.
    Allows for proper nouns, numbers, and technical terms without triggering retries.
    """
    if not text:
        return False
    # Count only English alphabet characters
    eng_chars = len(re.findall(r'[a-zA-Z]', text))
    return (eng_chars / len(text)) > threshold

def translate_chunk(chunk, max_retries=3):
    """
    Translates a single chunk with retry logic, but optimized for speed on success.
    """
    if not chunk or not chunk.strip():
        return ""
    
    translators = [GOOGLE, MYMEMORY]
    current_text = chunk
    
    for attempt in range(max_retries):
        try:
            # 1. No sleep on the first attempt - maximum speed!
            if attempt > 0:
                # Stagger only if retrying to avoid further rate limits
                time.sleep(random.uniform(0.5, 1.5)) 
            
            translator = translators[attempt % len(translators)]
            translated = translator.translate(current_text)
            
            # 2. Use a smarter check to avoid unnecessary retries
            if translated and not contains_too_much_english(translated):
                return translated
            
            # If still needs translation, use the previous result as next input
            current_text = translated if (translated and len(translated) > 10) else chunk
            
        except Exception as e:
            print(f"Translation attempt {attempt + 1} speed-bump: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) 
            
    return current_text

def translate_text(text, max_workers=20):
    """Orchestrates high-speed concurrent translation."""
    chunks = split_into_chunks(text, max_chars=1000) 
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        translated_chunks = list(executor.map(translate_chunk, chunks))
    return " ".join([tc for tc in translated_chunks if tc])


