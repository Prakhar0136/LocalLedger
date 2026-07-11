from pydantic import BaseModel
from typing import Optional

class ReceiptRecord(BaseModel):
    """Strict schema for data extracted from a receipt image."""
    receipt_date: str  
    vendor_name: str
    total_amount: float
    confidence_score: Optional[int] = 100
    category: str = "Uncategorized"  