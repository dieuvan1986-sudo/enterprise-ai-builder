"""
Unit tests for runtime lifecycle definitions.
"""

from runtime.lifecycle import (
    RUNTIME_LIFECYCLE,
    RuntimePhase,
    is_terminal_phase,
    next_phase,
)


def test_runtime_lifecycle_order():
    """Runtime lifecycle should follow RFC-0005."""
    assert RUNTIME_LIFECYCLE == (
        RuntimePhase.INITIALIZE,
        RuntimePhase.LOAD_SERVICES,
        RuntimePhase.LOAD_WORKFLOW,
        RuntimePhase.BUILD_EXECUTION_CONTEXT,
        RuntimePhase.EXECUTE_WORKFLOW,
        RuntimePhase.PUBLISH_EVENTS,
        RuntimePhase.CLEANUP,
        RuntimePhase.SHUTDOWN,
    )


def test_every_runtime_phase_is_in_lifecycle():
    """Every RuntimePhase must appear exactly once in the lifecycle."""
    assert set(RuntimePhase) == set(RUNTIME_LIFECYCLE)


def test_next_phase_sequence():
    """Every phase should transition to the correct next phase."""
    for current, expected in zip(
        RUNTIME_LIFECYCLE,
        RUNTIME_LIFECYCLE[1:],
    ):
        assert next_phase(current) is expected


def test_shutdown_has_no_next_phase():
    """Shutdown is the terminal lifecycle phase."""
    assert next_phase(RuntimePhase.SHUTDOWN) is None


def test_only_shutdown_is_terminal():
    """Only SHUTDOWN should be terminal."""
    for phase in RuntimePhase:
        if phase is RuntimePhase.SHUTDOWN:
            assert is_terminal_phase(phase) is True
        else:
            assert is_terminal_phase(phase) is False


def test_all_phases_are_unique():
    """Lifecycle must not contain duplicated phases."""
    assert len(RUNTIME_LIFECYCLE) == len(set(RUNTIME_LIFECYCLE))


def test_lifecycle_starts_with_initialize():
    """Lifecycle must always start with INITIALIZE."""
    assert RUNTIME_LIFECYCLE[0] is RuntimePhase.INITIALIZE


def test_lifecycle_ends_with_shutdown():
    """Lifecycle must always end with SHUTDOWN."""
    assert RUNTIME_LIFECYCLE[-1] is RuntimePhase.SHUTDOWN
