import pandas as pd
from langchain_core.tools import tool
from typing import List, Dict, Any

@tool
def calculate_total_spending(amounts: List[float]) -> float:
    """
    Calculates the exact sum of an array of transaction amounts.
    Always use this tool for arithmetic instead of calculating mentally.
    """
    series = pd.Series(amounts)
    return round(float(series.sum()), 2)

@tool
def verify_statement_balance(calculated_total: float, reported_total: float) -> Dict[str, Any]:
    """
    Compares the calculated sum of transactions against the bank statement's reported total.
    Returns a dictionary indicating if they match, and the difference if they do not.
    """
    difference = round(abs(calculated_total - reported_total), 2)
    is_match = difference < 0.01
    
    return {
        "match": is_match,
        "calculated_total": calculated_total,
        "reported_total": reported_total,
        "difference": difference
    }