import sqlite3
import uuid
from langgraph.checkpoint.sqlite import SqliteSaver
from graph import build_graph

def run_auditor():
    db_path = "local_ledger.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    
    graph = build_graph().compile(
        checkpointer=memory, 
        interrupt_before=["ask_human"]
    )
    
    # Generate a unique ID for this specific run so old runs don't interfere
    run_id = f"audit_run_{uuid.uuid4().hex[:6]}"
    config = {"configurable": {"thread_id": run_id}}
    initial_state = {"errors": [], "retry_count": 0}
    
    print(f"Starting Local Ledger Auditor (Run ID: {run_id})...")
    
    for event in graph.stream(initial_state, config):
        pass
        
    snapshot = graph.get_state(config)
    
    if snapshot.next and snapshot.next[0] == "ask_human":
        print("\n" + "="*50)
        print("⚠️ SYSTEM HALTED: Unresolvable math mismatch.")
        print(f"Calculated: ${snapshot.values.get('calculated_total')} | Expected: ${snapshot.values.get('statement_total')}")
        print("="*50)
        
        user_input = input("\nPlease provide a resolution note to override: ")
        
        graph.update_state(config, {"human_notes": user_input})
        
        print("\nResuming graph execution...")
        for event in graph.stream(None, config):
            pass

if __name__ == "__main__":
    run_auditor()