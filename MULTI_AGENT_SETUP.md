# 🤖 Multi-Agent Autohire Setup Guide

Complete setup instructions for the advanced multi-agent autonomous job application system.

---

## 🎯 **SYSTEM ARCHITECTURE**

This advanced system implements a **reflective, multi-agent architecture** that:

### **Agent Team**
1. **Planner Agent** - Breaks down job search into strategic tasks
2. **Coder Agent** - Writes automation code to execute tasks
3. **Executor Agent** - Runs code and monitors execution
4. **Memory Agent** - Retrieves relevant past experiences using RAG
5. **Observer Agent** - Reflects on results and decides next action

### **Workflow Loop**
```
Plan → Code → Execute → Observe → Reflect → Correct
                          ↑                      ↓
                          └──────────────────────┘
                         (Loop until success or max iterations)
```

### **Technologies**
- **LangGraph**: State machine for cyclic workflows
- **AutoGen**: Multi-agent collaboration framework
- **LlamaIndex**: RAG for knowledge retrieval
- **ChromaDB**: Vector store for memory
- **Langfuse**: Observability and tracing
- **Pywinauto**: Robust Windows desktop control
- **Playwright**: Browser automation
- **Docker**: Containerized isolation

---

## 📋 **PREREQUISITES**

### **Required**
- ✅ **OpenAI API Key** (for GPT-4 agents)
  - Get it at: https://platform.openai.com/api-keys
  - Cost: ~$0.02-0.05 per job search session

### **Optional (Recommended)**
- ⚙️ **Langfuse Account** (for tracing/debugging)
  - Get it at: https://cloud.langfuse.com/
  - Cost: FREE tier (50k events/month)

- 🔄 **Anthropic API Key** (fallback LLM)
  - Get it at: https://console.anthropic.com/
  - Cost: ~$0.015 per session

### **System Requirements**
- Windows 10/11 (for native mode)
- OR Docker Desktop (for containerized mode)
- 8GB+ RAM
- 10GB+ free disk space

---

## 🚀 **QUICK START (2 STEPS)**

### **Step 1: Configure Credentials**

```bash
# 1. Copy example file
copy .env.example .env

# 2. Edit .env and add your credentials:
#    - OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
#    - Job platform credentials (already configured)
```

### **Step 2: Run the System**

#### **Option A: Containerized (Recommended - No Desktop Interference)**
```bash
# Double-click this file:
RUN_MULTI_AGENT.bat

# Or run manually:
docker-compose -f docker-compose.multi-agent.yml up --build
```

Then open http://localhost:6080 to watch the agents work in an isolated desktop!

#### **Option B: Native (Runs Directly on Your Machine)**
```bash
# First, verify credentials
python backend\test_credentials.py

# Then run the multi-agent system
python backend\multi_agent_job_hunter.py
```

---

## 🔧 **DETAILED SETUP**

### **1. Install Dependencies**

#### **For Containerized Mode (Docker)**
```bash
# Install Docker Desktop from:
# https://www.docker.com/products/docker-desktop/

# Verify Docker is running
docker --version
```

#### **For Native Mode (Windows)**
```bash
# Install Python 3.11+
# Download from: https://www.python.org/downloads/

# Install dependencies
pip install -r requirements_complete.txt

# Install Playwright browsers
playwright install chromium firefox
```

---

### **2. Configure API Credentials**

#### **Required: OpenAI API Key**

1. Go to https://platform.openai.com/signup
2. Add payment method (required for API access)
3. Generate API key: https://platform.openai.com/api-keys
4. Copy key starting with `sk-proj-` or `sk-`
5. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
   ```

#### **Optional: Langfuse (Observability)**

1. Go to https://cloud.langfuse.com/ (free signup)
2. Create new project called "Autohire"
3. Go to Settings → API Keys
4. Copy Secret Key (sk-lf-...) and Public Key (pk-lf-...)
5. Add to `.env`:
   ```bash
   LANGFUSE_SECRET_KEY=sk-lf-YOUR-SECRET-KEY
   LANGFUSE_PUBLIC_KEY=pk-lf-YOUR-PUBLIC-KEY
   ```

#### **Optional: Anthropic Claude (Fallback)**

1. Go to https://console.anthropic.com/
2. Add payment method
3. Generate API key
4. Add to `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
   ```

---

### **3. Verify Setup**

Run the credential test script:

```bash
python backend\test_credentials.py
```

You should see:
```
✅ PASS - OpenAI API: Valid - Connection successful
✅ PASS - Job Platforms: All platforms configured
⚠️ SKIP - Anthropic Claude: Not configured (optional)
✅ PASS - Langfuse Observability: Valid - Connection successful
✅ PASS - ChromaDB Memory: Working - Collection: autohire_memory
```

---

## 🎮 **RUNNING THE SYSTEM**

### **Containerized Mode (Isolated Desktop)**

#### **Start the System**
```bash
# Option 1: Double-click the batch file
RUN_MULTI_AGENT.bat

