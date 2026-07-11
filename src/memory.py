import chromadb
from pathlib import Path

class CategoryMemory:
    """Manages long-term learning for expense categorization using vector embeddings."""
    def __init__(self):
        base_dir = Path(__file__).parent.parent
        db_path = base_dir / "data" / "chroma_db"
        
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(
            name="vendor_categories"
        )

    def learn_rule(self, vendor_name: str, category: str):
        """Saves a new categorization rule to long-term memory."""
        doc_id = vendor_name.lower().replace(" ", "_").replace(",", "")
        
        self.collection.upsert(
            documents=[vendor_name],
            metadatas=[{"category": category}],
            ids=[doc_id]
        )
        print(f"[Memory] Learned: '{vendor_name}' -> {category}")

    def predict_category(self, vendor_name: str) -> str:
        """Finds the closest matching vendor in memory and returns its category."""
        if self.collection.count() == 0:
            return "Uncategorized"

        results = self.collection.query(
            query_texts=[vendor_name],
            n_results=1
        )
        
        if results['distances'] and len(results['distances'][0]) > 0:
            distance = results['distances'][0][0]
            if distance < 1.0: 
                return results['metadatas'][0][0]['category']
                
        return "Uncategorized"