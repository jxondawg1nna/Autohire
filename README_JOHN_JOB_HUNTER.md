# 🤖 AUTONOMOUS JOB HUNTER - COMPLETE SYSTEM

## Built for: **John Galgano** | Melbourne, VIC, Australia

---

## 🎯 WHAT THIS IS

A **fully autonomous job search and application system** that runs on your local Windows computer. You'll see everything happening in real-time as the system:

✅ **Generates professional CVs** using your profile data
✅ **Searches LinkedIn, Seek, and Indeed** for jobs in Melbourne
✅ **Finds roles matching your skills** (Social Researcher, Data Analyst, etc.)
✅ **Operates visibly** - watch the mouse move, browser navigate, text being typed
✅ **Tracks all jobs found** and saves results to JSON files

**Future Features (Partially Implemented):**
🔄 Automatically applies to matching jobs
🔄 Generates tailored cover letters for each application
🔄 Sends you daily email reports

---

## 📂 FILES CREATED

### Core System Files:
```
📁 E:\Autohire 2\
├── 🚀 RUN_JOB_HUNTER.bat              ← DOUBLE-CLICK THIS TO START!
├── 📋 QUICKSTART_GUIDE.md              ← Read this first
├── 📦 requirements_job_hunter.txt      ← Python dependencies
│
├── 📁 backend/
│   ├── autonomous_job_hunter.py        ← Main orchestrator
│   │
│   └── app/
│       ├── core/
│       │   ├── profile_data.py         ← Your CV data and job criteria
│       │   └── credential_manager.py   ← Secure login management
│       │
│       └── services/
│           ├── visible_automation_engine.py  ← Browser automation (visible!)
│           └── word_cv_generator.py          ← CV generation
│
├── 📁 generated_cvs/               ← Your generated CVs (DOCX files)
├── 📁 job_search_results/          ← Job listings found (JSON files)
├── 📁 logs/                        ← System logs
└── 📁 .browser_profile/            ← Saved login sessions
```

---

## ⚡ QUICK START

### 1️⃣ Install Dependencies (ONE TIME ONLY)

Open Command Prompt in `E:\Autohire 2\` and run:

```bash
pip install -r requirements_job_hunter.txt
playwright install chromium
```

### 2️⃣ Run the System

**Option A: Double-click the batch file** (EASIEST)
```
RUN_JOB_HUNTER.bat
```

**Option B: Run from command line**
```bash
python backend\autonomous_job_hunter.py
```

### 3️⃣ Watch It Work!

You'll see:
- ✅ Browser opening (visible Chrome window)
- ✅ Navigation to LinkedIn, Seek, Indeed
- ✅ Login process (first time only)
- ✅ Job search queries being typed
- ✅ Results being scraped
- ✅ Console showing progress

---

## 🧠 HOW IT WORKS

```
┌─────────────────────────────────────────────────────────────┐
│                 AUTONOMOUS JOB HUNTER WORKFLOW              │
└─────────────────────────────────────────────────────────────┘

Step 1: PROFILE SETUP
  ├─ Load John's CV data (profile_data.py)
  ├─ Load credentials (credential_manager.py)
  └─ Initialize automation engine

Step 2: CV GENERATION
  ├─ Generate professional DOCX CV
  ├─ Save to generated_cvs/
  └─ Ready for upload to job applications

Step 3: JOB SEARCH
  ├─ Open Chrome browser (VISIBLE!)
  │
  ├─ LinkedIn Search:
  │   ├─ Navigate to linkedin.com/jobs
  │   ├─ Login (first time only, session saved)
  │   ├─ Search: "Social Researcher Melbourne"
  │   ├─ Scrape job listings
  │   └─ Extract: title, company, location, URL
  │
  ├─ Seek Search:
  │   ├─ Navigate to seek.com.au
  │   ├─ Search: "Data Analyst Melbourne"
  │   ├─ Scrape results
  │   └─ Extract job details
  │
  └─ Indeed Search:
      ├─ Navigate to au.indeed.com
      ├─ Search: "Research Analyst Melbourne"
      ├─ Scrape results
      └─ Extract job details

Step 4: RESULTS PROCESSING
  ├─ Deduplicate jobs
  ├─ Calculate match scores
  ├─ Filter by location (Melbourne)
  ├─ Sort by relevance
  └─ Save to JSON file

Step 5: OUTPUT
  ├─ Console summary
  ├─ JSON results file
  └─ Log file with full details
