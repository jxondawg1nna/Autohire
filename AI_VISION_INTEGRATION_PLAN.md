# 🤖 AI Vision Integration - Complete Build Plan

## 🎯 Objective

Transform the operator from rule-based to AI-powered vision intelligence, enabling it to:
- Analyze screenshots like a human
- Make intelligent decisions in complex scenarios
- Understand visual context and layout
- Handle ambiguous situations
- Learn optimal strategies

---

## 📋 Architecture Overview

```
Current State (Rule-Based):
┌─────────────┐
│   Vision    │ → Screenshot + DOM
└─────────────┘
       ↓
┌─────────────┐
│ Simple Rules│ → if "Apply" in buttons → click
└─────────────┘
       ↓
┌─────────────┐
│   Action    │
└─────────────┘

Target State (AI-Powered):
┌─────────────┐
│   Vision    │ → Screenshot + DOM + Context
└─────────────┘
       ↓
┌─────────────────────────────────┐
│  Claude Vision API              │
│  - Analyzes screenshot          │
│  - Understands page layout      │
│  - Reads visible text           │
│  - Identifies next best action  │
└─────────────────────────────────┘
       ↓
┌─────────────┐
│ Smart Action│ → Context-aware decision
└─────────────┘

Hybrid Mode (Optimal):
┌─────────────┐
│   Vision    │
└─────────────┘
       ↓
┌─────────────────────────────────┐
│  Decision Router                │
│  Simple case? → Rules (95%)     │
│  Complex case? → AI (5%)        │
└─────────────────────────────────┘
       ↓
┌─────────────┐
│   Action    │
└─────────────┘
```

---

## 🔧 Implementation Phases

### Phase 1: Configuration & Setup (30 min)

**Files to create/modify:**
- `backend/.env` - Add API keys
- `backend/app/core/config.py` - Load AI settings
- `test_ai_config.py` - Verify setup

**Tasks:**
1. ✅ Add Anthropic API key to environment
2. ✅ Add OpenAI API key (optional fallback)
3. ✅ Create configuration loader
4. ✅ Test API connectivity

**Code:**
```python
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...  # Optional

# config.py
ANTHROPIC_API_KEY: Optional[str] = None
ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
OPENAI_API_KEY: Optional[str] = None
AI_VISION_ENABLED: bool = True
AI_VISION_PROVIDER: str = "claude"  # or "openai"
```

**Deliverable:** Configuration system working

---

### Phase 2: Vision Prompt Engineering (45 min)

**Files to create:**
- `backend/app/services/vision_prompts.py` - Prompt templates
- `backend/app/services/vision_context.py` - Context builder

**Tasks:**
1. ✅ Create prompt templates for different scenarios
2. ✅ Build context aggregation system
3. ✅ Add screenshot optimization
4. ✅ Create decision parsing system

**Prompt Templates:**

```python
# Job search scenario
SEARCH_PROMPT = """
You are an autonomous browser operator searching for jobs.

CURRENT GOAL: {goal.objective}

SCREENSHOT: [Attached]

PAGE STATE:
- URL: {vision.current_url}
- Title: {vision.page_title}
- Visible inputs: {len(inputs)}
- Visible buttons: {len(buttons)}

QUESTION: What action should I take to progress toward the goal?

Respond with JSON:
{
  "action_type": "click|fill_field|scroll|wait|navigate",
  "target": "CSS selector",
  "value": "value if filling field",
  "reasoning": "why this helps achieve the goal",
  "confidence": 0.0-1.0
}
"""

# Application form scenario
APPLICATION_PROMPT = """
You are filling out a job application form.

SCREENSHOT: [Attached]

VISIBLE FIELDS:
{field_list}

USER PROFILE:
- Name: John Galgano
- Email: john@example.com
- Phone: +61412345678
- Skills: Python, FastAPI, React, PostgreSQL

QUESTION: Which field should I fill next and with what value?

Respond with JSON:
{
  "action_type": "fill_field",
  "target": "selector",
  "value": "appropriate value",
  "reasoning": "why this field next"
}
"""

# Ambiguous page scenario
ANALYSIS_PROMPT = """
You are trying to understand an ambiguous page.

SCREENSHOT: [Attached]
GOAL: {goal}

This page is unclear. Please:
1. Identify the page type (login, form, results, error, etc)
2. List all interactive elements
3. Recommend best next action

Respond with detailed JSON analysis.
"""
```

