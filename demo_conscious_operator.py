#!/usr/bin/env python3
"""
DEMO: Conscious Operator in Action
Shows the operator working consciously instead of following scripts
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.conscious_operator import ConsciousOperator, Goal
import logging
import time

# Setup logging to see what operator is thinking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def demo_basic_operation():
    """
    Demo 1: Basic conscious operation
    Shows SEE → THINK → ACT → VERIFY loop
    """
    print("=" * 80)
    print("🧠 DEMO 1: Basic Conscious Operation")
    print("=" * 80)
    print("\nWatch the operator:")
    print("  1. See what's on the page (vision)")
    print("  2. Think about what to do (decision)")
    print("  3. Act on the decision (execution)")
    print("  4. Verify it worked (validation)")
    print("\n" + "=" * 80 + "\n")

    operator = ConsciousOperator(headless=False)
    operator.start_session()

    try:
        # Navigate to a job site
        print("🚀 Navigating to Indeed...")
        operator.page.goto("https://www.indeed.com")
        time.sleep(2)

        # Define simple goal
        goal = Goal(
            objective="Search for Python developer jobs",
            success_criteria=["python developer", "jobs"],
            max_attempts=5,
            max_duration_minutes=5
        )

        print(f"\n🎯 Goal: {goal.objective}")
        print("Watch the browser - operator will:")
        print("  - Look for search box")
        print("  - Fill it with 'python developer'")
        print("  - Click search")
        print("  - Verify results appeared\n")

        # Let operator work
        success = operator.work_towards_goal(goal)

        print("\n" + "=" * 80)
        if success:
            print("✅ SUCCESS: Goal achieved!")
        else:
            print("❌ FAILED: Goal not achieved")

        print(f"📊 Actions taken: {len(operator.memory.actions_taken)}")
        print("\nRecent actions:")
        for action in operator.memory.actions_taken[-5:]:
            print(f"  - {action.type}: {action.reasoning}")
        print("=" * 80)

        input("\n\nPress Enter to continue to Demo 2...")

    finally:
        operator.close_session()


def demo_recovery():
    """
    Demo 2: Automatic recovery from failures
    Shows how operator handles unexpected situations
    """
    print("\n" + "=" * 80)
    print("🛡️ DEMO 2: Automatic Recovery")
    print("=" * 80)
    print("\nThis demo shows recovery from:")
    print("  - Broken selectors")
    print("  - Network delays")
    print("  - Unexpected UI changes")
    print("\n" + "=" * 80 + "\n")

    operator = ConsciousOperator(headless=False)
    operator.start_session()

    try:
        print("🚀 Navigating to job site...")
        operator.page.goto("https://www.seek.com.au")
        time.sleep(3)

        # This goal will encounter some failures
        goal = Goal(
            objective="Find software developer jobs in Melbourne",
            success_criteria=["software developer", "melbourne"],
            failure_indicators=["error", "not found"],
            max_attempts=8,  # More attempts to show recovery
            max_duration_minutes=5
        )

        print(f"\n🎯 Goal: {goal.objective}")
        print("Watch how operator:")
        print("  - Tries different selectors if first fails")
        print("  - Adapts to page layout")
        print("  - Recovers from errors")
        print("  - Keeps trying until success\n")

        # Work with recovery
        success = operator.work_towards_goal(goal)

        print("\n" + "=" * 80)
        if success:
            print("✅ SUCCESS: Achieved goal despite challenges!")
        else:
            print("⚠️ Goal not fully achieved, but operator kept trying")

        print(f"\n📊 Statistics:")
        print(f"  Total actions: {len(operator.memory.actions_taken)}")
        print(f"  Failed strategies: {len(operator.memory.failed_strategies)}")
        print(f"  Successful strategies: {len(operator.memory.successful_strategies)}")
        print("=" * 80)

        input("\n\nPress Enter to continue to Demo 3...")

    finally:
        operator.close_session()


def demo_learning():
    """
    Demo 3: Learning system
    Shows knowledge persistence across sessions
    """
    print("\n" + "=" * 80)
    print("📚 DEMO 3: Learning & Memory")
    print("=" * 80)
    print("\nThis demo shows:")
    print("  - Knowledge base creation")
    print("  - Strategy learning")
    print("  - Memory persistence")
    print("\n" + "=" * 80 + "\n")

    from app.services.operator_resilience import KnowledgeBase

    # Create knowledge base
    kb = KnowledgeBase("demo_knowledge.pkl")

    print(f"📚 Current Knowledge Base:")
    print(f"  Strategies: {len(kb.strategies)}")
    print(f"  Recoveries: {len(kb.recoveries)}")
    print(f"  Field Mappings: {len(kb.field_mappings)}")

    # Add some learned strategies
    print("\n🧠 Learning new strategies...")

    kb.add_successful_strategy(
        goal_type="apply_to_job",
        page_url="https://www.indeed.com/apply",
        actions=[
            {"type": "click", "target": "button.apply-button"},
            {"type": "fill_field", "target": "input[name='name']", "value": "John Galgano"}
        ],
        duration=45.5
    )

    kb.add_successful_strategy(
        goal_type="search_jobs",
        page_url="https://www.linkedin.com/jobs",
        actions=[
            {"type": "fill_field", "target": "input.search-box", "value": "python developer"},
            {"type": "click", "target": "button[type='submit']"}
        ],
        duration=12.3
    )

    kb.learn_field_mapping("input[placeholder*='Email']", "john.galgano@example.com")
    kb.learn_field_mapping("input[placeholder*='Phone']", "+61412345678")

    print("✅ Learned 2 strategies and 2 field mappings")

    # Show updated knowledge
    print(f"\n📚 Updated Knowledge Base:")
    print(f"  Strategies: {len(kb.strategies)}")
    print(f"  Field Mappings: {len(kb.field_mappings)}")

    print("\n💾 Knowledge saved to: demo_knowledge.pkl")
    print("   This persists across sessions!")

    # Show best strategy
    best = kb.get_best_strategy("apply_to_job", "https://www.indeed.com/apply")
    if best:
        print(f"\n🏆 Best strategy for 'apply_to_job' on Indeed:")
        print(f"   Success rate: {best.success_rate:.0%}")
        print(f"   Times used: {best.times_used}")
        print(f"   Avg duration: {best.avg_duration_seconds:.1f}s")

    print("\n" + "=" * 80)
    print("📚 Knowledge base will grow as operator works!")
    print("   After 100 applications: ~50+ learned strategies")
    print("   After 1000 applications: ~200+ learned strategies")
    print("=" * 80)


def main():
    """Run all demos"""
    print("\n" * 2)
    print("=" * 80)
    print("             🧠 CONSCIOUS OPERATOR DEMONSTRATION")
    print("=" * 80)
    print("\nThis will demonstrate three key features:")
    print("  1. Vision-based operation (SEE → THINK → ACT → VERIFY)")
    print("  2. Automatic recovery from failures")
    print("  3. Learning and knowledge persistence")
    print("\nEach demo will open a browser window showing the operator working.")
    print("=" * 80)

    input("\n\nPress Enter to start Demo 1...")

    try:
        # Demo 1: Basic operation
        demo_basic_operation()

        # Demo 2: Recovery
        demo_recovery()

        # Demo 3: Learning
        demo_learning()

        print("\n\n" + "=" * 80)
        print("✅ ALL DEMOS COMPLETE!")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("  ✅ Operator makes decisions based on what it SEES")
        print("  ✅ Adapts to page changes automatically")
        print("  ✅ Recovers from failures without intervention")
        print("  ✅ Learns successful strategies over time")
        print("  ✅ Can work continuously for hours")
        print("\nNext Steps:")
        print("  1. Review CONSCIOUS_OPERATOR_GUIDE.md for full documentation")
        print("  2. Try with AI decision making (requires API key)")
        print("  3. Run continuous worker on real job applications")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
