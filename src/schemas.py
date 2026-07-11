from pydantic import BaseModel
from typing import Optional

class ReceiptRecord(BaseModel):
    """Strict schema for data extracted from a receipt image."""
    receipt_date: str  # Format: YYYY-MM-DD
    vendor_name: str
    total_amount: float
    confidence_score: Optional[int] = 100