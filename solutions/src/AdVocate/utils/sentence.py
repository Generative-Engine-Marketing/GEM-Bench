import numpy as np
class Sentence:
    """Class representing a sentence with its embedding"""
    def __init__(self, sentence: str, embedding_model, mk_embd = True):
        self.sentence = sentence
        self.model = embedding_model
        if mk_embd:
            self.embedding = self.get_embedding()
        
    def get_embedding(self) -> np.ndarray:
        """Get embedding for the sentence"""
        return self.model.encode(self.sentence, convert_to_numpy=True, show_progress_bar=False)
    
    def __str__(self) -> str:
        """String representation of the sentence"""
        return f"Sentence(sentence='{self.sentence[:50]}...')"
    
    def to_string(self) -> str:
        """String representation of the sentence"""
        return self.sentence