# Option 2: Command line
docker-compose -f docker-compose.multi-agent.yml up --build
```

#### **Access Virtual Desktop**
- Open browser: http://localhost:6080
- Password: `autohire`
- Watch agents work in real-time without interfering with your screen!

#### **Stop the System**
```bash
docker-compose -f docker-compose.multi-agent.yml down
```

#### **View Logs**
```bash
docker-compose -f docker-compose.multi-agent.yml logs -f autohire-multi-agent
```

---

### **Native Mode (Direct Execution)**

```bash
# Verify credentials first
python backend\test_credentials.py

# Run the multi-agent system
python backend\multi_agent_job_hunter.py
```

**⚠️ Warning**: Native mode will control your actual mouse and keyboard!

---

## 📊 **UNDERSTANDING THE WORKFLOW**

### **What Happens When You Run It**

1. **Memory Agent** retrieves relevant past experiences from ChromaDB
2. **Planner Agent** creates a strategic plan:
   - Search LinkedIn for "Social Researcher Melbourne"
   - Filter jobs matching 70%+ profile
   - Apply to top 5 matches
   - Generate tailored CV for each

3. **Coder Agent** writes Python automation code:
   ```python
   # Navigate to LinkedIn
   # Log in with credentials
   # Search for jobs
   # Click on each job
   # Apply with tailored CV
   ```

4. **Executor Agent** runs the code:
   - Executes in isolated environment
   - Captures screenshots at each step
   - Logs all actions

5. **Observer Agent** analyzes results:
   - Success: Yes/No
   - Confidence: 85%
   - Observations: ["Login successful", "Found 12 jobs", "Applied to 5"]
   - Next Action: Continue / Retry / Complete / Abort

6. **Reflective Loop**:
   - If errors occurred → Loop back to Planner for retry
   - If successful → Complete
   - Max 10 iterations (configurable)

---

## 🔍 **OBSERVABILITY (Langfuse)**

If you configured Langfuse, you can see:

1. **Every agent message** in the conversation
2. **Every tool call** (Playwright actions, API calls)
3. **Execution times** for each step
4. **Token usage** and costs
5. **Error traces** with full context

Access at: https://cloud.langfuse.com/

---

## 📁 **OUTPUT FILES**

### **Results**
```
data/results/job_search_results_20250101_120000.json
```

Contains:
- Jobs found
- Applications submitted
- Errors encountered
- Execution time

### **Screenshots**
```
data/screenshots/linkedin_login_20250101_120001.png
data/screenshots/job_application_20250101_120030.png
```

Every automation step is captured for debugging.

### **Memory (ChromaDB)**
```
data/chromadb/
```

Vector embeddings of successful patterns for future retrieval.

### **Logs**
```
logs/autohire_20250101.log
```

Detailed execution logs.

---

## ⚙️ **CONFIGURATION OPTIONS**

Edit `.env` to customize:

### **Agent Configuration**
```bash
PRIMARY_MODEL=gpt-4o              # LLM for agents
FALLBACK_MODEL=claude-3-5-sonnet  # Fallback if primary fails
AGENT_TEMPERATURE=0.7             # Creativity (0-1)
MAX_ITERATIONS=10                 # Max retry loops
ENABLE_REFLECTION=true            # Enable self-correction
```

### **Memory Configuration**
```bash
ENABLE_MEMORY=true                # Use RAG memory
MEMORY_BACKEND=chromadb           # Vector store
RAG_TOP_K=3                       # Memories to retrieve
```

### **Desktop Control**
```bash
DESKTOP_CONTROL=pywinauto         # Robust element-based
# DESKTOP_CONTROL=pyautogui       # Fast but brittle
ENABLE_VISION_LLM=true            # Use GPT-4-Vision for screen analysis
```

### **Logging**
```bash
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
ENABLE_LANGFUSE=true              # Trace to Langfuse
SAVE_SCREENSHOTS=true             # Save every step
```

### **Job Search**
```bash
DAILY_APPLICATION_LIMIT=20        # Max applications per day
AUTO_APPLY_THRESHOLD=0.7          # Min match score (0-1)
REQUIRE_MANUAL_APPROVAL=false     # Auto-apply vs manual review
RETRY_FAILED_APPLICATIONS=true    # Retry failed applications
MAX_RETRIES=3                     # Max retry attempts
```

---

## 🆘 **TROUBLESHOOTING**

### **"No API key found"**
- Ensure `.env` file exists (copy from `.env.example`)
- Check `OPENAI_API_KEY=sk-...` is set correctly
- No spaces around `=`

### **"Invalid API key"**
- Verify key is correct (copy-paste from OpenAI dashboard)
- Ensure payment method added to OpenAI account
- Try generating a new key

### **"Docker not running"**
- Start Docker Desktop
- Check system tray for Docker icon
- Run `docker info` to verify

### **"Agent not making progress"**
- Check Langfuse traces to see where it's stuck
- Review screenshots in `data/screenshots/`
- Check `MAX_ITERATIONS` in `.env` (may need to increase)

### **"LinkedIn login failed"**
- Credentials may have changed
- LinkedIn may have CAPTCHA
- Try manual login first to verify credentials

---

## 💡 **BEST PRACTICES**

### **Start Small**
Test with one platform first:
```python
# In multi_agent_job_hunter.py, modify:
task = "Search LinkedIn only for 'Social Researcher Melbourne', find 3 jobs, don't apply yet"
```

### **Monitor First Run**
- Watch the virtual desktop (http://localhost:6080)
- Check Langfuse traces
- Review screenshots

### **Iterate and Improve**
- System learns from successful patterns (stored in ChromaDB)
- Failed attempts → Observer suggests improvements → Planner creates new plan
- After a few runs, success rate increases

### **Use Langfuse for Debugging**
- See exactly where errors occur
- Understand agent reasoning
- Optimize prompts if needed

---

## 📈 **SCALING UP**

### **Run with More Platforms**
```bash
# Default task searches all platforms:
task = "Search LinkedIn, Seek, and Indeed for jobs matching my profile. Apply to top 10 matches."
```

### **Add Neo4j Knowledge Graph (Optional)**
```bash
# Start with Neo4j enabled:
docker-compose -f docker-compose.multi-agent.yml --profile with-neo4j up
```

Enables:
- Structured knowledge storage
- Relationship tracking (Job → Company → Skills)
- Advanced querying

### **Add PostgreSQL Database (Optional)**
```bash
# Start with PostgreSQL enabled:
docker-compose -f docker-compose.multi-agent.yml --profile with-postgres up
```

Enables:
- Persistent application tracking
- Analytics and reporting
- Historical job search data

---

## 🔒 **SECURITY NOTES**

✅ **Safe Practices**:
- `.env` file is in `.gitignore` (never committed)
- Credentials encrypted at rest using Fernet
- Containerized mode isolates automation

⚠️ **Important**:
- Never commit `.env` to Git
- Rotate API keys if exposed
- Keep Docker images updated
- Review generated code before execution (in native mode)

---

## 💰 **COST BREAKDOWN**

### **Per Job Search Session (10 jobs)**
- OpenAI API (GPT-4o): ~$0.02-0.05
- Anthropic Claude (if used): ~$0.015-0.03
- Langfuse: $0 (free tier)
- Total: **~$0.02-0.08 per session**

### **Monthly (20 sessions)**
- ~$0.40-$1.60/month

**Much cheaper than job search subscription services!**

---

## 🎯 **NEXT STEPS**

1. ✅ **Verify credentials**: `python backend\test_credentials.py`
2. 🚀 **Run first session**: `RUN_MULTI_AGENT.bat`
3. 👁️ **Watch agents work**: http://localhost:6080
4. 📊 **Check results**: `data/results/`
5. 🔍 **Review traces**: https://cloud.langfuse.com/
6. 🎨 **Customize**: Edit `.env` for your preferences

---

## 📚 **ADDITIONAL RESOURCES**

- **OpenAI Platform**: https://platform.openai.com/
- **Langfuse Docs**: https://langfuse.com/docs
- **LangGraph Tutorial**: https://python.langchain.com/docs/langgraph
- **AutoGen Guide**: https://microsoft.github.io/autogen/
- **Pywinauto Docs**: https://pywinauto.readthedocs.io/

---

## 🤝 **SUPPORT**

- **Setup Issues**: See `CREDENTIALS_SETUP.md`
- **API Errors**: Check Langfuse traces
- **Docker Issues**: See `CONTAINERIZED_GUIDE.md`
- **General Questions**: Review logs in `logs/`

---

**Ready? Let's get started! 🚀**

```bash
python backend\test_credentials.py && RUN_MULTI_AGENT.bat
```

*The multi-agent system will autonomously search and apply for jobs matching your profile while you watch!*
