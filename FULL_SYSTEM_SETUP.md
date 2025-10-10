# 🚀 Complete Advanced Autohire System Setup

**Full-Stack Multi-Agent Job Application System**
With: LangChain, LangGraph, AutoGen, LlamaIndex, ChromaDB, Neo4j, Langfuse

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOHIRE FULL SYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   LangChain  │  │  LangGraph   │  │   AutoGen    │         │
│  │  (Agents)    │  │  (Workflow)  │  │  (Collab)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  LlamaIndex  │  │   ChromaDB   │  │    Neo4j     │         │
│  │    (RAG)     │  │  (Vectors)   │  │   (Graph)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Langfuse   │  │  PostgreSQL  │  │    Redis     │         │
│  │  (Tracing)   │  │    (Data)    │  │   (Cache)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 What Each Framework Does

### **LangChain** - Agent Framework
- **Purpose**: Provides the agent structure and tool integration
- **Usage**: Orchestrates agent behavior, tool calling, memory
- **In Autohire**: Connects agents to Playwright, CV generator, job platforms

### **LangGraph** - State Machine Workflow
- **Purpose**: Creates cyclic, reflective workflows with checkpoints
- **Usage**: Plan → Code → Execute → Observe → Reflect → Loop
- **In Autohire**: Manages agent workflow, saves state to PostgreSQL

### **AutoGen** - Multi-Agent Collaboration
- **Purpose**: Enables multiple agents to collaborate and debate
- **Usage**: Planner, Coder, Executor agents communicate
- **In Autohire**: Agents discuss best approach, code review, retry logic

### **LlamaIndex** - RAG (Retrieval-Augmented Generation)
- **Purpose**: Retrieves relevant context from vector store
- **Usage**: Query past successful job searches, automation patterns
- **In Autohire**: "Last time LinkedIn login worked, button was X"

### **ChromaDB** - Vector Embeddings Store
- **Purpose**: Stores semantic embeddings for similarity search
- **Usage**: Converts text to vectors, finds similar past experiences
- **In Autohire**: Stores successful automation patterns, job matches

### **Neo4j** - Knowledge Graph Database
- **Purpose**: Stores relationships between entities
- **Usage**: Job → Company → Skills → Location relationships
- **In Autohire**: "Which companies hire for these skills in Melbourne?"

### **Langfuse** - LLM Observability & Tracing
- **Purpose**: Traces every LLM call, agent decision, tool execution
- **Usage**: Debug why automation failed, see agent reasoning
- **In Autohire**: Full visibility into multi-agent workflow

### **PostgreSQL** - Persistent Database
- **Purpose**: Stores job listings, applications, LangGraph checkpoints
- **Usage**: Resume workflow from failure, track application history
- **In Autohire**: Save state, job history, application tracking

### **Redis** - Caching Layer
- **Purpose**: Fast in-memory caching for repeated queries
- **Usage**: Cache job search results, API responses
- **In Autohire**: Speed up repeated searches, rate limiting

---

## 📋 Prerequisites

### **Required**
- **Docker Desktop** - For containerized deployment
- **OpenAI API Key** - For GPT-4 agents ($0.02-0.05/session)

### **Optional but Recommended**
- **Anthropic API Key** - For Claude fallback
- **Langfuse Account** - For observability (FREE tier)

---

## 🚀 Quick Start (One Command)

```bash
# 1. Clone/navigate to project
cd "e:\Autohire 2"

# 2. Copy environment file
copy .env.example .env

# 3. Edit .env and add your OpenAI API key
notepad .env
# Set: OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE

# 4. Start EVERYTHING with one command
docker-compose -f docker-compose.full.yml up --build
```

**That's it!** All services will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Neo4j (ports 7474, 7687)
- ChromaDB (port 8000)
- Langfuse (port 3000)
- Autohire App (ports 6080, 5900)

---

## 🌐 Access Points

After starting, access these UIs:

| Service | URL | Purpose |
|---------|-----|---------|
| **VNC Desktop** | http://localhost:6080 | Watch automation live |
| **Neo4j Browser** | http://localhost:7474 | Query knowledge graph |
| **Langfuse UI** | http://localhost:3000 | View agent traces |
| **ChromaDB** | http://localhost:8000 | Vector store API |
| **PostgreSQL** | localhost:5432 | Database (use DBeaver/pgAdmin) |

**Default Credentials:**
- VNC Password: `autohire`
- Neo4j: `neo4j / autohire_neo4j_password`
- PostgreSQL: `autohire_user / autohire_password`
- Langfuse: Create account on first visit

---

## 📁 Project Structure

```
Autohire 2/
│
├── docker-compose.full.yml          # Full system orchestration
├── Dockerfile.full                  # App container with all frameworks
├── requirements_full.txt            # All Python dependencies
│
├── backend/
│   ├── multi_agent_job_hunter.py   # Main orchestrator
│   ├── claude_job_hunter.py        # Simple version (no APIs)
│   │
│   └── app/
│       ├── agents/
│       │   └── agent_config.py     # Agent configurations
│       ├── core/
│       │   ├── profile_data.py     # Your CV data
│       │   └── credential_manager.py
│       └── tools/
│           └── pywinauto_controller.py
│
├── docker/
│   └── supervisor/
│       └── autohire-full.conf      # Supervisor config
│
├── scripts/
│   └── init-db.sql                 # PostgreSQL initialization
│
├── data/                            # Persistent data
│   ├── chromadb/                   # Vector store
│   ├── results/                    # Job search results
│   ├── screenshots/                # Browser screenshots
│   └── cvs/                        # Generated CVs
│
└── logs/                            # Application logs
```