**Deliverable:** Prompt system with 5+ templates

---

### Phase 3: Claude Vision Integration (60 min)

**Files to modify:**
- `backend/app/services/ai_decision_engine.py` - Update implementation
- `backend/app/services/vision_optimizer.py` - NEW: Image optimization

**Tasks:**
1. ✅ Implement Claude Vision API calls
2. ✅ Add screenshot compression (reduce costs)
3. ✅ Create response parser
4. ✅ Add error handling & retries
5. ✅ Implement fallback strategies

**Code Structure:**

```python
class ClaudeVisionEngine:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1024

    def decide_action(self, vision: Vision, goal: Goal, memory: Memory) -> Action:
        # 1. Optimize screenshot (compress, resize)
        optimized_screenshot = self._optimize_screenshot(vision.screenshot)

        # 2. Build context-aware prompt
        prompt = self._build_prompt(vision, goal, memory)

        # 3. Call Claude Vision API
        response = self._call_api(optimized_screenshot, prompt)

        # 4. Parse response to Action
        action = self._parse_response(response)

        # 5. Validate action is safe
        if self._is_safe_action(action):
            return action
        else:
            return self._safe_fallback_action()

    def _optimize_screenshot(self, screenshot_bytes: bytes) -> str:
        """
        Optimize screenshot to reduce API costs
        - Resize to max 1024x768
        - Compress to JPEG 80% quality
        - Convert to base64
        """
        from PIL import Image
        import io
        import base64

        img = Image.open(io.BytesIO(screenshot_bytes))

        # Resize if too large
        if img.width > 1024 or img.height > 768:
            img.thumbnail((1024, 768), Image.Resampling.LANCZOS)

        # Compress
        buffer = io.BytesIO()
        img.convert('RGB').save(buffer, format='JPEG', quality=80, optimize=True)

        # Base64 encode
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _call_api(self, screenshot_b64: str, prompt: str) -> str:
        """Call Claude Vision API with retries"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": screenshot_b64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }]
                )

                return response.content[0].text

            except anthropic.RateLimitError:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise

            except Exception as e:
                logger.error(f"Claude API error: {e}")
                if attempt < max_retries - 1:
                    continue
                raise
```

**Deliverable:** Working Claude Vision integration

---

### Phase 4: Hybrid Decision Engine (45 min)

**Files to create:**
- `backend/app/services/hybrid_decision_engine.py` - Smart router

**Tasks:**
1. ✅ Create decision complexity analyzer
2. ✅ Route simple cases to rules
3. ✅ Route complex cases to AI
4. ✅ Track AI usage statistics
5. ✅ Optimize cost/performance ratio

**Logic:**

