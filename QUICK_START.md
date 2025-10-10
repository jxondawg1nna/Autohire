# 🚀 Quick Start - Claude-Powered Autohire

**Pure browser automation - NO API keys needed!**

---

## ⚡ ONE-COMMAND START

### **Option 1: Containerized (Recommended)**

```bash
# Just double-click:
RUN_CLAUDE.bat

# Then open: http://localhost:6080
```

**That's it!** No API keys, no configuration, no cost!

---

### **Option 2: Native (Direct on Your PC)**

```bash
# Install dependencies
pip install -r requirements_basic.txt

# Install browsers
playwright install chromium

# Run
python backend\claude_job_hunter.py
```

---

## 📋 What It Does

1. **Generates your CV** using python-docx (no Word needed)
2. **Searches LinkedIn** for jobs matching your profile
3. **Searches Seek** for jobs in Melbourne
4. **Searches Indeed** for relevant positions
5. **Saves all results** to `data/results/`

---

## 🎯 How It Works

### **No LLM API Calls!**
- Uses **Playwright** for browser automation
- Uses **python-docx** for CV generation
- Uses **direct selectors** to find job listings
- Everything runs locally in a container

### **Isolated Desktop**
- Runs in Docker container with virtual display
- Won't interfere with your actual screen
- Watch it work at http://localhost:6080

---

## 📁 Output Files

After running, you'll find:

```
data/
├── cvs/
│   └── CV_General_20250101_120000.docx
├── screenshots/
│   ├── linkedin_search_120001.png
│   ├── linkedin_results_120005.png
│   ├── seek_search_120010.png
│   └── seek_results_120015.png
└── results/
    └── job_search_20250101_120030.json
```

### **Results JSON Structure**
```json
{
  "timestamp": "2025-01-01T12:00:30",
  "jobs_found": 25,
  "jobs": [
    {
      "title": "Social Researcher",
      "company": "Example Corp",
      "location": "Melbourne VIC",
      "platform": "LinkedIn",
      "url": "https://...",
      "found_date": "2025-01-01T12:00:15"
    }
  ]
}
```

---

## 🔧 Customization

Edit `backend/app/core/profile_data.py` to change:

- **Job titles to search for**
- **Locations**
- **Keywords**
- **Your CV content**

Example:
```python
JOB_SEARCH_CRITERIA = {
    "target_titles": [
        "Data Analyst",      # Add your target roles
        "Research Analyst",
        "Business Analyst"
    ],
    "locations": [
        "Melbourne",         # Add your preferred locations
        "Sydney",
        "Remote"
    ]
}
```

---

## 🎮 Docker Commands

### **Start the system**
```bash
docker-compose -f docker-compose.claude.yml up --build
```

### **Stop the system**
```bash
docker-compose -f docker-compose.claude.yml down
```

### **View logs**
```bash
docker-compose -f docker-compose.claude.yml logs -f autohire-claude
```

### **Restart**
```bash
docker-compose -f docker-compose.claude.yml restart
```

---

## 🐛 Troubleshooting

### **"Docker not running"**
- Start Docker Desktop
- Check system tray for Docker icon

### **"Can't see virtual desktop"**
- Wait 10 seconds after starting
- Go to http://localhost:6080
- Password: `autohire`

### **"No jobs found"**
- Check screenshots in `data/screenshots/`
- LinkedIn/Seek may have changed their layout
- Check logs in `logs/` directory

### **"Container won't start"**
- Make sure ports 6080 and 5900 aren't in use
- Run: `docker-compose -f docker-compose.claude.yml down`
- Then try again

---

## 📊 What Gets Searched

By default, the system searches for:

- **Job Title**: "Social Researcher" (from your profile)
- **Location**: "Melbourne" (your location)
- **Platforms**: LinkedIn, Seek, Indeed

It will:
1. Navigate to each platform
2. Fill in search form
3. Extract first 10 job listings
4. Save titles, companies, locations, URLs
5. Take screenshots at each step

---

## 💡 Key Features

### ✅ **No API Costs**
- No OpenAI API
- No Anthropic API
- No Google API
- Completely FREE to run!

### ✅ **Isolated Execution**
- Runs in Docker container
- Virtual desktop (VNC)
- Won't interfere with your work

### ✅ **Full Automation**
- Generates CV automatically
- Searches all platforms
- Extracts job data
- Saves results

### ✅ **Observable**
- Screenshots at every step
- Detailed logs
- VNC to watch live

---

## 🎯 Next Steps

### **After First Run**
1. Check `data/results/` for job listings
2. Review `data/screenshots/` to see what happened
3. Check `data/cvs/` for your generated CV

### **Customize It**
1. Edit `profile_data.py` with your info
2. Change job search criteria
3. Modify CV template in `claude_job_hunter.py`

### **Automate It**
Set up a scheduled task to run daily:
```bash
# Windows Task Scheduler
schtasks /create /tn "Autohire Daily" /tr "C:\path\to\RUN_CLAUDE.bat" /sc daily /st 09:00
```

---

## 🔒 Privacy & Security

✅ **Your data stays local**
- No data sent to external APIs
- Everything runs in your container
- Results saved to your disk

✅ **Credentials are encrypted**
- Job platform credentials encrypted at rest
- Uses Fernet symmetric encryption

✅ **Safe to run**
- Read-only browsing (doesn't apply yet)
- Just extracts job data
- Doesn't modify anything online

---

## 📈 Comparison: Old vs New

### **Old Multi-Agent System**
- ❌ Requires OpenAI API key ($$$)
- ❌ Complex setup (Langfuse, ChromaDB, etc.)
- ❌ Many dependencies
- ✅ More "intelligent" (can adapt)

### **New Claude System** (This One)
- ✅ **NO API keys needed**
- ✅ **Simple setup** (just Docker)
- ✅ **Minimal dependencies**
- ✅ **FREE to run**
- ⚠️ Less adaptive (uses fixed selectors)

**Recommendation**: Start with this simple system!

---

## 🚀 Ready to Run?

```bash
# Just run this:
RUN_CLAUDE.bat

# Then watch at:
http://localhost:6080
```

**That's all you need!** 🎉

---

## 📞 Support

If something doesn't work:
1. Check `logs/` directory for error messages
2. Check `data/screenshots/` to see what happened
3. Review Docker logs: `docker-compose -f docker-compose.claude.yml logs`

Common issues:
- Port conflicts → Change ports in `docker-compose.claude.yml`
- Selector changes → Job sites updated their HTML
- Timeout errors → Increase wait times in code

---

**Enjoy your automated job search!** 🎯