---

## ⚙️ Configuration

### **1. Environment Variables (.env)**

```bash
# === LLM API Keys (Required) ===
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE        # Optional fallback
GOOGLE_API_KEY=YOUR-GEMINI-KEY-HERE           # Optional free tier

# === Langfuse (Optional) ===
LANGFUSE_SECRET_KEY=sk-lf-YOUR-SECRET
LANGFUSE_PUBLIC_KEY=pk-lf-YOUR-PUBLIC

# === LangSmith (Optional) ===
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=YOUR-LANGSMITH-KEY
LANGCHAIN_PROJECT=autohire

# === Multi-Agent Config ===
PRIMARY_MODEL=gpt-4o                          # gpt-4o, claude-3-5-sonnet
FALLBACK_MODEL=claude-3-5-sonnet
AGENT_TEMPERATURE=0.7
MAX_ITERATIONS=10
ENABLE_REFLECTION=true
ENABLE_MULTI_AGENT=true

# === Memory & Knowledge ===
ENABLE_MEMORY=true
MEMORY_BACKEND=chromadb
ENABLE_KNOWLEDGE_GRAPH=true

# === Job Credentials ===
LINKEDIN_USERNAME=your-email@gmail.com
LINKEDIN_PASSWORD=your-password
SEEK_USERNAME=your-email@gmail.com
SEEK_PASSWORD=your-password
INDEED_USERNAME=your-email@gmail.com
INDEED_PASSWORD=your-password
```

---

## 🔧 Individual Service Setup

### **1. PostgreSQL Setup**

```bash
# Connect to database
docker exec -it autohire-postgres psql -U autohire_user -d autohire

# View tables
\dt

# Query jobs
SELECT * FROM job_listings ORDER BY found_date DESC LIMIT 10;

# View agent runs
SELECT * FROM agent_runs ORDER BY start_time DESC;
```

### **2. Neo4j Setup**

```bash
# Access Neo4j Browser
open http://localhost:7474

# Login with:
# Username: neo4j
# Password: autohire_neo4j_password

# Example Cypher queries:
# Create a job node
CREATE (j:Job {
  title: 'Social Researcher',
  company: 'Monash University',
  location: 'Melbourne',
  skills: ['Research', 'Data Analysis']
})

# Find jobs by skill
MATCH (j:Job)
WHERE 'Research' IN j.skills
RETURN j

# Create relationships
MATCH (j:Job {title: 'Social Researcher'})
CREATE (c:Company {name: 'Monash University'})
CREATE (j)-[:POSTED_BY]->(c)
```

### **3. ChromaDB Setup**

```python
# The app will automatically create collections
# You can query manually:

import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)

# List collections
collections = client.list_collections()

# Get autohire memory collection
collection = client.get_collection("autohire_memory")

# Query similar experiences
results = collection.query(
    query_texts=["how to login to LinkedIn"],
    n_results=3
)
```

### **4. Langfuse Setup**

```bash
# 1. Open Langfuse UI
open http://localhost:3000

# 2. Create account (first visit)
# 3. Create project: "Autohire"
# 4. Go to Settings → API Keys
# 5. Copy Secret Key and Public Key
# 6. Add to .env file:
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...

# 7. Restart containers
docker-compose -f docker-compose.full.yml restart autohire-full
```

---

## 🎮 Running the System

### **Option 1: Full System (Recommended)**

```bash
# Start all services
docker-compose -f docker-compose.full.yml up --build

# Wait for services to be healthy (30-60 seconds)
# Watch at: http://localhost:6080
```

### **Option 2: With Dashboard**

```bash
# Start with Streamlit dashboard
docker-compose -f docker-compose.full.yml --profile with-dashboard up --build

# Access dashboard at: http://localhost:8502
```

### **Option 3: Specific Services Only**

```bash
# Start just database + neo4j + chromadb
docker-compose -f docker-compose.full.yml up postgres neo4j chromadb
```

---

## 📊 Monitoring & Debugging

### **1. View Logs**

```bash
# All services
docker-compose -f docker-compose.full.yml logs -f

# Specific service
docker-compose -f docker-compose.full.yml logs -f autohire-full

# Agent logs only
docker-compose -f docker-compose.full.yml logs -f autohire-full | grep "Agent"
```

### **2. View Agent Traces (Langfuse)**

1. Open http://localhost:3000
2. Navigate to "Traces"
3. Click on a trace to see:
   - All agent messages
   - LLM calls and responses
   - Tool executions
   - Execution times
   - Token usage

### **3. Query Knowledge Graph (Neo4j)**

