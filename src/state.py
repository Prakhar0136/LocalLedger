from typing import TypedDict, List, Dict, Annotated, Optional
from pathlib import Path
import operator
from schemas import ReceiptRecord

class AuditState(TypedDict):
    """The shared memory dictionary that flows through our LangGraph nodes."""
    inbox_files: Dict[str, List[Path]]
    receipts: List[ReceiptRecord]
    
    calculated_total: float
    statement_total: float
    audit_match: bool
    audit_difference: float
    
    report_path: str
    
    errors: Annotated[List[str], operator.add]
    retry_count: int
    human_notes: Optional[str]
    policy_alerts: List[str] 