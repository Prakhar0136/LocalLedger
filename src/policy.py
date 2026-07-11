import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

class PolicyEngine:
    """Uses Agentic RAG to check transactions against user-defined plain English rules."""
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing from .env")
            
        # Configure LlamaIndex to use Gemini instead of the default OpenAI
        Settings.llm = Gemini(
            model="gemini-3.5-flash",
            api_key=api_key
        )
        
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        self.base_dir = Path(__file__).parent.parent
        self.goals_file = self.base_dir / "data" / "inbox" / "budget_goals.md"
        
        if not self.goals_file.exists():
            self.goals_file.write_text("# Budget Policies\n\nNo rules defined yet.")
        
        # Load the markdown file into the RAG vector store
        documents = SimpleDirectoryReader(input_files=[str(self.goals_file)]).load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        self.query_engine = self.index.as_query_engine()

    def evaluate_transaction(self, vendor: str, category: str, amount: float) -> str:
        """Queries the budget goals to see if a transaction violates any rules."""
        prompt = f"""
Transaction

Vendor: {vendor}
Category: {category}
Amount: ${amount:.2f}

Based ONLY on the budget policies in the retrieved context:

- If this transaction violates a policy, explain why in one short sentence.
- Otherwise respond with exactly:

PASS
"""
        response = self.query_engine.query(prompt)
        return str(response).strip()