```cypher
# View all jobs
MATCH (j:Job) RETURN j LIMIT 25

# View job relationships
MATCH (j:Job)-[r]->(n)
RETURN j, r, n

# Find jobs by company
MATCH (j:Job)-[:POSTED_BY]->(c:Company {name: 'Monash University'})
RETURN j
```

### **4. Check Vector Store (ChromaDB)**

```bash
# Via API
curl http://localhost:8000/api/v1/collections

# Or use Python client
python
>>> import chromadb
>>> client = chromadb.HttpClient(host='localhost', port=8000)
>>> client.heartbeat()
```

---

## 🔄 Workflow Explanation

### **How All Frameworks Work Together**

```
1. USER REQUEST
   ↓
2. LANGCHAIN creates initial agent
   ↓
3. LANGGRAPH starts workflow state machine
   ↓
4. MEMORY AGENT queries LLAMAINDEX
   - Searches CHROMADB for similar past experiences
   - Queries NEO4J for job/company relationships
   ↓
5. PLANNER AGENT (AutoGen)
   - Uses RAG context to create plan
   - Logged in LANGFUSE
   ↓
6. CODER AGENT (AutoGen)
   - Writes automation code
   - Uses past successful patterns from ChromaDB
   ↓
7. EXECUTOR AGENT
   - Runs code with Playwright
   - Saves results to POSTGRESQL
   ↓
8. OBSERVER AGENT
   - Analyzes results
   - Decides: retry, continue, or complete
   ↓
9. LANGGRAPH decides next state
   - If retry → back to Planner
   - If continue → next task
   - If complete → save to POSTGRESQL
   ↓
10. KNOWLEDGE GRAPH UPDATED (Neo4j)
    - Job → Company relationships
    - Skills → Jobs relationships
    ↓
11. CHROMADB UPDATED
    - Successful patterns stored as embeddings
    ↓
12. LANGFUSE records full trace
    - Every agent message
    - Every LLM call
    - Every tool execution
```

---

## 💰 Cost Breakdown

### **With OpenAI API**
| Component | Cost per Run | Monthly (20 runs) |
|-----------|--------------|-------------------|
| GPT-4o API calls | $0.02-0.05 | $0.40-$1.00 |
| Langfuse | FREE | $0.00 |
| All other services | FREE (local) | $0.00 |
| **Total** | **~$0.03** | **~$0.60** |

### **Infrastructure Costs (Local Docker)**
- **RAM usage**: ~4GB
- **Disk usage**: ~5GB
- **CPU usage**: <15% average
- **Cost**: $0 (runs on your PC)

---

## 🆘 Troubleshooting

### **Services Won't Start**

```bash
# Check Docker
docker info

# Check logs
docker-compose -f docker-compose.full.yml logs

# Restart specific service
docker-compose -f docker-compose.full.yml restart postgres
```

### **Database Connection Error**

```bash
# Check PostgreSQL health
docker exec autohire-postgres pg_isready

# Recreate database
docker-compose -f docker-compose.full.yml down -v
docker-compose -f docker-compose.full.yml up --build
```

### **Neo4j Won't Connect**

```bash
# Check Neo4j logs
docker logs autohire-neo4j

# Wait for it to be ready (can take 30 seconds)
# Then access http://localhost:7474
```

### **ChromaDB Not Responding**

```bash
# Check if running
curl http://localhost:8000/api/v1/heartbeat

# Restart
docker-compose -f docker-compose.full.yml restart chromadb
```

---

## 🚀 Next Steps

### **After Setup**

1. ✅ Verify all services are running: `docker ps`
2. ✅ Access Langfuse UI and create account
3. ✅ Access Neo4j Browser and explore
4. ✅ Run first job search via VNC: http://localhost:6080
5. ✅ Check traces in Langfuse
6. ✅ Query results in PostgreSQL

### **Customization**

- Edit agent prompts in `backend/app/agents/agent_config.py`
- Modify workflow in `backend/multi_agent_job_hunter.py`
- Add new tools/capabilities
- Tune RAG retrieval parameters
- Customize knowledge graph schema

---

## 📚 Resources

- **LangChain Docs**: https://python.langchain.com/docs
- **LangGraph Tutorial**: https://langchain-ai.github.io/langgraph/
- **AutoGen Guide**: https://microsoft.github.io/autogen/
- **LlamaIndex Docs**: https://docs.llamaindex.ai/
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Neo4j Guide**: https://neo4j.com/docs/
- **Langfuse Docs**: https://langfuse.com/docs

---

## 🎯 Summary

**What You Get:**
- ✅ Multi-agent job search system
- ✅ Full observability with Langfuse
- ✅ Vector memory with ChromaDB
- ✅ Knowledge graph with Neo4j
- ✅ State persistence with PostgreSQL
- ✅ Fast caching with Redis
- ✅ Reflective workflow with LangGraph
- ✅ Agent collaboration with AutoGen
- ✅ Smart retrieval with LlamaIndex

**Total Setup Time:** ~10 minutes
**Total Cost:** ~$0.60/month

**Ready to run with just:**
```bash
docker-compose -f docker-compose.full.yml up --build
```

🚀 **Welcome to the future of automated job hunting!**
