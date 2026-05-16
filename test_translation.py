from translator import translate_text, split_into_chunks

text = """
John said, "Hello there! How are you doing today?" 
Mary replied, "I am doing well, thank you for asking."
John asked, "Would you like to go to the park later?"
Mary answered, "I would love to, but I have to finish my homework first."
"""

print("Original Text:")
print(text)
print("-" * 20)

print("Split Chunks:")
chunks = split_into_chunks(text, max_chars=50)
for i, chunk in enumerate(chunks):
    print(f"[{i}]: {chunk}")

print("-" * 20)
print("Translated Text:")
translated = translate_text(text, max_workers=2)
print(translated)
