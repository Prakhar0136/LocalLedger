# 🧾 Local Ledger: Autonomous AI Budget Auditor

> An AI-powered local financial auditing system that automatically processes bank statements and receipt images, validates spending against custom budget rules, and generates mathematically verified audit reports.

Built with **LangGraph**, **Google Gemini Vision**, **LlamaIndex**, **ChromaDB**, **SQLite**, and **Pandas**.

---

# ✨ Features

- 📄 **Multi-Modal Data Ingestion**
  - Processes CSV bank statements, PDF receipts, and receipt images.
  - Uses Gemini Vision with structured Pydantic schemas for reliable extraction.

- 🤖 **Agentic Workflow**
  - Powered by LangGraph state machines.
  - Deterministic execution instead of a simple chatbot pipeline.

- 🔄 **Self-Correcting Audit Loop**
  - Automatically retries extraction when totals don't match.
  - Prevents incorrect financial reports.

- 👨‍💻 **Human-in-the-Loop**
  - Pauses execution when reconciliation fails.
  - Allows manual intervention before continuing.

- 🧠 **Long-Term Memory**
  - ChromaDB stores vendor embeddings.
  - Learns transaction categories over time.

- 📚 **Policy-Based Auditing**
  - Reads plain-English budget rules from a Markdown file.
  - Uses LlamaIndex RAG to detect spending violations.

- 🧮 **Deterministic Math**
  - Pandas performs all financial calculations.
  - Eliminates LLM math hallucinations.

---

# 🏗️ System Architecture

```mermaid
flowchart TB

CLI([PowerShell CLI<br/>Human-in-the-Loop])

subgraph Storage["Local Storage Layer"]
    FS[(Local File System<br/>Inbox / Reports)]
    SQL[(SQLite Checkpoint<br/>State Saver)]
    Chroma[(ChromaDB<br/>Vector Memory)]
    MD["budget_goals.md<br/>Policy Document"]
end

subgraph Core["Orchestration Layer"]
    LG{{LangGraph<br/>State Machine}}
    State["AuditState<br/>TypedDict"]
    Tools["Pandas<br/>Math Guardrails"]
end

subgraph Agents["Intelligence Layer"]
    Vision["Gemini Extraction Agent"]
    Memory["Memory Pattern Engine"]
    RAG["LlamaIndex Policy Engine"]
end

subgraph Cloud["External Services"]
    Gemini(("Google Gemini API"))
end

CLI --> LG
LG --> CLI

FS --> LG
LG --> FS

LG --> SQL
SQL --> LG

LG --> State
State --> LG

LG --> Tools

LG --> Vision
Vision --> LG

LG --> Memory
Memory --> LG

LG --> RAG
RAG --> LG

Memory --> Chroma
Chroma --> Memory

RAG --> MD

Vision --> Gemini
RAG --> Gemini

style CLI fill:#e1bee7,stroke:#4a148c,stroke-width:2px

style FS fill:#bbdefb
style SQL fill:#bbdefb
style Chroma fill:#bbdefb
style MD fill:#bbdefb

style LG fill:#c8e6c9
style State fill:#c8e6c9
style Tools fill:#c8e6c9

style Vision fill:#ffe0b2
style Memory fill:#ffe0b2
style RAG fill:#ffe0b2

style Gemini fill:#cfd8dc
```

---

# 🔄 LangGraph Workflow

```mermaid
flowchart TD

Start((START))

Ingest["1. Ingest Files"]

Extract["2. Extract Receipt Data"]

Categorize["3. Categorize Expenses"]

Policy["4. Policy Validation"]

Audit["5. Mathematical Audit"]

Decision{"Totals Match?"}

Retry["6. Reconciliation Loop"]

Human["7. Human Review"]

Report["8. Generate Audit Report"]

End((END))

Start --> Ingest
Ingest --> Extract
Extract --> Categorize
Categorize --> Policy
Policy --> Audit
Audit --> Decision

Decision -- Yes --> Report
Decision -- Retry --> Retry
Retry --> Extract
Decision -- Failed --> Human
Human --> Report
Report --> End

style Start fill:#000,color:#fff
style End fill:#000,color:#fff

style Ingest fill:#fff3e0
style Extract fill:#fff3e0
style Categorize fill:#fff3e0
style Policy fill:#fff3e0
style Report fill:#fff3e0

style Audit fill:#e3f2fd

style Decision fill:#f3e5f5

style Retry fill:#ffebee
style Human fill:#ffebee
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/LocalLedger.git
cd LocalLedger
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
```

---

# 📁 Project Structure

```text
LocalLedger/
│
├── data/
│   ├── inbox/
│   ├── processed/
│   ├── reports/
│   └── chroma_db/
│
├── src/
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── extractors.py
│   ├── memory.py
│   ├── policy.py
│   ├── tools.py
│   ├── schemas.py
│   └── file_handler.py
│
├── .env
├── requirements.txt
└── README.md
```

---

# 🚀 Usage

## Step 1 — Define Budget Rules

Edit:

```text
data/inbox/budget_goals.md
```

Example:

```text
Monthly Food Budget: ₹8000

Alert if Shopping exceeds ₹5000.

Notify if Entertainment exceeds ₹3000.

Flag any transaction above ₹10000.
```

---

## Step 2 — Add Financial Documents

Place the following inside:

```text
data/inbox/
```

Example:

```
bank_statement.csv
receipt1.jpg
receipt2.png
receipt3.pdf
budget_goals.md
```

---

## Step 3 — Run the Auditor

```bash
python src/main.py
```

---

## Step 4 — Review the Report

The generated audit will be available at:

```text
data/reports/latest_audit.md
```

---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python |
| Agent Framework | LangGraph |
| Vision Model | Google Gemini 2.5 Flash |
| Retrieval | LlamaIndex |
| Vector Database | ChromaDB |
| Local Database | SQLite |
| Validation | Pydantic |
| Data Processing | Pandas |
| Fuzzy Matching | RapidFuzz |
| Environment | python-dotenv |

---

# 📌 Future Improvements

- Multi-bank statement support
- OCR confidence scoring
- Expense trend visualization
- Local LLM support via Ollama
- Email audit reports
- Interactive Streamlit dashboard
- Monthly spending analytics
- Recurring subscription detection

---

# 📄 License

This project is licensed under the **MIT License**.

---

# ⭐ If you found this project helpful, consider giving it a star!