import sqlite3
import pandas as pd
from langgraph.graph import StateGraph, START, END

from state import AuditState
from file_handler import FileSystemManager
from extractors import ExtractionAgents
from tools import calculate_total_spending, verify_statement_balance
from memory import CategoryMemory
from policy import PolicyEngine  # <-- NEW IMPORT

file_manager = FileSystemManager()
extractors = ExtractionAgents()
category_db = CategoryMemory()
policy_engine = PolicyEngine()   # <-- NEW INITIALIZATION

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

def categorize_node(state: AuditState) -> dict:
    print("\n[Node: Categorizing Receipts]")
    receipts = state.get("receipts", [])
    
    for r in receipts:
        cat = category_db.predict_category(r.vendor_name)
        r.category = cat
        print(f"  -> '{r.vendor_name}' classified as: {cat}")
        
    return {"receipts": receipts}

# --- NEW POLICY CHECK NODE ---
def policy_check_node(state: AuditState) -> dict:
    print("\n[Node: Checking Budget Policies via RAG]")
    receipts = state.get("receipts", [])
    alerts = []
    
    for r in receipts:
        eval_result = policy_engine.evaluate_transaction(r.vendor_name, r.category, r.total_amount)
        if "PASS" not in eval_result.upper():
            alerts.append(f"**{r.vendor_name}**: {eval_result}")
            print(f"  -> ⚠️ Flagged: {r.vendor_name} (${r.total_amount})")
        else:
            print(f"  -> {r.vendor_name} passed budget policies.")
            
    return {"policy_alerts": alerts}

def math_audit_node(state: AuditState) -> dict:
    print("\n[Node: Auditing Math against Statement]")
    
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
    print(f"\n[Node: Applying Human Override]")
    print(f"  -> Human Note: {state.get('human_notes')}")
    return {"audit_match": True}

def write_report_node(state: AuditState) -> dict:
    print("\n[Node: Writing Report]")
    
    if state.get("human_notes"):
        match_text = f"MANUALLY RESOLVED - Note: {state.get('human_notes')}"
    else:
        match_text = "PASSED" if state.get("audit_match") else f"FAILED (Diff: ${state.get('audit_difference')})"
    
    report_content = f"# Local Ledger Audit Report\n\n"
    report_content += f"**Audit Status:** {match_text}\n"
    report_content += f"**Calculated Total:** ${state.get('calculated_total', 0)}\n"
    report_content += f"**Statement Expected:** ${state.get('statement_total', 0)}\n\n"
    
    # NEW: Add Policy Alerts Section
    alerts = state.get("policy_alerts", [])
    if alerts:
        report_content += "## ⚠️ Budget Policy Violations\n"
        for alert in alerts:
            report_content += f"- {alert}\n"
        report_content += "\n"
    
    report_content += "## Processed Receipts\n"
    for r in state.get("receipts", []):
        report_content += f"- {r.receipt_date} | **{r.vendor_name}** ({r.category}): ${r.total_amount}\n"
        
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
    return "ask_human"

def build_graph():
    builder = StateGraph(AuditState)
    
    builder.add_node("ingest", ingest_files_node)
    builder.add_node("process", process_receipts_node)
    builder.add_node("categorize", categorize_node)
    builder.add_node("policy_check", policy_check_node) # <-- NEW
    builder.add_node("audit", math_audit_node)
    builder.add_node("reconcile", reconcile_node)
    builder.add_node("ask_human", ask_human_node)
    builder.add_node("report", write_report_node)
    
    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "process")
    builder.add_edge("process", "categorize")
    builder.add_edge("categorize", "policy_check")      # <-- ROUTED HERE
    builder.add_edge("policy_check", "audit")           # <-- ROUTED TO AUDIT
    
    builder.add_conditional_edges(
        "audit", 
        route_after_audit, 
        {"report": "report", "reconcile": "reconcile", "ask_human": "ask_human"}
    )
    
    builder.add_edge("reconcile", "process")
    builder.add_edge("ask_human", "report")
    builder.add_edge("report", END)
    
    return builder