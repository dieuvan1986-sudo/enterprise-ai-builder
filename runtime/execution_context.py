"""
Runtime execution context.

This module defines the execution context shared across the Runtime
lifecycle. It represents the canonical state of a workflow execution
and is intended to be consumed by specialized contexts such as
ActionContext, EventContext and PluginContext.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.lifecycle import RuntimePhase
from runtime.workflow import Workflow
from runtime.workflow_state import WorkflowState


@dataclass(slots=True)
class ExecutionContext:
    """
    Canonical runtime execution context.

    This object is owned by the Runtime and lives for the entire
    workflow execution lifecycle.
    """

    project: dict[str, Any]
    workflow: Workflow
    state: WorkflowState

    phase: RuntimePhase = RuntimePhase.INITIALIZE

    variables: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)
