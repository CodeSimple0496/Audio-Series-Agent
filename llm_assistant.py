import re

class ScriptAssistant:
    def __init__(self, limit=100000):
        self.character_limit = limit

    def check_length(self, text):
        """Returns True if within limits, False otherwise."""
        if len(text) > self.character_limit:
            return False, f"Script exceeds {self.character_limit} characters (current: {len(text)}). Please split your input."
        return True, "Script length is within limits."

    def extract_names_heuristic(self, text):
        """
        A simple heuristic script to extract potential character names.
        Looks for capitalized words preceding dialogue or common actions.
        For a real production system, consider a small NER model.
        """
        # Very basic regex looking for Capitalized words followed by "said", "asked", etc.
        # Or words at the start of dialogue.
        pattern = r'([A-Z][a-z]+)\s+(?:said|asked|replied|shouted|whispered)'
        names = re.findall(pattern, text)
        
        # Deduplicate and count
        name_counts = {}
        for name in names:
            name_counts[name] = name_counts.get(name, 0) + 1
            
        # Return top 5 names
        sorted_names = sorted(name_counts.items(), key=lambda x: x[1], reverse=True)
        return [name for name, count in sorted_names[:5]]

    def suggest_voice_mapping(self, text):
        names = self.extract_names_heuristic(text)
        mapping = {}
        # Simple heuristic: alternating voices or picking from a list
        available_voices = ["Male", "Sweet Female", "Tense Male"]
        for i, name in enumerate(names):
            mapping[name] = available_voices[i % len(available_voices)]
            
        return mapping
