"""
Enterprise AI Builder
Kernel - Service Descriptor
Version: 0.1.0

RFC:
    RFC-0002 - Dependency Injection and Service Container
    RFC-0003 - Service Lifetime Model
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable


class ServiceLifetime(Enum):
    """
    Defines the lifetime of a registered service.
    """

    SINGLETON = auto()
    SCOPED = auto()
    TRANSIENT = auto()


@dataclass(slots=True)
class ServiceDescriptor:
    """
    Describes a registered service.

    A ServiceDescriptor stores the metadata required by the
    ServiceContainer to manage a service throughout its lifecycle.
    """

    name: str

    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON

    instance: Any | None = None

    factory: Callable[[], Any] | None = None
