# 🚀 AI Vision Quick Start

## 5-Minute Setup

### Step 1: Get API Key (2 minutes)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Click "API Keys" → "Create Key"
4. Copy the key (starts with `sk-ant-api03-...`)

### Step 2: Configure (1 minute)

Edit `backend/.env`:

```bash
# Replace the placeholder
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE

# Enable AI
AI_VISION_ENABLED=true
AI_VISION_PROVIDER=claude
```

### Step 3: Test (2 minutes)

```bash
# Test AI connection
python test_ai_vision.py
```

You should see:
```
✅ API Connection                    PASS
✅ Complexity Analysis               PASS
✅ Screenshot Optimization           PASS
✅ Live AI Decision                  PASS (if you approve the live test)
✅ Hybrid Statistics                 PASS
```

---

## Usage Examples

### Basic: Job Search with AI

```python
from app.services.ai_decision_engine import create_conscious_operator_with_ai
from app.services.conscious_operator import Goal

# Create operator with AI enabled
operator = create_conscious_operator_with_ai(
    api_key="sk-ant-...",
    provider="claude"
)

# Start working
operator.start_session()
operator.page.goto("https://www.indeed.com")

# Define goal
goal = Goal(
    objective="Search for Python Developer jobs in Melbourne",
    success_criteria=["python", "developer", "melbourne", "results"]
)

# Let AI work towards goal
success = operator.work_towards_goal(goal)

# Check stats
if hasattr(operator.decision_engine, 'get_stats'):
    stats = operator.decision_engine.get_stats()
    print(f"AI usage: {stats['ai_percentage']:.1f}%")
    print(f"Tokens used: {stats['total_tokens']}")
```

### Advanced: Custom AI Scenario

```python
from app.services.ai_decision_engine import AIDecisionEngine, HybridDecisionEngine

# Create AI engine
ai_engine = AIDecisionEngine(provider="claude", api_key="sk-ant-...")

# Create hybrid engine (15% AI target)
hybrid = HybridDecisionEngine(ai_engine, ai_usage_target=0.15)

# Use in operator
operator.decision_engine = hybrid.decide

# Work on complex task
goal = Goal(
    objective="Complete job application form",
    success_criteria=["submitted", "confirmation"]
)

# AI will be used for complex decisions, rules for simple ones
operator.work_towards_goal(goal)

# Get detailed stats
stats = hybrid.get_stats()
print(f"""
Decision Breakdown:
  Total: {stats['total_decisions']}
  Rule-based: {stats['rule_based']} ({100 - stats['ai_percentage']:.1f}%)
  AI-powered: {stats['ai_powered']} ({stats['ai_percentage']:.1f}%)

Cost Efficiency:
  Target: {stats['target_percentage']:.0f}% AI
  Actual: {stats['ai_percentage']:.1f}% AI
  Within target: {'✅' if stats['within_target'] else '❌'}

API Usage:
  API calls: {stats['api_calls']}
  Total tokens: {stats['total_tokens']}
""")
```

---

## How It Works

### Hybrid Decision Flow

```
┌─────────────────┐
│  Page Loaded    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Capture Vision │  ← Screenshot + DOM
│  (SEE)          │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Analyze         │  ← Complexity scoring
│ Complexity      │     (0.0 = simple, 1.0 = complex)
└────────┬────────┘
         │
         v
    ┌────┴────┐
    │         │
    v         v
  Simple    Complex
  (<0.3)    (>0.6)
    │         │
    v         v
┌──────┐  ┌──────┐
│ Rules│  │  AI  │  ← Claude Vision
│ FREE │  │ $$   │
└──┬───┘  └──┬───┘
   │         │
   └────┬────┘
        │
        v
   ┌─────────┐
   │ Execute │
   │ Action  │
   └─────────┘
```

### Complexity Factors

The system analyzes:

1. **Element Count**: More elements = more complex
2. **Failed Attempts**: Repeated failures = complex
3. **Button Ambiguity**: Multiple similar buttons = complex
4. **Page Structure**: Unusual layouts = complex
5. **Text Volume**: Too little or too much = complex

### Cost Optimization

**Target: <15% AI usage**

Typical job application breakdown:
```
Action                    Decision Type    Cost
────────────────────────────────────────────────
Navigate to Indeed        Rule             $0.00
Fill search box          Rule             $0.00
Click Search             Rule             $0.00
Analyze job listing      AI               $0.02
Click Apply              Rule             $0.00
Fill name field          Rule             $0.00
Fill email field         Rule             $0.00
Choose resume file       AI               $0.02
Ambiguous question       AI               $0.02
Click Submit             Rule             $0.00
────────────────────────────────────────────────
TOTAL: 10 actions        3 AI / 7 rules   $0.06
                         30% AI usage
```

