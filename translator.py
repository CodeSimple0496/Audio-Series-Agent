from deep_translator import GoogleTranslator, MyMemoryTranslator
from concurrent.futures import ThreadPoolExecutor
import re
import time
import random

# Standardize Contextual Blocks for High-Accuracy Translation
# Translating in larger chunks ensures better Hindi grammar
TRANSLATION_BLOCK_SIZE = 2000 
TTS_CHUNK_SIZE = 500

# Reuse translator instances
GOOGLE = GoogleTranslator(source='en', target='hi')
MYMEMORY = MyMemoryTranslator(source='en', target='hi')

def split_into_chunks(text, max_chars=TRANSLATION_BLOCK_SIZE):
    """
    Split text into chunks of at most max_chars, trying to split on sentence boundaries.
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
    Translates a single chunk with retry logic, optimized for accuracy.
    """
    if not chunk or not chunk.strip():
        return ""
    
    translators = [GOOGLE, MYMEMORY]
    current_text = chunk
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(random.uniform(0.5, 1.5)) 
            
            translator = translators[attempt % len(translators)]
            translated = translator.translate(current_text)
            
            # High-accuracy check: prioritize Google result if it's mostly Hindi
            if translated and not contains_too_much_english(translated):
                return translated
            
            # If still needs translation, try again
            current_text = translated if (translated and len(translated) > 10) else chunk
            
        except Exception as e:
            print(f"Translation sync error {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) 
            
    return current_text

def translate_text(text, max_workers=20):
    """Orchestrates contextual translation before splitting into TTS chunks."""
    # Use larger Contextual Blocks for higher translation accuracy
    context_blocks = split_into_chunks(text, max_chars=TRANSLATION_BLOCK_SIZE) 
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        translated_blocks = list(executor.map(translate_chunk, context_blocks))
    
    # Return the full translated text to be reconsidered for TTS chunks
    return " ".join([tb for tb in translated_blocks if tb])



