# 🚀 AUTONOMOUS JOB HUNTER - QUICK START GUIDE

## For: John Galgano
## Purpose: Automatically search and apply to jobs in Melbourne, Australia

---

## ✅ WHAT THIS SYSTEM DOES:

1. **Generates Professional CVs** - Creates Word documents from your CV data
2. **Searches Job Sites** - Finds jobs on LinkedIn, Seek, and Indeed
3. **Matches Your Profile** - Filters jobs based on your skills and location
4. **Visible Automation** - You see everything happening on your screen
5. **Tracks Applications** - Saves all job listings found

---

## 📋 SETUP (ONE-TIME)

### Step 1: Install Python Dependencies

Open Command Prompt in this folder and run:

```bash
pip install -r requirements_job_hunter.txt
```

### Step 2: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 3: Verify Your Credentials

Make sure `logincredentials.txt` has your correct login info:
```
username: johngalgano53@gmail.com
password: Oscarg2232
```

**✅ Setup Complete!**

---

## 🎯 HOW TO RUN

### Option 1: Double-Click the Batch File (EASIEST)

Just double-click: **`RUN_JOB_HUNTER.bat`**

### Option 2: Run from Command Prompt

```bash
cd "E:\Autohire 2"
python backend\autonomous_job_hunter.py
```

---

## 👀 WHAT YOU'LL SEE:

1. **Console logs** showing progress
2. **Chrome browser opening** (visible, not hidden!)
3. **Mouse moving and clicking** on the screen
4. **Text being typed** into search boxes
5. **Job listings being scraped** from LinkedIn, Seek, and Indeed
6. **Results saved** to JSON file

---

## 📁 WHERE FILES ARE SAVED:

### Generated CVs:
```
E:\Autohire 2\generated_cvs\
  ├── John_Galgano_CV_General_20250101_120000.docx
  ├── John_Galgano_CoverLetter_Research_Analyst.docx
  └── ...
```

### Job Search Results:
```
E:\Autohire 2\job_search_results\
  └── results_20250101_120000.json
```

### Logs:
```
E:\Autohire 2\logs\
  └── job_hunter.log
```

---

## 🎛️ CUSTOMIZATION

### Change Search Criteria

Edit `backend\app\core\profile_data.py`:

```python
JOB_SEARCH_CRITERIA = {
    "target_titles": [
        "Social Researcher",    # ← Add/remove job titles here
        "Data Analyst",
        ...
    ],
    "locations": [
        "Melbourne",            # ← Change locations here
        "Remote",
    ],
    ...
}
```

### Change Application Limits

Edit `APPLICATION_SETTINGS` in the same file:

```python
APPLICATION_SETTINGS = {
    "daily_application_limit": 20,     # ← Change this
    "applications_per_session": 5,
    ...
}
```

---

## 🔧 TROUBLESHOOTING

### Problem: "Module not found"
**Solution:** Run `pip install -r requirements_job_hunter.txt`

### Problem: "Playwright not installed"
**Solution:** Run `playwright install chromium`

### Problem: Browser doesn't open
**Solution:**
1. Check if Chrome is installed
2. Run: `playwright install chromium --force`

### Problem: Login fails
**Solution:**
1. Check credentials in `logincredentials.txt`
2. Make sure 2FA is disabled or handle it manually first
3. Browser profile will save session after first manual login

### Problem: Can't find Word
**Solution:**
- The system generates DOCX files programmatically
- You don't need Word installed
- If you want to convert to PDF, ensure Word is installed

---

## 🛡️ SAFETY FEATURES

✅ **Human-like behavior** - Random delays, natural mouse movements
✅ **Rate limiting** - Waits between searches to avoid bans
✅ **Session persistence** - Saves login sessions
✅ **Failsafe** - Move mouse to top-left corner to stop automation
✅ **Visible mode** - You see everything happening

---

## 📊 SAMPLE OUTPUT

```
================================================================================
🤖 AUTONOMOUS JOB HUNTER INITIALIZED FOR John Galgano
📍 Location: Melbourne, VIC, Australia
🎯 Target Roles: Social Researcher, Market Researcher, Data Analyst...
================================================================================

STEP 1: Generating CV...
✅ CV generated: e:/Autohire 2/generated_cvs/John_Galgano_CV_General_20250101.docx

STEP 2: Starting visible browser automation...
✅ Browser started (visible mode)

STEP 3: Searching for 'Social Researcher' jobs...
🔍 Searching LinkedIn for: Social Researcher Melbourne
  ✓ Found: Senior Social Researcher at Roy Morgan
  ✓ Found: Research Analyst at IPSOS
  ...
✅ Found 15 jobs on LinkedIn

🔍 Searching Seek for: Social Researcher
  ✓ Found: Market Researcher at Nielsen
  ...
✅ Found 8 jobs on Seek

🔍 Searching Indeed for: Social Researcher
  ✓ Found: Qualitative Researcher at Kantar
  ...
✅ Found 12 jobs on Indeed

================================================================================
📊 SEARCH COMPLETE - FOUND 35 JOBS
================================================================================
  LinkedIn: 15 jobs
  Seek: 8 jobs
  Indeed: 12 jobs

💾 Results saved to: e:/Autohire 2/job_search_results/results_20250101_120000.json

✅ JOB SEARCH SESSION COMPLETED
```

---

## 🎯 NEXT STEPS (FUTURE FEATURES)

The following features are in development:

- ✅ **Job Search** (DONE)
- ✅ **CV Generation** (DONE)
- 🔄 **Automatic Applications** (In Progress)
- 🔄 **Cover Letter Customization** (In Progress)
- 🔄 **Application Tracking Dashboard** (Planned)
- 🔄 **Email Notifications** (Planned)

---

## 📞 NEED HELP?

Check the log files:
- `logs/job_hunter.log` - Main system log
- Console output - Real-time status

---

## ⚡ QUICK REFERENCE

| Action | Command |
|--------|---------|
| Run job hunter | `RUN_JOB_HUNTER.bat` |
| Install deps | `pip install -r requirements_job_hunter.txt` |
| Install browsers | `playwright install chromium` |
| View results | `job_search_results/results_*.json` |
| View logs | `logs/job_hunter.log` |

---

**Built with ❤️ for John Galgano's job search automation**

*Let the robots do the tedious work while you focus on preparing for interviews!* 🚀