```python
class HybridDecisionEngine:
    """
    Smart router: Uses rules for 95% of cases, AI for 5%
    Saves costs while maintaining intelligence
    """

    def __init__(self, ai_engine: ClaudeVisionEngine):
        self.ai_engine = ai_engine
        self.rules_used = 0
        self.ai_used = 0

    def decide(self, vision: Vision, goal: Goal, memory: Memory) -> Action:
        # Analyze complexity
        complexity = self._analyze_complexity(vision, goal)

        if complexity == "simple":
            # Use rules (fast, free)
            self.rules_used += 1
            return self._rule_based_decision(vision, goal)
        else:
            # Use AI (smart, costs money)
            self.ai_used += 1
            return self.ai_engine.decide_action(vision, goal, memory)

    def _analyze_complexity(self, vision: Vision, goal: Goal) -> str:
        """
        Determine if situation is simple or complex

        Simple cases (use rules):
        - Obvious "Apply" or "Submit" button visible
        - Clear form with empty fields
        - Standard search box
        - Common patterns (login, search, etc)

        Complex cases (use AI):
        - Ambiguous page layout
        - Multiple similar buttons
        - Unexpected page state
        - Error or block detected
        - No obvious next action
        """

        # Rule 1: Obvious action button
        for btn in vision.visible_buttons:
            if any(word in btn['text'].lower() for word in
                   ['apply now', 'submit application', 'easy apply']):
                return "simple"

        # Rule 2: Standard search scenario
        if 'search' in goal.objective.lower():
            search_inputs = [i for i in vision.visible_inputs
                           if 'search' in i['placeholder'].lower()]
            if search_inputs:
                return "simple"

        # Rule 3: Clear form with obvious fields
        if len(vision.visible_inputs) > 0:
            empty_fields = [i for i in vision.visible_inputs if not i['value']]
            if len(empty_fields) == 1:  # Only one empty field
                return "simple"

        # Default: Use AI for complex situations
        return "complex"

    def _rule_based_decision(self, vision: Vision, goal: Goal) -> Action:
        """Fast rule-based decisions for common cases"""

        # Check for obvious buttons
        for btn in vision.visible_buttons:
            text = btn['text'].lower()

            if 'apply' in text and 'apply' in goal.objective.lower():
                return Action(
                    type="click",
                    target=btn['selector'],
                    reasoning=f"Rule: Found '{btn['text']}' button matching goal"
                )

            if any(word in text for word in ['submit', 'continue', 'next']):
                if vision.visible_inputs:
                    # Only submit if fields are filled
                    filled = [i for i in vision.visible_inputs if i['value']]
                    if len(filled) > 0:
                        return Action(
                            type="click",
                            target=btn['selector'],
                            reasoning="Rule: Submitting filled form"
                        )

        # Fill empty fields
        for inp in vision.visible_inputs:
            if not inp['value']:
                value = self._get_field_value(inp)
                if value:
                    return Action(
                        type="fill_field",
                        target=inp['selector'],
                        value=value,
                        reasoning=f"Rule: Filling {inp['placeholder'] or inp['name']}"
                    )

        # Default: Scroll to explore
        return Action(
            type="scroll",
            value="down",
            reasoning="Rule: Exploring page"
        )

    def get_stats(self) -> Dict:
        """Return usage statistics"""
        total = self.rules_used + self.ai_used
        return {
            'rules_used': self.rules_used,
            'ai_used': self.ai_used,
            'total_decisions': total,
            'ai_percentage': (self.ai_used / total * 100) if total > 0 else 0,
            'cost_efficiency': f"{self.rules_used}/{total} free decisions"
        }
```

**Deliverable:** Hybrid system using AI only when needed

---

### Phase 5: Testing & Validation (60 min)

**Files to create:**
- `test_ai_vision_simple.py` - Test AI on single page
- `test_ai_vision_indeed.py` - Test on Indeed
- `test_hybrid_efficiency.py` - Verify cost optimization

**Test Scenarios:**

```python
# Test 1: Simple page (should use rules)
def test_simple_page():
    operator = create_ai_operator()
    operator.page.goto("https://example.com")

    # Should make decision using rules (free)
    action = operator.decide_next_action()

    assert operator.stats['ai_used'] == 0  # No AI needed

# Test 2: Complex page (should use AI)
def test_complex_page():
    operator = create_ai_operator()
    operator.page.goto("https://confusing-application-form.com")

    # Should use AI vision for complex layout
    action = operator.decide_next_action()

    assert operator.stats['ai_used'] == 1  # AI used

# Test 3: Full job application
def test_job_application():
    operator = create_ai_operator()

    goal = Goal(
        objective="Apply to Python Developer job at TechCorp",
        success_criteria=["application submitted", "thank you"]
    )

    success = operator.work_towards_goal(goal)

    # Check efficiency
    stats = operator.get_stats()
    assert stats['ai_percentage'] < 20  # <20% AI usage
    assert success == True
```

**Deliverable:** Verified AI integration working

---

### Phase 6: Full Application Workflow (90 min)

**Files to create:**
- `workflows/job_application_workflow.py` - Complete pipeline
- `test_end_to_end_application.py` - Full test

**Workflow:**

