"""
Runtime lifecycle definitions.

This module defines the execution phases of the Enterprise AI Builder
Runtime. It serves as the single source of truth for lifecycle state
throughout the framework.
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class RuntimePhase(str, Enum):
    """
    Execution phases of the Runtime.

    The order of these phases is defined by RFC-0005 and must remain
    stable unless superseded by a future approved RFC.
    """

    INITIALIZE = "initialize"
    LOAD_SERVICES = "load_services"
    LOAD_WORKFLOW = "load_workflow"
    BUILD_EXECUTION_CONTEXT = "build_execution_context"
    EXECUTE_WORKFLOW = "execute_workflow"
    PUBLISH_EVENTS = "publish_events"
    CLEANUP = "cleanup"
    SHUTDOWN = "shutdown"


#: Ordered lifecycle phases defined by RFC-0005.
RUNTIME_LIFECYCLE: Final[tuple[RuntimePhase, ...]] = (
    RuntimePhase.INITIALIZE,
    RuntimePhase.LOAD_SERVICES,
    RuntimePhase.LOAD_WORKFLOW,
    RuntimePhase.BUILD_EXECUTION_CONTEXT,
    RuntimePhase.EXECUTE_WORKFLOW,
    RuntimePhase.PUBLISH_EVENTS,
    RuntimePhase.CLEANUP,
    RuntimePhase.SHUTDOWN,
)


def is_terminal_phase(phase: RuntimePhase) -> bool:
    """
    Return True if the given phase is terminal.
    """
    return phase is RuntimePhase.SHUTDOWN


def next_phase(phase: RuntimePhase) -> RuntimePhase | None:
    """
    Return the next lifecycle phase.

    Returns None if the supplied phase is the final phase.
    """
    index = RUNTIME_LIFECYCLE.index(phase)

    if index == len(RUNTIME_LIFECYCLE) - 1:
        return None

    return RUNTIME_LIFECYCLE[index + 1]
