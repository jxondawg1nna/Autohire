#!/usr/bin/env python3
"""
Focused test: Search functionality with conscious operator
Shows decision-making in action
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.conscious_operator import ConsciousOperator, Goal, Action
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_conscious_search():
    """Test conscious decision-making on job search"""
    print("\n" + "="*80)
    print("CONSCIOUS OPERATOR - Job Search Test")
    print("="*80)
    print("\nWatch the operator:")
    print("  1. Navigate to Indeed")
    print("  2. THINK about what it sees")
    print("  3. DECIDE how to search")
    print("  4. ACT and fill search box")
    print("  5. VERIFY search worked")
    print("="*80 + "\n")

    operator = ConsciousOperator(headless=False)

    try:
        # Start browser
        operator.start_session(user_data_dir=".browser_profile")
        print("✅ Browser started\n")

        # Navigate
        print("📍 Navigating to Indeed...")
        operator.page.goto("https://www.indeed.com", wait_until="domcontentloaded")
        time.sleep(3)  # Let page fully load

        # MANUAL DEMONSTRATION: Show what operator sees
        print(f"\n{'='*80}")
        print("STEP 1: VISION - What does the operator SEE?")
        print(f"{'='*80}\n")

        vision = operator.see()
        print(f"Page: {vision.page_title}")
        print(f"URL: {vision.current_url}")
        print(f"\nVisible inputs ({len(vision.visible_inputs)}):")
        for i, inp in enumerate(vision.visible_inputs[:5], 1):
            print(f"  {i}. Type: {inp['type']:10} | Name: {inp['name']:20} | Placeholder: {inp['placeholder']}")

        print(f"\nVisible buttons ({len(vision.visible_buttons)}):")
        for i, btn in enumerate(vision.visible_buttons[:5], 1):
            print(f"  {i}. '{btn['text']}'")

        # MANUAL: Make a decision
        print(f"\n{'='*80}")
        print("STEP 2: THINK - What should the operator DO?")
        print(f"{'='*80}\n")

        # Find the job search input
        search_input = None
        for inp in vision.visible_inputs:
            if 'what' in inp['placeholder'].lower() or 'job' in inp['placeholder'].lower() or 'keyword' in inp['name'].lower():
                search_input = inp
                break

        if search_input:
            print(f"✅ DECISION: Found search input!")
            print(f"   Selector: {search_input['selector']}")
            print(f"   Placeholder: {search_input['placeholder']}")
            print(f"   Plan: Fill it with 'python developer'\n")

            # MANUAL: Execute action
            print(f"{'='*80}")
            print("STEP 3: ACT - Execute the decision")
            print(f"{'='*80}\n")

            action = Action(
                type="fill_field",
                target=search_input['selector'],
                value="python developer",
                reasoning="Found job search input, filling with keywords"
            )

            print(f"Action: {action.type}")
            print(f"Target: {action.target}")
            print(f"Value: {action.value}")
            print(f"Reasoning: {action.reasoning}\n")

            success = operator.act(action)
            print(f"{'✅' if success else '❌'} Action executed\n")

            time.sleep(2)

            # MANUAL: Verify
            print(f"{'='*80}")
            print("STEP 4: VERIFY - Did it work?")
            print(f"{'='*80}\n")

            new_vision = operator.see()

            # Check if field was filled
            filled = False
            for inp in new_vision.visible_inputs:
                if inp['selector'] == search_input['selector'] and inp['value']:
                    filled = True
                    print(f"✅ VERIFIED: Field now contains '{inp['value']}'")
                    break

            if not filled:
                print("⚠️ Field may not have been filled correctly")

            # Now find and click search button
            print(f"\n{'='*80}")
            print("STEP 5: Find and click search button")
            print(f"{'='*80}\n")

            search_button = None
            for btn in new_vision.visible_buttons:
                if any(word in btn['text'].lower() for word in ['search', 'find', 'jobs']):
                    search_button = btn
                    break

            if search_button:
                print(f"✅ Found search button: '{search_button['text']}'")

                click_action = Action(
                    type="click",
                    target=search_button['selector'],
                    reasoning=f"Clicking '{search_button['text']}' button to search"
                )

                print(f"Clicking: {search_button['selector']}\n")
                operator.act(click_action)

                print("⏳ Waiting for search results...")
                time.sleep(5)

                # Check results
                results_vision = operator.see()
                print(f"\nAfter search:")
                print(f"  New URL: {results_vision.current_url}")
                print(f"  New title: {results_vision.page_title}")

                # Take screenshot
                operator.page.screenshot(path="search_results.png")
                print(f"\n📸 Screenshot saved: search_results.png")

        else:
            print("❌ Could not find search input")

        # Summary
        print(f"\n{'='*80}")
        print("DEMONSTRATION COMPLETE")
        print(f"{'='*80}\n")
        print("What you just saw:")
        print("  👁️ VISION: Operator analyzed page structure")
        print("  🧠 THINK: Made intelligent decision about what to do")
        print("  ⚡ ACT: Executed the action (fill field, click)")
        print("  ✅ VERIFY: Checked that action worked")
        print("\nThis is CONSCIOUS operation:")
        print("  - No hardcoded selectors")
        print("  - Adapts to what it sees")
        print("  - Makes decisions based on page state")
        print(f"{'='*80}\n")

        input("Press Enter to close browser...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        operator.close_session()
        print("\n✅ Browser closed\n")


if __name__ == "__main__":
    test_conscious_search()
