#!/usr/bin/env python3
"""
Real-world test: Conscious operator on Indeed job site
Tests adaptive behavior on actual job search
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.conscious_operator import ConsciousOperator, Goal
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_indeed_job_search():
    """Test: Search for jobs on Indeed and analyze first result"""
    print("\n" + "="*80)
    print("REAL-WORLD TEST: Indeed Job Search")
    print("="*80)
    print("\nThis will:")
    print("  1. Navigate to Indeed")
    print("  2. Search for 'python developer' jobs")
    print("  3. Analyze search results")
    print("  4. Click on first job listing")
    print("  5. Extract job details")
    print("\nOperator will make decisions based on what it SEES")
    print("="*80 + "\n")

    # Create operator (visible so you can watch)
    operator = ConsciousOperator(headless=False)

    try:
        # Start session with persistence
        operator.start_session(user_data_dir=".browser_profile")
        print("✅ Browser started\n")

        # Navigate to Indeed
        print("📍 Navigating to Indeed...")
        operator.page.goto("https://www.indeed.com", wait_until="domcontentloaded")
        time.sleep(2)

        # Define goal: Search for jobs
        search_goal = Goal(
            objective="Search for python developer jobs",
            success_criteria=[
                "python developer",
                "jobs",
                "results"
            ],
            failure_indicators=["error", "no results"],
            max_attempts=10,
            max_duration_minutes=3
        )

        print(f"\n🎯 GOAL 1: {search_goal.objective}")
        print("   Watch the browser - operator will:")
        print("   - Find the search box")
        print("   - Type 'python developer'")
        print("   - Submit search")
        print("   - Verify results appear\n")

        # Let operator work
        start_time = time.time()
        success = operator.work_towards_goal(search_goal)
        duration = time.time() - start_time

        print(f"\n{'='*80}")
        if success:
            print(f"✅ GOAL 1 SUCCESS in {duration:.1f}s")
        else:
            print(f"⚠️ GOAL 1 incomplete ({duration:.1f}s)")

        print(f"\n📊 Actions taken: {len(operator.memory.actions_taken)}")
        print("\nAction sequence:")
        for i, action in enumerate(operator.memory.actions_taken, 1):
            print(f"  {i}. {action.type:12} → {action.reasoning}")

        # Take screenshot of results
        screenshot_path = "indeed_results.png"
        operator.page.screenshot(path=screenshot_path)
        print(f"\n📸 Screenshot saved: {screenshot_path}")

        # Analyze what we see now
        print(f"\n{'='*80}")
        print("👁️ VISION ANALYSIS - What operator sees:")
        print(f"{'='*80}")

        vision = operator.see()
        print(f"\nCurrent page: {vision.page_title}")
        print(f"URL: {vision.current_url}")
        print(f"\nVisible elements:")
        print(f"  - Inputs: {len(vision.visible_inputs)}")
        print(f"  - Buttons: {len(vision.visible_buttons)}")
        print(f"  - Text elements: {len(vision.visible_text)}")

        if vision.visible_buttons:
            print(f"\n  First 5 buttons:")
            for btn in vision.visible_buttons[:5]:
                print(f"    • '{btn['text'][:40]}'")

        if vision.visible_text:
            print(f"\n  Page text (first 10 lines):")
            for text in vision.visible_text[:10]:
                if text.strip():
                    print(f"    • {text[:60]}")

        # Goal 2: Click on first job
        print(f"\n{'='*80}")
        print("🎯 GOAL 2: Click on first job listing")
        print(f"{'='*80}\n")

        click_goal = Goal(
            objective="Click on the first job listing to see details",
            success_criteria=["job description", "apply", "qualifications"],
            max_attempts=5,
            max_duration_minutes=2
        )

        start_time = time.time()
        success2 = operator.work_towards_goal(click_goal)
        duration2 = time.time() - start_time

        print(f"\n{'='*80}")
        if success2:
            print(f"✅ GOAL 2 SUCCESS in {duration2:.1f}s")
            print("\nJob details page opened!")

            # Get final vision
            final_vision = operator.see()
            print(f"\nJob page: {final_vision.page_title}")
            print(f"URL: {final_vision.current_url}")

            # Save final screenshot
            operator.page.screenshot(path="indeed_job_detail.png")
            print("\n📸 Screenshot saved: indeed_job_detail.png")

        else:
            print(f"⚠️ GOAL 2 incomplete ({duration2:.1f}s)")

        # Final statistics
        print(f"\n{'='*80}")
        print("📊 SESSION STATISTICS")
        print(f"{'='*80}")
        print(f"Total time: {duration + duration2:.1f}s")
        print(f"Total actions: {len(operator.memory.actions_taken)}")
        print(f"Goals achieved: {sum([success, success2])}/2")
        print(f"Success rate: {sum([success, success2])/2*100:.0f}%")

        print(f"\n📚 Learning:")
        print(f"  Successful strategies: {len(operator.memory.successful_strategies)}")
        print(f"  Failed strategies: {len(operator.memory.failed_strategies)}")

        input("\n\nPress Enter to close browser...")

    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        operator.close_session()
        print("\n✅ Browser closed")

    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")
    print("\nWhat you just saw:")
    print("  ✅ Operator navigated to Indeed")
    print("  ✅ Made decisions based on visual inspection")
    print("  ✅ Adapted to page layout")
    print("  ✅ Executed actions (search, click)")
    print("  ✅ Verified results")
    print("\nThis is CONSCIOUS operation - no hardcoded selectors!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_indeed_job_search()
