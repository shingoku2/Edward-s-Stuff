#!/usr/bin/env python3
"""
Test for interruptible macro delays
"""

import time
from src.macro_runner import MacroRunner, MacroExecutionState
from src.macro_manager import Macro, MacroStep, MacroStepType

def test_interruptible_delay():
    """Test that _interruptible_sleep can be stopped quickly"""
    print("Testing interruptible delay...")

    # Create a macro runner
    runner = MacroRunner(enabled=True)

    # Test 1: Normal completion of delay
    print("  Test 1: Normal delay completion...")
    start = time.time()
    runner._interruptible_sleep(0.5)
    elapsed = time.time() - start

    if 0.4 < elapsed < 0.6:
        print(f"    ✓ Normal delay works (took {elapsed:.2f}s)")
    else:
        print(f"    ✗ Delay time unexpected: {elapsed:.2f}s")
        return False

    # Test 2: Interrupted delay
    print("  Test 2: Interrupted delay...")
    runner.state = MacroExecutionState.RUNNING
    start = time.time()

    # Start sleep in background
    import threading
    def sleep_task():
        runner._interruptible_sleep(5.0)  # Long delay

    thread = threading.Thread(target=sleep_task)
    thread.start()

    # Wait a bit, then stop
    time.sleep(0.2)
    runner.state = MacroExecutionState.STOPPED
    thread.join(timeout=2.0)

    elapsed = time.time() - start

    if elapsed < 1.0:  # Should stop quickly, not wait 5 seconds
        print(f"    ✓ Delay stopped quickly (took {elapsed:.2f}s instead of 5s)")
    else:
        print(f"    ✗ Delay did not stop quickly: {elapsed:.2f}s")
        return False

    # Test 3: Verify it checks state during sleep
    print("  Test 3: State checking during sleep...")
    runner.state = MacroExecutionState.RUNNING
    start = time.time()

    def delayed_stop():
        time.sleep(0.3)
        runner.state = MacroExecutionState.STOPPED

    stop_thread = threading.Thread(target=delayed_stop)
    stop_thread.start()

    runner._interruptible_sleep(5.0)

    elapsed = time.time() - start
    stop_thread.join()

    if 0.2 < elapsed < 0.5:
        print(f"    ✓ State checked during sleep (stopped at {elapsed:.2f}s)")
    else:
        print(f"    ✗ State check timing unexpected: {elapsed:.2f}s")
        return False

    return True

def test_macro_with_interruptible_delays():
    """Test that macros with delays can be stopped"""
    print("\nTesting macro execution with interruptible delays...")

    # Create a macro with a long delay
    macro = Macro(
        id="test-macro",
        name="Test Macro",
        description="Test macro with long delay",
        game_profile_id=None,
        steps=[
            MacroStep(type=MacroStepType.DELAY.value, duration_ms=10000)  # 10 second delay
        ],
        enabled=True,
        repeat=1
    )

    runner = MacroRunner(enabled=True)

    # Execute macro in background
    import threading

    start = time.time()
    runner.execute_macro(macro)

    # Wait a bit, then stop
    time.sleep(0.3)
    runner.stop_macro()

    # Wait for execution thread to finish
    if runner.execution_thread:
        runner.execution_thread.join(timeout=2.0)

    elapsed = time.time() - start

    if elapsed < 2.0:  # Should stop quickly, not wait 10 seconds
        print(f"  ✓ Macro stopped quickly (took {elapsed:.2f}s instead of 10s)")
        return True
    else:
        print(f"  ✗ Macro did not stop quickly: {elapsed:.2f}s")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("INTERRUPTIBLE DELAY TEST")
    print("=" * 60)

    test1_passed = test_interruptible_delay()
    test2_passed = test_macro_with_interruptible_delays()

    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        exit(1)