```

---

## 📋 YOUR PROFILE DATA

The system knows about you:

### Personal Info:
- **Name:** John Galgano
- **Email:** johngalgano53@gmail.com
- **Phone:** 0422099192
- **Location:** Melbourne, VIC
- **LinkedIn:** linkedin.com/in/john-galgano-7181bb335

### Current Position:
- **Title:** Senior Researcher
- **Company:** Roy Morgan
- **Since:** January 2024
- **Experience:** 500+ surveys and interviews

### Education:
- **Degree:** Bachelor of Arts (Anthropology)
- **University:** Monash University

### Skills:
- Quantitative & qualitative research
- CATI interviewing & survey administration
- AI/Data tools (Claude Code, GPT, Python, etc.)
- Automation (Playwright, PyAutoGUI)

### Target Jobs:
```python
"Social Researcher"
"Market Researcher"
"Research Analyst"
"Data Analyst"
"Insights Analyst"
"Quantitative Researcher"
"Qualitative Researcher"
"Research Consultant"
"AI Research Specialist"
"Junior Data Scientist"
```

---

## 🔐 SECURITY

✅ **Credentials encrypted** using Fernet encryption
✅ **Browser sessions saved** - no need to login every time
✅ **Local storage only** - nothing sent to cloud
✅ **Visible automation** - you see everything happening

### Login Credentials:
Stored in: `E:\Autohire 2\logincredentials.txt`
```
username: johngalgano53@gmail.com
password: Oscarg2232
```

**Note:** Change the password in the file if you update it on job sites.

---

## 🎨 CUSTOMIZATION

### Change Job Search Criteria

Edit `backend\app\core\profile_data.py`:

```python
# Line ~130
JOB_SEARCH_CRITERIA = {
    "target_titles": [
        "Social Researcher",        # ← Add more titles here
        "YOUR NEW JOB TITLE",
    ],
    "locations": [
        "Melbourne",                # ← Change location
        "Remote",
    ],
    "keywords": [
        "research", "data",         # ← Add more keywords
    ]
}
```

### Change Application Settings

```python
# Line ~160
APPLICATION_SETTINGS = {
    "daily_application_limit": 20,           # Max 20 apps per day
    "applications_per_session": 5,           # 5 apps per run
    "min_delay_between_applications": 120,   # 2 min delay
    "auto_apply_threshold": 0.7,             # 70% match score needed
}
```

---

## 📊 OUTPUT FILES

### Generated CVs:
```
generated_cvs/
├── John_Galgano_CV_General_20250101_120000.docx
├── John_Galgano_CV_Social_Researcher_20250101_130000.docx
└── John_Galgano_CoverLetter_RoyMorgan.docx
```

### Job Search Results:
```json
{
  "title": "Senior Research Analyst",
  "company": "IPSOS",
  "location": "Melbourne VIC",
  "platform": "LinkedIn",
  "url": "https://linkedin.com/jobs/...",
  "found_at": "2025-01-01T12:00:00"
}
```

### Log Files:
```
logs/job_hunter.log

2025-01-01 12:00:00 - INFO - 🤖 AUTONOMOUS JOB HUNTER INITIALIZED FOR John Galgano
2025-01-01 12:00:05 - INFO - ✅ CV generated: John_Galgano_CV_General.docx
2025-01-01 12:00:10 - INFO - 🔍 Searching LinkedIn for: Social Researcher Melbourne
...
```

---

## 🛠️ TROUBLESHOOTING

### ❌ "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
pip install -r requirements_job_hunter.txt
playwright install chromium
```

### ❌ "Browser not opening"

**Solution:**
```bash
playwright install chromium --force
```

### ❌ "Login fails"

**Solution:**
1. Check credentials in `logincredentials.txt`
2. If 2FA is enabled, login manually first (browser will save session)
3. Delete `.browser_profile/` folder to reset sessions

### ❌ "No jobs found"

**Solution:**
1. Check internet connection
2. Job sites may have changed their HTML structure
3. Run in slower mode: Edit `autonomous_job_hunter.py` line 297:
   ```python
   automation = VisibleAutomationEngine(headless=False, slow_mo=2000)  # Slower
   ```

### ❌ "PyAutoGUI moves too fast"

**Solution:**
Edit `backend\app\services\visible_automation_engine.py` line 29:
```python
pyautogui.PAUSE = 1.0  # Increase from 0.5 to 1.0
```

---

## 🚀 ADVANCED FEATURES

### Run in Headless Mode (No Visible Browser)

Edit `autonomous_job_hunter.py` line 297:
```python
automation = VisibleAutomationEngine(headless=True, slow_mo=500)
```

### Schedule Automatic Runs

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start program `E:\Autohire 2\RUN_JOB_HUNTER.bat`

