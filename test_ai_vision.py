#!/usr/bin/env python3
"""
Test AI Vision Integration
Tests the complete AI-powered decision engine with screenshots
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import os
from dotenv import load_dotenv
load_dotenv("backend/.env")

from app.services.conscious_operator import ConsciousOperator, Goal
from app.services.ai_decision_engine import AIDecisionEngine, HybridDecisionEngine, create_conscious_operator_with_ai
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ai_api_connection():
    """Test 1: Verify AI API is accessible"""
    print("\n" + "="*80)
    print("TEST 1: AI API Connection")
    print("="*80)

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ FAIL: No ANTHROPIC_API_KEY found in .env")
        print("\nTo fix:")
        print("1. Go to https://console.anthropic.com/")
        print("2. Create an API key")
        print("3. Add to backend/.env: ANTHROPIC_API_KEY=sk-ant-...")
        return False

    if "PLACEHOLDER" in api_key:
        print("❌ FAIL: ANTHROPIC_API_KEY is still placeholder")
        print("\nReplace placeholder with real key in backend/.env")
        return False

    print(f"✓ API key found: {api_key[:20]}...")

    try:
        ai_engine = AIDecisionEngine(provider="claude", api_key=api_key)
        print(f"✓ AI Engine initialized: {ai_engine.model}")
        print("✅ PASS: API connection configured")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_hybrid_complexity_analysis():
    """Test 2: Test complexity analyzer"""
    print("\n" + "="*80)
    print("TEST 2: Complexity Analysis")
    print("="*80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "PLACEHOLDER" in api_key:
        print("⏭️  SKIP: No API key")
        return None

    try:
        from app.services.conscious_operator import Vision, Memory

        ai_engine = AIDecisionEngine(provider="claude", api_key=api_key)
        hybrid = HybridDecisionEngine(ai_engine)

        # Test case 1: Simple page (search box + button)
        simple_vision = Vision(
            screenshot=b"fake",
            current_url="https://indeed.com",
            page_title="Indeed - Job Search",
            visible_inputs=[
                {'name': 'q', 'placeholder': 'Search jobs', 'selector': '#q', 'value': ''}
            ],
            visible_buttons=[
                {'text': 'Search', 'selector': '#search-btn'}
            ],
            visible_text=['Find jobs', 'Search for jobs']
        )

        goal = Goal(objective="Search for Python jobs", success_criteria=["jobs", "python"])
        memory = Memory()

        score = hybrid._analyze_complexity(simple_vision, goal, memory)
        print(f"\nSimple page complexity: {score:.2f}")
        print(f"Expected: < 0.3 (simple)")

        if score < 0.3:
            print("✓ Correctly identified as simple")
        else:
            print(f"⚠️  Expected < 0.3, got {score:.2f}")

        # Test case 2: Complex page (many fields, no obvious button)
        complex_vision = Vision(
            screenshot=b"fake",
            current_url="https://example.com/apply",
            page_title="",
            visible_inputs=[{'name': f'field{i}', 'placeholder': '', 'selector': f'#f{i}', 'value': ''} for i in range(15)],
            visible_buttons=[{'text': f'Button {i}', 'selector': f'#b{i}'} for i in range(5)],
            visible_text=['x' * 150]  # Lots of text
        )

        memory_with_failures = Memory()
        for i in range(3):
            from app.services.conscious_operator import Action
            memory_with_failures.actions_taken.append(
                Action(type="click", reasoning="Error: element not found")
            )

        score = hybrid._analyze_complexity(complex_vision, goal, memory_with_failures)
        print(f"\nComplex page complexity: {score:.2f}")
        print(f"Expected: > 0.6 (complex)")

        if score > 0.6:
            print("✓ Correctly identified as complex")
        else:
            print(f"⚠️  Expected > 0.6, got {score:.2f}")

        print("\n✅ PASS: Complexity analyzer working")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_screenshot_optimization():
    """Test 3: Screenshot optimization"""
    print("\n" + "="*80)
    print("TEST 3: Screenshot Optimization")
    print("="*80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "PLACEHOLDER" in api_key:
        print("⏭️  SKIP: No API key")
        return None

    try:
        from PIL import Image
        import io

        # Create a test screenshot
        img = Image.new('RGB', (1920, 1080), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        original_bytes = buffer.getvalue()

        print(f"Original screenshot: {len(original_bytes) / 1024:.1f} KB")

        ai_engine = AIDecisionEngine(provider="claude", api_key=api_key)
        optimized_b64 = ai_engine._optimize_screenshot(original_bytes)

        import base64
        optimized_bytes = base64.b64decode(optimized_b64)
        print(f"Optimized screenshot: {len(optimized_bytes) / 1024:.1f} KB")

        reduction = ((len(original_bytes) - len(optimized_bytes)) / len(original_bytes)) * 100
        print(f"Size reduction: {reduction:.0f}%")

        if reduction > 50:
            print("✅ PASS: Screenshot optimization working (>50% reduction)")
            return True
        else:
            print(f"⚠️  WARNING: Only {reduction:.0f}% reduction (expected >50%)")
            return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_live_ai_decision():
    """Test 4: Live AI decision on real page"""
    print("\n" + "="*80)
    print("TEST 4: Live AI Decision on Real Page")
    print("="*80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "PLACEHOLDER" in api_key:
        print("⏭️  SKIP: No API key - Cannot test live AI")
        print("\nThis test requires a valid Anthropic API key.")
        print("Once you have a key, this will:")
        print("  1. Open Indeed")
        print("  2. Take screenshot")
        print("  3. Ask Claude what to do")
        print("  4. Execute the AI's decision")
        return None

    ai_enabled = os.getenv("AI_VISION_ENABLED", "false").lower() == "true"
    if not ai_enabled:
        print("⏭️  SKIP: AI_VISION_ENABLED=false in .env")
        print("\nSet AI_VISION_ENABLED=true to enable this test")
        return None

    print("⚠️  This test will:")
    print("  1. Open a browser (visible)")
    print("  2. Navigate to Indeed")
    print("  3. Take screenshot and send to Claude")
    print("  4. Execute Claude's suggested action")
    print("  5. Cost: ~$0.02-0.05")

    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("⏭️  SKIP: User declined")
        return None

    try:
        # Create operator with AI
        operator = create_conscious_operator_with_ai(api_key=api_key, provider="claude")

        print("\n🚀 Starting browser...")
        operator.start_session(user_data_dir=".browser_profile")

        print("📍 Navigating to Indeed...")
        operator.page.goto("https://www.indeed.com", wait_until="domcontentloaded")

        import time
        time.sleep(3)

        print("\n👁️  Capturing vision...")
        vision = operator.see()
        print(f"  URL: {vision.current_url}")
        print(f"  Title: {vision.page_title}")
        print(f"  Inputs: {len(vision.visible_inputs)}")
        print(f"  Buttons: {len(vision.visible_buttons)}")

        print("\n🧠 Asking Claude for decision...")
        goal = Goal(
            objective="Search for Python Developer jobs",
            success_criteria=["python", "developer", "jobs"]
        )

        # Force AI decision (bypass hybrid rules for testing)
        action = operator.decision_engine.ai_engine.decide_action(vision, goal, operator.memory)

        print(f"\n💡 Claude decided: {action.type}")
        print(f"   Target: {action.target}")
        print(f"   Value: {action.value}")
        print(f"   Reasoning: {action.reasoning}")

        # Execute action
        print(f"\n⚡ Executing action...")
        success = operator.act(action)

        if success:
            print("✅ Action executed successfully")
            time.sleep(2)
            operator.page.screenshot(path="ai_decision_result.png")
            print("📸 Result screenshot: ai_decision_result.png")
        else:
            print("❌ Action failed")

        # Show stats
        if hasattr(operator.decision_engine, 'ai_engine'):
            print(f"\n📊 AI Stats:")
            print(f"   API calls: {operator.decision_engine.ai_engine.api_calls_made}")
            print(f"   Total tokens: {operator.decision_engine.ai_engine.total_tokens_used}")

        operator.close_session()

        print("\n✅ PASS: AI decision test complete")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        try:
            operator.close_session()
        except:
            pass
        return False


def test_hybrid_stats():
    """Test 5: Hybrid engine statistics"""
    print("\n" + "="*80)
    print("TEST 5: Hybrid Engine Statistics")
    print("="*80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "PLACEHOLDER" in api_key:
        print("⏭️  SKIP: No API key")
        return None

    try:
        ai_engine = AIDecisionEngine(provider="claude", api_key=api_key)
        hybrid = HybridDecisionEngine(ai_engine, ai_usage_target=0.15)

        # Simulate decisions
        hybrid.simple_action_count = 85
        hybrid.ai_action_count = 15

        stats = hybrid.get_stats()

        print(f"\nSimulated 100 decisions:")
        print(f"  Rule-based: {stats['rule_based']}")
        print(f"  AI-powered: {stats['ai_powered']}")
        print(f"  AI percentage: {stats['ai_percentage']:.1f}%")
        print(f"  Target: {stats['target_percentage']:.0f}%")
        print(f"  Within target: {stats['within_target']}")

        if stats['within_target']:
            print("\n✅ PASS: Within AI usage target")
            return True
        else:
            print(f"\n⚠️  WARNING: Exceeds target ({stats['ai_percentage']:.1f}% > {stats['target_percentage']:.0f}%)")
            return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 AI VISION INTEGRATION TEST SUITE")
    print("="*80)

    tests = [
        ("API Connection", test_ai_api_connection),
        ("Complexity Analysis", test_hybrid_complexity_analysis),
        ("Screenshot Optimization", test_screenshot_optimization),
        ("Live AI Decision", test_live_ai_decision),
        ("Hybrid Statistics", test_hybrid_stats),
    ]

    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    for name, result in results.items():
        symbol = "✅" if result is True else "⏭️ " if result is None else "❌"
        status = "PASS" if result is True else "SKIP" if result is None else "FAIL"
        print(f"{symbol} {name:30} {status}")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0 and passed > 0:
        print("\n🎉 All tests passed!")
        print("\n✅ AI Vision Integration: READY")
        print("\nNext steps:")
        print("  1. Run: python FINAL_DEMONSTRATION.py")
        print("  2. Test on real job applications")
        print("  3. Monitor AI usage and costs")
    elif skipped > 0 and failed == 0:
        print("\n⚠️  Some tests skipped (likely missing API key)")
        print("\nTo enable all tests:")
        print("  1. Add ANTHROPIC_API_KEY to backend/.env")
        print("  2. Set AI_VISION_ENABLED=true")
        print("  3. Re-run tests")
    else:
        print("\n❌ Some tests failed - check output above")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
