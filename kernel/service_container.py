"""
Enterprise AI Builder
Kernel - Service Container
Version: 0.3.0

RFC:
    RFC-0002 - Dependency Injection and Service Container
    RFC-0003 - Service Lifetime Model
    RFC-0004 - Service Registration API
"""

from __future__ import annotations

from typing import Any, Callable

from kernel.service_descriptor import (
    ServiceDescriptor,
    ServiceLifetime,
)


class ServiceContainer:
    """
    Lightweight Dependency Injection container.

    The public API remains intentionally small while allowing
    future extension through ServiceDescriptor.
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceDescriptor] = {}

    def register(self, name: str, service: Any) -> None:
        """
        Backward-compatible registration.

        Equivalent to register_singleton().
        """
        self.register_singleton(name, service)

    def register_singleton(self, name: str, service: Any) -> None:
        """
        Register a singleton service instance.
        """
        self._services[name] = ServiceDescriptor(
            name=name,
            lifetime=ServiceLifetime.SINGLETON,
            instance=service,
        )

    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
    ) -> None:
        """
        Register a singleton factory.

        Factory execution semantics are intentionally deferred to
        a future sprint.
        """
        self._services[name] = ServiceDescriptor(
            name=name,
            lifetime=ServiceLifetime.SINGLETON,
            factory=factory,
        )

    def register_transient(
        self,
        name: str,
        factory: Callable[[], Any],
    ) -> None:
        """
        Register a transient factory.

        A new instance will eventually be created on every resolve.
        Resolution semantics are introduced in a later sprint.
        """
        self._services[name] = ServiceDescriptor(
            name=name,
            lifetime=ServiceLifetime.TRANSIENT,
            factory=factory,
        )

    def resolve(self, name: str) -> Any:
        """
        Resolve a registered service.
        """

        descriptor = self._services.get(name)

        if descriptor is None:
            raise KeyError(f"Service '{name}' is not registered.")

        if descriptor.instance is not None:
            return descriptor.instance

        if descriptor.factory is not None:
            return descriptor.factory()

        raise RuntimeError(
            f"Service '{name}' has neither an instance nor a factory."
        )

    def contains(self, name: str) -> bool:
        """
        Check whether a service is registered.
        """
        return name in self._services

    def remove(self, name: str) -> None:
        """
        Remove a registered service.
        """
        self._services.pop(name, None)

    def clear(self) -> None:
        """
        Remove all registered services.
        """
        self._services.clear()

    def __contains__(self, name: str) -> bool:
        return self.contains(name)

    def __len__(self) -> int:
        return len(self._services)