With optimization: **<15% AI = <$0.10 per application**

---

## Prompt Scenarios

The system automatically selects the right prompt template:

### 1. Job Search (`job_search`)

Used when: Searching, browsing job listings

Optimized for:
- Finding search boxes
- Identifying job postings
- Clicking through results

### 2. Application Form (`application_form`)

Used when: Filling application forms

Optimized for:
- Field identification
- Smart value matching
- Form progression

### 3. Ambiguous Page (`ambiguous_page`)

Used when: Unfamiliar page layout

Optimized for:
- Page type detection
- Next action recommendation
- Error recovery

---

## Configuration Options

All in `backend/.env`:

```bash
# Provider
AI_VISION_PROVIDER=claude          # or "openai"
AI_VISION_ENABLED=true              # Set false to disable AI

# Model Selection
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022   # Balanced (recommended)
# ANTHROPIC_MODEL=claude-3-opus-20240229     # Most capable, 3x cost
# ANTHROPIC_MODEL=claude-3-haiku-20240307    # Fastest, 1/10 cost

# Hybrid Settings (set in code)
ai_usage_target=0.15                # 15% AI usage target
max_retries=3                       # API retry attempts
```

---

## Monitoring & Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,  # Show all decisions
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Output:
```
2025-01-15 10:30:45 - ai_decision_engine - DEBUG - ✓ Rule-based decision (complexity: 0.20)
2025-01-15 10:30:47 - ai_decision_engine - DEBUG - 📐 Resized screenshot: 1024x768
2025-01-15 10:30:47 - ai_decision_engine - DEBUG - 💾 Screenshot: 450.2KB → 85.3KB (81% reduction)
2025-01-15 10:30:49 - ai_decision_engine - DEBUG - 🪙 Tokens: 1250 in + 85 out = 1335 total
2025-01-15 10:30:49 - ai_decision_engine - INFO - 🧠 Using AI (complexity: 0.75) | Stats: 12.5% AI usage (2/16)
```

### Track Costs

```python
# Get stats
stats = hybrid_engine.get_stats()

# Calculate cost (approximate)
# Claude Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
input_tokens = stats['total_tokens'] * 0.85  # ~85% input
output_tokens = stats['total_tokens'] * 0.15  # ~15% output

cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)
print(f"Estimated cost: ${cost:.4f}")
```

---

## Troubleshooting

### ❌ "API key not found"

Check `backend/.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...  # Must start with sk-ant-
```

### ❌ "Rate limit exceeded"

Wait 60 seconds, or:
```python
hybrid = HybridDecisionEngine(ai_engine, ai_usage_target=0.05)  # Reduce to 5%
```

### ❌ "Screenshot optimization failed"

Install Pillow:
```bash
pip install Pillow
```

### ⚠️ AI usage too high (>20%)

Check complexity thresholds in `HybridDecisionEngine`:
```python
# Lower thresholds = more rule-based decisions
if complexity_score < 0.4:  # Was 0.3
    action = self._rule_based_decision(...)
```

---

## Next Steps

1. ✅ **Tested?** Run `python test_ai_vision.py`
2. ✅ **Working?** Try `python FINAL_DEMONSTRATION.py`
3. ✅ **Ready?** Start applying to jobs!

### Full Application Workflow (Coming Next)

```python
# End-to-end job application
from app.services.job_application_workflow import JobApplicationWorkflow

workflow = JobApplicationWorkflow(
    api_key="sk-ant-...",
    use_ai=True,
    ai_usage_target=0.15
)

# Apply to 10 jobs
results = workflow.apply_to_jobs(
    search_terms="Python Developer",
    location="Melbourne",
    max_applications=10
)

print(f"Applied to {results['successful']} jobs")
print(f"AI usage: {results['ai_percentage']:.1f}%")
print(f"Total cost: ${results['estimated_cost']:.2f}")
```

---

## Support

- **Documentation**: See `AI_VISION_INTEGRATION_PLAN.md` for full technical details
- **Setup Help**: See `SETUP_AI_VISION.md` for step-by-step instructions
- **Prompts**: See `backend/app/services/vision_prompts.py` for all prompt templates
- **Tests**: Run `python test_ai_vision.py` to validate your setup

**You're now ready to let AI guide your job search! 🎉**
