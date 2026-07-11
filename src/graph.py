import sqlite3
import pandas as pd
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from state import AuditState
from file_handler import FileSystemManager
from extractors import ExtractionAgents
from tools import calculate_total_spending, verify_statement_balance

file_manager = FileSystemManager()
extractors = ExtractionAgents()

def ingest_files_node(state: AuditState) -> dict:
    print("\n[Node: Ingesting Files]")
    return {"inbox_files": file_manager.scan_inbox(), "retry_count": state.get("retry_count", 0)}
    
def process_receipts_node(state: AuditState) -> dict:
    print(f"[Node: Processing Receipts (Attempt {state.get('retry_count', 0) + 1})]")
    images = state.get("inbox_files", {}).get("images", [])
    
    parsed_receipts = []
    for img_path in images:
        try:
            parsed_receipts.append(extractors.process_receipt_image(img_path))
        except Exception as e:
            return {"errors": [f"Extraction failed on {img_path.name}: {str(e)}"]}
            
    return {"receipts": parsed_receipts}
    
def math_audit_node(state: AuditState) -> dict:
    print("[Node: Auditing Math against Statement]")
    
    receipts = state.get("receipts", [])
    amounts = [r.total_amount for r in receipts] if receipts else [0.0]
    calc_total = calculate_total_spending.invoke({"amounts": amounts})
    
    statement_total = 0.0
    files = state.get("inbox_files", {})
    if files.get("csv"):
        try:
            df = pd.read_csv(files["csv"][0])
            statement_total = round(float(df['Amount'].sum()), 2)
        except Exception:
            pass
            
    audit_result = verify_statement_balance.invoke({
        "calculated_total": calc_total,
        "reported_total": statement_total
    })
    
    return {
        "calculated_total": audit_result["calculated_total"],
        "statement_total": audit_result["reported_total"],
        "audit_match": audit_result["match"],
        "audit_difference": audit_result["difference"]
    }

def reconcile_node(state: AuditState) -> dict:
    print(f"\n[Node: Reconcile Loop Triggered!] Mismatch of ${state.get('audit_difference')}")
    return {"retry_count": state.get("retry_count", 0) + 1}

def ask_human_node(state: AuditState) -> dict:
    """This node only runs after the human provides input."""
    print(f"\n[Node: Applying Human Override]")
    print(f"  -> Human Note: {state.get('human_notes')}")
    # Force the audit to pass so the report can generate cleanly
    return {"audit_match": True}

def write_report_node(state: AuditState) -> dict:
    print("\n[Node: Writing Report]")
    
    # Check if a human intervened
    if state.get("human_notes"):
        match_text = f"MANUALLY RESOLVED - Note: {state.get('human_notes')}"
    else:
        match_text = "PASSED" if state.get("audit_match") else f"FAILED (Diff: ${state.get('audit_difference')})"
    
    report_content = f"# Local Ledger Audit Report\n\n"
    report_content += f"**Audit Status:** {match_text}\n"
    report_content += f"**Calculated Total:** ${state.get('calculated_total', 0)}\n"
    report_content += f"**Statement Expected:** ${state.get('statement_total', 0)}\n\n"
    
    report_content += "## Processed Receipts\n"
    for r in state.get("receipts", []):
        report_content += f"- {r.receipt_date} | **{r.vendor_name}**: ${r.total_amount}\n"
        
    report_path = file_manager.reports_dir / "latest_audit.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"  -> Report saved to {report_path}")
    return {"report_path": str(report_path)}

def route_after_audit(state: AuditState) -> str:
    if state.get("audit_match"):
        return "report"
    if state.get("retry_count", 0) < 2:
        return "reconcile"
    # NEW: Instead of forcing a report, route to the human
    return "ask_human"

def build_graph():
    builder = StateGraph(AuditState)
    
    builder.add_node("ingest", ingest_files_node)
    builder.add_node("process", process_receipts_node)
    builder.add_node("audit", math_audit_node)
    builder.add_node("reconcile", reconcile_node)
    builder.add_node("ask_human", ask_human_node)
    builder.add_node("report", write_report_node)
    
    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "process")
    builder.add_edge("process", "audit")
    
    builder.add_conditional_edges(
        "audit", 
        route_after_audit, 
        {"report": "report", "reconcile": "reconcile", "ask_human": "ask_human"}
    )
    
    builder.add_edge("reconcile", "process")
    builder.add_edge("ask_human", "report")
    builder.add_edge("report", END)
    
    return builder