### Email Notifications (Future Feature)

Add to `.env` file:
```
SENDGRID_API_KEY=your_key_here
NOTIFICATION_EMAIL=johngalgano53@gmail.com
```

---

## 📈 SYSTEM ARCHITECTURE

```
┌──────────────────────────────────────────────────┐
│         AUTONOMOUS JOB HUNTER ARCHITECTURE       │
└──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  USER INTERFACE (You!)                                  │
│  ├─ Double-click RUN_JOB_HUNTER.bat                    │
│  ├─ Watch browser automation on screen                  │
│  └─ View results in JSON files                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (autonomous_job_hunter.py)                │
│  ├─ Coordinates all components                          │
│  ├─ Manages workflow steps                              │
│  └─ Handles errors and retries                          │
└─────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  CV GENERATOR  │ │   AUTOMATION   │ │  CREDENTIAL    │
│                │ │     ENGINE     │ │   MANAGER      │
│ • Word docs    │ │ • Playwright   │ │ • Encrypted    │
│ • PDF convert  │ │ • PyAutoGUI    │ │   storage      │
│ • Tailoring    │ │ • Visible mode │ │ • Auto-login   │
└────────────────┘ └────────────────┘ └────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   LINKEDIN     │ │     SEEK       │ │    INDEED      │
│   SCRAPER      │ │    SCRAPER     │ │   SCRAPER      │
└────────────────┘ └────────────────┘ └────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  DATA STORAGE                                           │
│  ├─ Job listings (JSON)                                 │
│  ├─ Generated CVs (DOCX/PDF)                            │
│  └─ Application logs                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 WHAT'S NEXT?

### Phase 1: ✅ COMPLETE
- ✅ CV generation from profile data
- ✅ Job search on LinkedIn, Seek, Indeed
- ✅ Visible browser automation
- ✅ Results tracking and logging

### Phase 2: 🔄 IN PROGRESS
- 🔄 Automatic job applications
- 🔄 Form filling with profile data
- 🔄 CV upload to applications
- 🔄 Cover letter generation per job

### Phase 3: 📋 PLANNED
- 📋 Email notifications for new jobs
- 📋 Application tracking dashboard (web UI)
- 📋 Success rate analytics
- 📋 Interview scheduling integration

---

## 💡 TIPS & TRICKS

### Get Better Results:
1. **Keep LinkedIn/Seek/Indeed profiles updated** - The system uses your login
2. **Run daily** - New jobs posted every day
3. **Check `match_score`** in results - Higher score = better fit
4. **Review logs** - `logs/job_hunter.log` has full details

### Avoid Getting Blocked:
1. **Don't run too frequently** - Max 2-3 times per day
2. **Human delays built-in** - Random pauses mimic human behavior
3. **Session persistence** - Saves logins, no repeated logins
4. **Visible mode** - Looks more human than headless

### Customize for Your Needs:
1. **Edit profile_data.py** - Update your skills, experience
2. **Adjust delays** - Make automation faster/slower
3. **Add more job sites** - Extend search to other platforms

---

## 📞 SUPPORT

### Check These First:
1. **QUICKSTART_GUIDE.md** - Detailed setup instructions
2. **logs/job_hunter.log** - Full system logs
3. **Console output** - Real-time status

### Common Issues:
- **Slow performance?** - Increase `slow_mo` parameter
- **Missing jobs?** - Job sites changed HTML, may need updates
- **Login fails?** - Check credentials, handle 2FA manually first

---

## 🏆 SUCCESS METRICS

The system will show you:

```
================================================================================
📊 SEARCH COMPLETE - FOUND 35 JOBS
================================================================================
  LinkedIn: 15 jobs
  Seek: 8 jobs
  Indeed: 12 jobs

🎯 TOP MATCHING JOBS:

1. Senior Research Analyst
   Company: IPSOS
   Location: Melbourne VIC
   Platform: LinkedIn
   Match Score: 92%

2. Social Research Consultant
   Company: Kantar
   Location: Melbourne VIC
   Platform: Seek
   Match Score: 88%

...
```

---

## 📄 LICENSE

This is a **personal tool built for John Galgano**. Use responsibly and in accordance with job site terms of service.

---

## 🙏 BUILT WITH

- **Python 3.9+** - Core language
- **Playwright** - Browser automation
- **PyAutoGUI** - Desktop automation
- **python-docx** - Word document generation
- **Win32** - Windows COM automation

---

**Ready to start your autonomous job hunt? Double-click `RUN_JOB_HUNTER.bat`!** 🚀

---

*Built with ❤️ by Claude Code for John Galgano's job search automation*
