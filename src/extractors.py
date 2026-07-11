import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rapidfuzz import fuzz

from schemas import ReceiptRecord

load_dotenv()

class ExtractionAgents:
    """Agents responsible for pulling structured data from raw files."""
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from the .env file.")
        self.client = genai.Client(api_key=api_key)
        
    def process_receipt_image(self, image_path: Path) -> ReceiptRecord:
        """Uses Vision AI to extract structured data from a receipt image."""
        prompt = "Extract the date (YYYY-MM-DD), vendor name, and exact total amount from this receipt."
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        mime_type = 'image/png' if str(image_path).lower().endswith('.png') else 'image/jpeg'
            
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReceiptRecord,
                temperature=0.0
            )
        )
        
        return ReceiptRecord.model_validate_json(response.text)
        
    def match_receipt_to_transaction(self, receipt_vendor: str, bank_statement_descriptions: list[str]) -> str:
        """Uses fuzzy matching to find the closest bank transaction for a receipt."""
        best_match = None
        highest_score = 0
        
        for desc in bank_statement_descriptions:
            score = fuzz.partial_ratio(receipt_vendor.lower(), desc.lower())
            if score > highest_score:
                highest_score = score
                best_match = desc
                
        return best_match   