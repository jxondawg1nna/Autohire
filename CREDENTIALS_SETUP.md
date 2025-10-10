# 🔐 CREDENTIALS SETUP GUIDE

This guide will help you set up all the necessary credentials for the advanced multi-agent Autohire system.

---

## 📋 **REQUIRED CREDENTIALS:**

### 1. **OpenAI API Key** (Required)
- **Where:** https://platform.openai.com/api-keys
- **Why:** Powers GPT-4 agents for planning, coding, and decision-making
- **Cost:** Pay-as-you-go (~$0.01-0.03 per job search session)
- **Setup:**
  1. Create OpenAI account
  2. Add payment method
  3. Generate API key
  4. Copy key starting with `sk-`

### 2. **Anthropic API Key** (Optional)
- **Where:** https://console.anthropic.com/
- **Why:** Alternative LLM (Claude 3.5 Sonnet) for agents
- **Cost:** Pay-as-you-go (~$0.015 per job search session)
- **Setup:**
  1. Create Anthropic account
  2. Add payment method
  3. Generate API key
  4. Copy key starting with `sk-ant-`

### 3. **Google Gemini API Key** (Optional)
- **Where:** https://makersuite.google.com/app/apikey
- **Why:** Free tier alternative for basic automation
- **Cost:** **FREE** (with generous limits)
- **Setup:**
  1. Sign in with Google account
  2. Create API key
  3. Copy the key

### 4. **Langfuse Keys** (For Observability - Optional but Recommended)
- **Where:** https://cloud.langfuse.com/
- **Why:** Trace and debug every agent decision, tool call, and error
- **Cost:** **FREE** tier available (up to 50k events/month)
- **Setup:**
  1. Create Langfuse account (free)
  2. Create new project
  3. Copy **Secret Key** (sk-lf-...)
  4. Copy **Public Key** (pk-lf-...)

---

## 🔧 **SETUP INSTRUCTIONS:**

### Step 1: Copy the Example File
```bash
cd "E:\Autohire 2"
copy .env.example .env
```

### Step 2: Edit `.env` File

Open `E:\Autohire 2\.env` and fill in your credentials:

```bash
# === LLM API Keys ===
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE  # ← Paste your OpenAI key
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE        # ← Optional: Paste Claude key
GOOGLE_API_KEY=YOUR-GEMINI-KEY-HERE           # ← Optional: Paste Gemini key

# === Langfuse Observability (Optional) ===
LANGFUSE_SECRET_KEY=sk-lf-YOUR-SECRET-KEY     # ← Paste Langfuse secret
LANGFUSE_PUBLIC_KEY=pk-lf-YOUR-PUBLIC-KEY     # ← Paste Langfuse public
LANGFUSE_HOST=https://cloud.langfuse.com      # ← Keep as-is

# === Job Search Credentials (Already Set) ===
LINKEDIN_USERNAME=johngalgano53@gmail.com     # ← Already correct
LINKEDIN_PASSWORD=Oscarg2232                  # ← Already correct
SEEK_USERNAME=johngalgano53@gmail.com         # ← Already correct
SEEK_PASSWORD=Oscarg2232                      # ← Already correct
INDEED_USERNAME=johngalgano53@gmail.com       # ← Already correct
INDEED_PASSWORD=Oscarg2232                    # ← Already correct
```

### Step 3: Verify Setup

Run this test script:
```bash
python backend\test_credentials.py
```

It will check:
- ✅ OpenAI API key is valid
- ✅ Anthropic API key works (if provided)
- ✅ Langfuse connection successful
- ✅ Job platform credentials loaded

---

## 💰 **COST BREAKDOWN:**

### Option 1: OpenAI Only (Recommended)
- **Model:** GPT-4o
- **Cost per session:** ~$0.02-0.05
- **Monthly (10 sessions):** ~$0.50
- **Features:** Best reasoning, reliable automation

### Option 2: Anthropic Claude
- **Model:** Claude 3.5 Sonnet
- **Cost per session:** ~$0.015-0.03
- **Monthly (10 sessions):** ~$0.30
- **Features:** Great reasoning, very safe

### Option 3: Google Gemini (FREE!)
- **Model:** Gemini Pro
- **Cost:** **$0** (free tier: 60 requests/min)
- **Monthly:** **FREE**
- **Features:** Good for basic automation, may be less reliable

### Langfuse (Observability)
- **FREE tier:** 50,000 events/month
- **Cost:** $0 for personal use
- **Features:** Full tracing, debugging, analytics

---

## 🎯 **RECOMMENDED SETUP (Best Value):**

**For Testing:**
```
OPENAI_API_KEY=sk-...           (use this)
LANGFUSE_SECRET_KEY=sk-lf-...   (optional but helpful)
```

**For Production:**
```
OPENAI_API_KEY=sk-...           (primary)
ANTHROPIC_API_KEY=sk-ant-...    (fallback)
LANGFUSE_SECRET_KEY=sk-lf-...   (debugging)
```

---

## 🔐 **SECURITY CHECKLIST:**

✅ **NEVER commit `.env` to Git** (already in `.gitignore`)
✅ **Keep API keys secret** - don't share them
✅ **Use `.env.example` for templates** - safe to commit
✅ **Rotate keys if exposed** - regenerate immediately
✅ **Set up billing alerts** - prevent unexpected charges

---

## 🚀 **QUICK START (Minimum Required):**

**Only 2 credentials needed to start:**

1. **OpenAI API Key**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Paste into `.env` file

2. **Job Credentials** (Already Done!)
   - Already in `logincredentials.txt`
   - System will use automatically

**That's it!** You can run the system with just these two items.

---

## 🆘 **TROUBLESHOOTING:**

### "Invalid API key"
- Check key is correct (no extra spaces)
- Ensure you've added payment method to OpenAI account
- Try generating a new key

### "Rate limit exceeded"
- Wait a few minutes
- Check OpenAI dashboard for usage
- Consider upgrading to paid tier

### "Langfuse connection failed"
- Check secret and public keys are correct
- Ensure you created a project in Langfuse
- Try refreshing keys in Langfuse dashboard

---

## 📊 **HOW TO GET YOUR CREDENTIALS:**

### OpenAI (Primary LLM)
1. Visit: https://platform.openai.com/signup
2. Sign up with email
3. Add payment method (required for API access)
4. Go to: https://platform.openai.com/api-keys
5. Click "Create new secret key"
6. Name it "Autohire"
7. Copy the key (starts with `sk-`)
8. Paste into `.env` as `OPENAI_API_KEY=sk-...`

### Langfuse (Debugging - Optional)
1. Visit: https://cloud.langfuse.com/
2. Sign up (free)
3. Create new project called "Autohire"
4. Go to Settings → API Keys
5. Copy **Secret Key** (sk-lf-...)
6. Copy **Public Key** (pk-lf-...)
7. Paste both into `.env`

---

## ✅ **VERIFICATION:**

After setting up, your `.env` should look like:

```bash
OPENAI_API_KEY=sk-proj-abc123xyz...  ✅ Your actual key
LANGFUSE_SECRET_KEY=sk-lf-def456...  ✅ Your Langfuse secret
LANGFUSE_PUBLIC_KEY=pk-lf-ghi789...  ✅ Your Langfuse public
LINKEDIN_USERNAME=johngalgano53@gmail.com  ✅ Already set
LINKEDIN_PASSWORD=Oscarg2232               ✅ Already set
```

---

**Ready? Once credentials are set, run:**
```bash
python backend\multi_agent_job_hunter.py
```

🚀 **The multi-agent system will start!**

---

*Need help? Check the test script or contact support.*