```python
class JobApplicationWorkflow:
    """
    Complete job application pipeline with AI vision
    """

    def __init__(self, api_key: str):
        self.operator = create_ai_operator(api_key)
        self.knowledge_base = KnowledgeBase()

    def apply_to_job(self, job_url: str, user_profile: Dict) -> Dict:
        """
        Full application workflow:
        1. Navigate to job
        2. Read job description (AI vision)
        3. Click Apply
        4. Fill application form (AI + rules)
        5. Upload resume
        6. Submit
        7. Verify success
        """

        self.operator.start_session()

        try:
            # Step 1: Navigate
            self.operator.page.goto(job_url)
            time.sleep(2)

            # Step 2: Analyze job posting (AI vision)
            analysis_goal = Goal(
                objective="Understand job requirements",
                success_criteria=["requirements", "qualifications"]
            )
            vision = self.operator.see()
            job_analysis = self._analyze_job_with_ai(vision)

            # Step 3: Find and click Apply button
            apply_goal = Goal(
                objective="Click on Apply button",
                success_criteria=["application", "form"]
            )
            self.operator.work_towards_goal(apply_goal)

            # Step 4: Fill application form
            form_goal = Goal(
                objective="Complete application form",
                success_criteria=["submit", "send application"]
            )
            self.operator.work_towards_goal(form_goal)

            # Step 5: Submit
            submit_goal = Goal(
                objective="Submit application",
                success_criteria=["thank you", "submitted", "received"]
            )
            success = self.operator.work_towards_goal(submit_goal)

            # Step 6: Verify
            final_vision = self.operator.see()
            verified = self._verify_submission(final_vision)

            return {
                'success': success and verified,
                'job_url': job_url,
                'actions_taken': len(self.operator.memory.actions_taken),
                'ai_calls_made': self.operator.stats['ai_used'],
                'cost_estimate': self.operator.stats['ai_used'] * 0.02,  # ~$0.02 per call
                'job_analysis': job_analysis
            }

        finally:
            self.operator.close_session()
```

**Deliverable:** End-to-end job application working with AI

---

## 📊 Cost Optimization Strategy

### Expected Costs:

| Scenario | Rules | AI Calls | Cost per Application |
|----------|-------|----------|---------------------|
| Simple application | 95% | 1-2 calls | ~$0.04 |
| Complex application | 80% | 5-8 calls | ~$0.12 |
| Very complex | 60% | 15-20 calls | ~$0.30 |

### Optimization Tactics:

1. **Caching**: Save AI decisions for similar pages
2. **Batch processing**: Group similar decisions
3. **Smart routing**: Use rules whenever possible
4. **Screenshot optimization**: Compress images
5. **Prompt efficiency**: Shorter, focused prompts

**Target**: <$0.10 per application with hybrid mode

---

## 🎯 Success Criteria

### Phase 1-2: Configuration ✅
- [ ] API keys loaded
- [ ] Prompts working
- [ ] Can call Claude API

### Phase 3-4: Integration ✅
- [ ] Claude Vision returning decisions
- [ ] Hybrid mode working
- [ ] <20% AI usage on simple tasks

### Phase 5: Testing ✅
- [ ] Works on Indeed
- [ ] Handles complex forms
- [ ] Error recovery working

### Phase 6: Production ✅
- [ ] Complete job application
- [ ] Success rate >80%
- [ ] Cost <$0.15 per application

---

## 📅 Timeline

| Phase | Duration | Completion |
|-------|----------|------------|
| 1. Configuration | 30 min | Day 1 |
| 2. Prompts | 45 min | Day 1 |
| 3. Claude Integration | 60 min | Day 1 |
| 4. Hybrid Engine | 45 min | Day 1 |
| 5. Testing | 60 min | Day 2 |
| 6. Full Workflow | 90 min | Day 2 |

**Total**: ~5.5 hours over 2 days

---

## 🚀 Deliverables

1. ✅ **Configuration system** - API keys, settings
2. ✅ **Prompt library** - 5+ templates
3. ✅ **Claude Vision engine** - Screenshot analysis
4. ✅ **Hybrid decision system** - Smart routing
5. ✅ **Cost optimizer** - <$0.15/application
6. ✅ **Full workflow** - End-to-end application
7. ✅ **Test suite** - Comprehensive validation
8. ✅ **Documentation** - Usage guide

---

## 📝 Next Actions

1. **Get API key**: Sign up at console.anthropic.com
2. **Add to .env**: `ANTHROPIC_API_KEY=sk-ant-...`
3. **Run Phase 1**: Configuration setup
4. **Test basic call**: Verify API working
5. **Build incrementally**: One phase at a time

---

Ready to start with Phase 1?
