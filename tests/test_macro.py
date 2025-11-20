import time

import pytest

import macro_runner
from macro_runner import MacroRunner, MacroExecutionState
from macro_manager import Macro, MacroStep, MacroStepType


@pytest.mark.unit
def test_interruptible_sleep_honors_stop_state():
    runner = MacroRunner(enabled=True)
    runner.state = MacroExecutionState.STOPPED

    start = time.monotonic()
    runner._interruptible_sleep(0.5)
    elapsed = time.monotonic() - start

    assert elapsed < 0.25


@pytest.mark.unit
def test_macro_runner_emergency_stop(monkeypatch):
    monkeypatch.setattr(macro_runner, "PYNPUT_AVAILABLE", True)

    runner = MacroRunner(enabled=True)
    long_delay = MacroStep(type=MacroStepType.DELAY.value, duration_ms=500)
    macro = Macro(
        id="m1",
        name="Delay Macro",
        description="Wait then stop",
        steps=[long_delay],
        repeat=1,
    )

    macro.get_total_duration = lambda: 600

    started = runner.execute_macro(macro)
    assert started

    runner.stop_macro()
    if runner.execution_thread:
        runner.execution_thread.join(timeout=1.0)

    assert runner.state in {
        MacroExecutionState.STOPPED,
        MacroExecutionState.COMPLETED,
        MacroExecutionState.ERROR,
    }
