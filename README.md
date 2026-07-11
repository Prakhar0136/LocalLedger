flowchart TB
    %% Styling Definitions
    classDef user fill:#e1bee7,stroke:#4a148c,stroke-width:2px,color:#000
    classDef storage fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000
    classDef core fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000
    classDef agents fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    classDef external fill:#cfd8dc,stroke:#263238,stroke-width:2px,color:#000

    %% UI Node
    CLI([PowerShell CLI / Human-in-the-Loop]):::user

    %% Storage Layer
    subgraph StorageLayer [Local Storage Layer]
        FS[(Local File System\nInbox / Reports)]:::storage
        SQL[(SQLite Checkpoint\nState Saver)]:::storage
        Chroma[(ChromaDB\nVector Memory)]:::storage
        MD[budget_goals.md\nPolicy Document]:::storage
    end

    %% Core Application Layer
    subgraph CoreLayer [Orchestration Layer]
        LG{LangGraph State Machine}:::core
        State[AuditState TypedDict]:::core
        Tools[Pandas Math Guardrails]:::core
    end

    %% Agent Layer
    subgraph AgentLayer [Intelligence Layer]
        Vision[Gemini Extraction Agent]:::agents
        MemEngine[Memory Pattern Engine]:::agents
        RAG[LlamaIndex Policy Engine]:::agents
    end

    %% External APIs
    subgraph APILayer [External Cloud Services]
        GeminiCloud((Google Gemini API)):::external
    end

    %% Connections
    CLI <-->|Interrupts & Prompts| LG
    FS -->|Raw CSVs & Images| LG
    LG -->|Markdown Output| FS
    
    LG <-->|Saves/Loads Thread| SQL
    LG <-->|Updates/Reads| State
    LG <-->|Invokes| Tools
    
    LG <-->|Passes Images| Vision
    LG <-->|Categorizes Vendors| MemEngine
    LG <-->|Audits Rules| RAG
    
    MemEngine <-->|Read/Write Vectors| Chroma
    RAG <-->|Reads Context| MD
    
    Vision <-->|Vision LLM Call| GeminiCloud
    RAG <-->|Embeddings/LLM Call| GeminiCloud




flowchart TD
    %% Styling Definitions
    classDef startend fill:#000,stroke:#fff,stroke-width:2px,color:#fff
    classDef process fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef check fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef alert fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef logic fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px

    Start((START)):::startend --> Ingest[Node 1: Ingest Files]:::process
    
    Ingest -->|Raw Data| Extract[Node 2: Process Receipts]:::process
    Extract -->|JSON Receipts| Categorize[Node 3: Categorize]:::process
    Categorize -->|Categorized Receipts| Policy[Node 4: Policy Check]:::process
    Policy -->|Policy Alerts| Audit[Node 5: Math Audit]:::check
    
    Audit -->|Calculated Totals| Router{Condition: Match?}:::logic
    
    %% Routing Logic
    Router -->|True| Report[Node 8: Write Report]:::process
    Router -->|False & Retries < 2| Reconcile[Node 6: Reconcile Loop]:::alert
    Router -->|False & Retries >= 2| Breakpoint[Interrupt: Ask Human]:::alert
    
    %% Fallback Loops
    Reconcile -->|Increment Retry Count| Extract
    Breakpoint -.->|Terminal Prompt| Human[Node 7: Human Override]:::process
    Human -->|Insert Notes| Report
    
    Report -->|latest_audit.md| Finish((END)):::startend