from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances

import faiss
import numpy as np


class ScentSearch:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the scent search system with a sentence transformer model.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.scent_descriptions = []
        self.scent_vectors = None
        self.index = None
        print(f"Initialized ScentSearch with model: {model_name}")
    
    def add_scents(self, scent_descriptions):
        """
        Add scent descriptions to the search index.
        
        Args:
            scent_descriptions (list): List of scent description strings
        """
        self.scent_descriptions = scent_descriptions
        self.scent_vectors = self.model.encode(scent_descriptions)
        
        # Create and populate FAISS index
        dimension = self.scent_vectors.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.scent_vectors)
        
        print(f"Added {len(scent_descriptions)} scents to index")
        print(f"Vector shape: {self.scent_vectors.shape}")
    
    def search(self, query, k=1):
        """
        Search for the closest scents to the query.
        
        Args:
            query (str): Query string
            k (int): Number of results to return
            
        Returns:
            list: List of tuples (scent_description, distance)
        """
        # Encode the query
        query_vector = self.model.encode([query])
        
        # Search the index
        distances, indices = self.index.search(query_vector, k)
        
        # Format results
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            distance = distances[0][i]
            results.append((self.scent_descriptions[idx], distance))
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize the search system
    searcher = ScentSearch()
    
    # Define scent descriptions
    scents = [
        'lavender floral soft soothing',
        'lemongrass fresh grassy lemon herbal',
        'orange fresh citrus tangy sweet',
        'raspberry berry earthy herbal fresh',
        'garlic pungent wasabi spicy'
    ]
    
    # Add scents to the index
    searcher.add_scents(scents)
    
    # Perform a search
    query = 'garlic'
    results = searcher.search(query, k=2)
    
    # Display results
    print(f"\nSearch query: '{query}'")
    print("Results:")
    for i, (scent, distance) in enumerate(results):
        print(f"{i+1}. {scent} (distance: {distance:.4f})")