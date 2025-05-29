from typing import Dict, Optional
import numpy as np
from .functions import get_cosine_similarity
class Product:
    def __init__(self, name: str, description: str, category: str, url: str, model, embedding: Optional[np.ndarray] = None):
        self.name = name
        self.category = category
        self.description = description
        self.url = url
        self.model = model
        self.embedding = embedding

    def index(self):
        if self.embedding is None:
            self.embedding = self.model.encode(str(self), show_progress_bar=False, convert_to_numpy=True)

    def query(self, query_embedding:np.ndarray):
        return get_cosine_similarity(self.embedding, query_embedding)

    def show(self):
        return {
            "name": self.name,
            "category": self.category,
            "desc": self.description,
            "url": self.url
        }

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'category': self.category,
            'embedding': self.embedding.tolist() if self.embedding is not None else None
        }

    @classmethod
    def from_dict(cls, data: Dict, model) -> 'Product':
        embedding = np.array(data['embedding']) if data['embedding'] is not None else None
        return cls(
            name=data['name'],
            description=data['description'],
            category=data['category'],
            url=data['url'],
            model=model,
            embedding=embedding
        )

    def __str__(self) -> str:
        desc = self.description.rstrip('.')
        return f"{self.name}: {desc} (website: {self.url})."
