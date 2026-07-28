"""
Enterprise AI Builder
Kernel - Bootstrap
Version: 0.1.0

RFC:
    RFC-0002 - Dependency Injection and Service Container
"""

from __future__ import annotations

from runtime.engine import RuntimeEngine

from actions.bootstrap import create_action_registry

from kernel.service_container import ServiceContainer


class KernelBootstrap:
    """
    Composition Root for Enterprise AI Builder.

    Responsibilities:

    - Initialize framework services.
    - Register built-in services.
    - Construct RuntimeEngine.
    - Provide a fully configured runtime.

    All framework initialization should begin here.
    """

    def __init__(self) -> None:
        self.container = ServiceContainer()

    def initialize(self) -> ServiceContainer:
        """
        Initialize all built-in framework services.
        """

        registry = create_action_registry()

        self.container.register(
            "action_registry",
            registry,
        )

        return self.container

    def create_runtime_engine(
        self,
        project: dict,
    ) -> RuntimeEngine:
        """
        Create a configured RuntimeEngine.
        """

        registry = self.container.resolve("action_registry")

        return RuntimeEngine(
            project=project,
            registry=registry,
        )
