from typing import Any


class ServiceRegistry:
    """
    Registry for application-wide services.

    The ServiceRegistry stores singleton-like service instances that can
    be shared across the framework, including Runtime, Plugins,
    Validators, LLM adapters, Tool adapters, and future components.
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Register a service instance.
        """
        self._services[name] = service

    def get(self, name: str) -> Any:
        """
        Return a registered service.
        """
        if name not in self._services:
            raise ValueError(f"Unknown service: {name}")

        return self._services[name]

    def has(self, name: str) -> bool:
        """
        Check whether a service exists.
        """
        return name in self._services

    def remove(self, name: str) -> None:
        """
        Remove a registered service.
        """
        if name in self._services:
            del self._services[name]

    def names(self) -> list[str]:
        """
        Return all registered service names.
        """
        return sorted(self._services.keys())

    def clear(self) -> None:
        """
        Remove all registered services.
        """
        self._services.clear()
