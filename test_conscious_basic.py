#!/usr/bin/env python3
"""
Simple test: Basic conscious operator functionality
Tests each component step by step
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.conscious_operator import ConsciousOperator, Goal, Vision, Action
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_1_initialization():
    """Test 1: Can we create an operator?"""
    print("\n" + "="*80)
    print("TEST 1: Initialization")
    print("="*80)

    try:
        operator = ConsciousOperator(headless=True)
        print("✅ Operator created")
        return operator
    except Exception as e:
        print(f"❌ Failed to create operator: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_2_browser_session(operator):
    """Test 2: Can we start browser session?"""
    print("\n" + "="*80)
    print("TEST 2: Browser Session")
    print("="*80)

    try:
        operator.start_session()
        print("✅ Browser session started")
        return True
    except Exception as e:
        print(f"❌ Failed to start session: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_navigation(operator):
    """Test 3: Can we navigate to a page?"""
    print("\n" + "="*80)
    print("TEST 3: Navigation")
    print("="*80)

    try:
        operator.page.goto("https://example.com", wait_until="domcontentloaded")
        print(f"✅ Navigated to: {operator.page.url}")
        print(f"   Page title: {operator.page.title()}")
        return True
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        return False


def test_4_vision(operator):
    """Test 4: Can we see the page?"""
    print("\n" + "="*80)
    print("TEST 4: Vision System")
    print("="*80)

    try:
        vision = operator.see()

        print(f"✅ Vision captured:")
        print(f"   URL: {vision.current_url}")
        print(f"   Title: {vision.page_title}")
        print(f"   Screenshot size: {len(vision.screenshot)} bytes")
        print(f"   Visible inputs: {len(vision.visible_inputs)}")
        print(f"   Visible buttons: {len(vision.visible_buttons)}")
        print(f"   Visible text elements: {len(vision.visible_text)}")

        if vision.visible_text:
            print(f"\n   First 3 text elements:")
            for text in vision.visible_text[:3]:
                print(f"     - {text[:60]}")

        return vision
    except Exception as e:
        print(f"❌ Vision failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_5_decision_making(operator, vision):
    """Test 5: Can we make a decision?"""
    print("\n" + "="*80)
    print("TEST 5: Decision Making")
    print("="*80)

    try:
        goal = Goal(
            objective="Test goal",
            success_criteria=["example"],
            max_attempts=3
        )

        # Use rule-based decision (no AI needed)
        action = operator.think(vision, goal)

        print(f"✅ Decision made:")
        print(f"   Action type: {action.type}")
        print(f"   Target: {action.target}")
        print(f"   Reasoning: {action.reasoning}")

        return action
    except Exception as e:
        print(f"❌ Decision making failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_6_action_execution(operator):
    """Test 6: Can we execute an action?"""
    print("\n" + "="*80)
    print("TEST 6: Action Execution")
    print("="*80)

    try:
        # Simple wait action
        action = Action(type="wait", value="2", reasoning="Test wait action")

        print(f"   Executing: {action.type}")
        success = operator.act(action)

        if success:
            print("✅ Action executed successfully")
        else:
            print("⚠️ Action completed but may have had issues")

        return success
    except Exception as e:
        print(f"❌ Action execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_7_simple_goal(operator):
    """Test 7: Can we work towards a simple goal?"""
    print("\n" + "="*80)
    print("TEST 7: Simple Goal Achievement")
    print("="*80)

    try:
        # Navigate to example.com
        operator.page.goto("https://example.com", wait_until="domcontentloaded")

        # Goal: Just verify we can see "Example Domain"
        goal = Goal(
            objective="Verify we can see Example Domain",
            success_criteria=["Example Domain"],
            failure_indicators=["404", "error"],
            max_attempts=3,
            max_duration_minutes=1
        )

        print(f"   Goal: {goal.objective}")
        print(f"   Success criteria: {goal.success_criteria}")

        # Work on goal
        success = operator.work_towards_goal(goal)

        print(f"\n   Actions taken: {len(operator.memory.actions_taken)}")
        for i, action in enumerate(operator.memory.actions_taken[-5:], 1):
            print(f"     {i}. {action.type}: {action.reasoning}")

        if success:
            print("\n✅ Goal achieved!")
        else:
            print("\n⚠️ Goal not achieved (but that's okay for testing)")

        return success
    except Exception as e:
        print(f"❌ Goal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("CONSCIOUS OPERATOR - BASIC FUNCTIONALITY TEST")
    print("="*80)
    print("\nTesting each component step by step...\n")

    results = {}
    operator = None

    try:
        # Test 1: Initialization
        operator = test_1_initialization()
        results['initialization'] = operator is not None

        if not operator:
            print("\n❌ FATAL: Cannot proceed without operator")
            return

        # Test 2: Browser session
        results['browser_session'] = test_2_browser_session(operator)

        if not results['browser_session']:
            print("\n❌ FATAL: Cannot proceed without browser")
            return

        # Test 3: Navigation
        results['navigation'] = test_3_navigation(operator)

        # Test 4: Vision
        vision = test_4_vision(operator)
        results['vision'] = vision is not None

        # Test 5: Decision making
        action = test_5_decision_making(operator, vision) if vision else None
        results['decision_making'] = action is not None

        # Test 6: Action execution
        results['action_execution'] = test_6_action_execution(operator)

        # Test 7: Simple goal
        results['simple_goal'] = test_7_simple_goal(operator)

    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if operator and operator.page:
            try:
                operator.close_session()
                print("\n✅ Browser closed")
            except:
                pass

    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext step: Run 'python test_conscious_indeed.py' for real job site test")
    else:
        print("\n⚠️ Some tests failed - review output above")

    print("="*80)


if __name__ == "__main__":
    main()
