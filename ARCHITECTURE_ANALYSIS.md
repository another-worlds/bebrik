# Telegram Multi-Agent AI Bot - Architecture Analysis & Dataflow

## Overall Application Structure

```mermaid
graph TB
    %% External Services
    TG[Telegram API] 
    XAI[xAI Grok API]
    HF[HuggingFace API<br/>intfloat/multilingual-e5-large]
    MONGO[(MongoDB Atlas<br/>Vector Store)]
    
    %% Main Application Components
    MAIN[main.py<br/>FastAPI App]
    BOT[core/bot.py<br/>TelegramBot]
    
    %% Handlers
    MSG[handlers/message.py<br/>MessageHandler]
    DOC[handlers/document.py<br/>DocumentHandler]
    
    %% Services
    EMB[services/embedding.py<br/>HuggingFaceEmbeddingService]
    
    %% Database
    DB[database/mongodb.py<br/>MongoDB Driver]
    
    %% Models
    MDOC[models/document.py<br/>Document Model]
    MMSG[models/message.py<br/>Message Model]
    
    %% Utils
    LANG[utils/language.py<br/>Language Detection]
    TEXT[utils/text.py<br/>Text Processing]
    
    %% Configuration
    CONFIG[config.py<br/>Environment Config]
    
    %% User Interactions
    USER[👤 Telegram User]
    
    %% Main Data Flow
    USER -->|Messages/Files| TG
    TG -->|Webhook/Polling| BOT
    BOT -->|Text Messages| MSG
    BOT -->|Document Upload| DOC
    
    %% Message Processing Flow
    MSG -->|Queue Message| DB
    MSG -->|Get Context| DB
    MSG -->|Generate Response| XAI
    MSG -->|Document Query| DOC
    MSG -->|Language Detection| LANG
    MSG -->|Text Normalization| TEXT
    MSG -->|Store Response| DB
    MSG -->|Send Reply| BOT
    BOT -->|Reply| TG
    TG -->|Response| USER
    
    %% Document Processing Flow
    DOC -->|Extract Text| LANG
    DOC -->|Chunk Text| TEXT
    DOC -->|Generate Embeddings| EMB
    EMB -->|API Request| HF
    HF -->|1024-dim Vectors| EMB
    EMB -->|Embeddings| DOC
    DOC -->|Store Document| DB
    DOC -->|Create Document Model| MDOC
    DOC -->|Vector Search| DB
    DB -->|Similar Chunks| DOC
    DOC -->|Context| MSG
    
    %% Database Operations
    DB -->|Read/Write| MONGO
    MONGO -->|Vector Search| DB
    
    %% Configuration Dependencies
    CONFIG -->|API Keys| EMB
    CONFIG -->|API Keys| XAI
    CONFIG -->|Settings| BOT
    CONFIG -->|DB URI| DB
    
    %% FastAPI Integration
    MAIN -->|Lifespan Management| BOT
    MAIN -->|Health Endpoint| USER
    
    %% Styling
    classDef external fill:#ff9999,stroke:#333,stroke-width:2px
    classDef core fill:#99ccff,stroke:#333,stroke-width:2px
    classDef handler fill:#99ff99,stroke:#333,stroke-width:2px
    classDef service fill:#ffcc99,stroke:#333,stroke-width:2px
    classDef data fill:#cc99ff,stroke:#333,stroke-width:2px
    classDef util fill:#ffff99,stroke:#333,stroke-width:2px
    
    class TG,XAI,HF,MONGO external
    class MAIN,BOT,CONFIG core
    class MSG,DOC handler
    class EMB service
    class DB,MDOC,MMSG data
    class LANG,TEXT util
```

## Detailed Component Interaction Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant T as Telegram API
    participant B as TelegramBot
    participant M as MessageHandler
    participant D as DocumentHandler
    participant E as EmbeddingService
    participant H as HuggingFace API
    participant DB as MongoDB
    participant X as xAI Grok
    
    %% Message Flow
    U->>T: Send text message
    T->>B: Receive message
    B->>M: Process message
    M->>DB: Queue message
    M->>DB: Get conversation history
    M->>D: Query documents
    D->>E: Generate query embedding
    E->>H: API request (feature-extraction)
    H-->>E: 1024-dim vector
    E-->>D: Query embedding
    D->>DB: Vector similarity search
    DB-->>D: Relevant document chunks
    D-->>M: Document context
    M->>X: Generate response with context
    X-->>M: AI response
    M->>DB: Store response
    M-->>B: Return response
    B->>T: Send reply
    T->>U: Deliver response
    
    %% Document Upload Flow
    U->>T: Upload document
    T->>B: Receive document
    B->>D: Process document
    D->>D: Extract & chunk text
    D->>E: Generate embeddings
    E->>H: Batch embedding request
    H-->>E: Document embeddings
    E-->>D: Embedding vectors
    D->>DB: Store document with embeddings
    D-->>B: Processing complete
    B->>T: Confirmation message
    T->>U: Upload success
```

## Key Architecture Patterns

```mermaid
graph LR
    %% Architectural Patterns
    subgraph "🏗️ Architecture Patterns"
        RAG[RAG Pattern<br/>Retrieval-Augmented Generation]
        ASYNC[Async/Await<br/>Non-blocking I/O]
        QUEUE[Message Queue<br/>Batch Processing]
        VECTOR[Vector Search<br/>Semantic Similarity]
    end
    
    subgraph "🔧 Design Patterns"
        SINGLE[Singleton Pattern<br/>Service Instances]
        FACTORY[Factory Pattern<br/>Document Loaders]
        STRATEGY[Strategy Pattern<br/>Embedding Services]
        OBSERVER[Observer Pattern<br/>Message Processing]
    end
    
    subgraph "🌐 Integration Patterns"
        API[API Gateway<br/>FastAPI]
        WEBHOOK[Webhook/Polling<br/>Telegram Integration]
        CLIENT[HTTP Client<br/>External APIs]
        PERSIST[Data Persistence<br/>MongoDB]
    end
```

## Technology Stack Overview

```mermaid
mindmap
  root((Telegram Bot))
    Core Technologies
      Python 3.11
      FastAPI
      AsyncIO
      Docker
    AI & ML
      xAI Grok
      HuggingFace Embeddings
      LangChain
      Vector Search
    Storage
      MongoDB Atlas
      Vector Database
      File Storage
    Communication
      Telegram Bot API
      HTTP/HTTPS
      WebHooks
    Development
      Virtual Environment
      Docker Compose
      Health Monitoring
      Logging
```
