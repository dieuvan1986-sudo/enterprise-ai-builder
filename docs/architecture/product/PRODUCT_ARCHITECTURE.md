# Enterprise AI Builder - Product Architecture

**Version:** 1.0 (Draft)

---

# 1. Vision

Enterprise AI Builder is an enterprise-grade AI workflow framework for building reliable, extensible, maintainable and production-ready AI applications.

The framework is designed to provide a stable architectural foundation rather than solve a single business problem.

Applications are built on top of Enterprise AI Builder.

Enterprise AI Builder is not an application.

---

# 2. Design Goals

The framework is designed around the following goals.

- Simplicity
- Explicit Architecture
- Plugin First
- Long-term Maintainability
- Enterprise Scalability
- Testability
- Backward Compatibility

---

# 3. Architecture Layers

```
+------------------------------------------------------+
|                  Business Applications               |
+------------------------------------------------------+
|                    SDK / Public API                  |
+------------------------------------------------------+
|                  Runtime & Workflow                  |
+------------------------------------------------------+
|             Registries & Extension Points            |
+------------------------------------------------------+
|          Kernel (DI, Bootstrap, Lifecycle)           |
+------------------------------------------------------+
```

Each layer only depends on lower layers.

Lower layers must never depend on upper layers.

---

# 4. Core Modules

## Kernel

Responsibilities:

- Dependency Injection
- Bootstrap
- Configuration
- Lifecycle
- Core Contracts

The Kernel is the most stable part of the framework.

---

## Registry

Responsible for discovering framework capabilities.

Examples:

- Action Registry
- Tool Registry
- Provider Registry
- Prompt Registry

---

## Runtime

Responsible for execution.

Responsibilities:

- Workflow Engine
- Execution Context
- Workflow State
- Template Rendering

Runtime coordinates execution.

Runtime does not contain business logic.

---

## SDK

Provides public APIs for developers.

Applications interact with the framework through the SDK.

Internal framework classes should not become part of the public SDK without architectural review.

---

## Applications

Applications represent business implementations.

Examples:

- AI Money Factory
- Customer Service Agent
- Research Assistant

Applications depend on the framework.

The framework never depends on applications.

---

# 5. Architectural Principles

## Framework First

Business logic belongs outside the framework.

Reusable capabilities belong inside the framework.

---

## Plugin First

Features should become plugins whenever practical.

Kernel growth should remain minimal.

---

## Explicit over Magic

Avoid:

- reflection
- hidden dependency injection
- implicit registration
- automatic discovery without configuration

Behavior should remain predictable.

---

## Composition over Inheritance

Prefer composition.

Inheritance should remain shallow.

---

## Documentation before Implementation

Architecture changes begin with documentation.

Implementation follows approved documentation.

---

## Stable Public APIs

Public APIs should remain stable.

Breaking changes require:

- RFC
- ADR
- Migration Strategy

---

# 6. Dependency Rules

Allowed:

Applications
→ SDK
→ Runtime
→ Registry
→ Kernel

Forbidden:

Kernel
→ Runtime

Kernel
→ Applications

Runtime
→ Applications

Registry
→ CLI

Providers
→ Runtime internals

---

# 7. Extension Model

Enterprise AI Builder is designed as an extensible platform.

Extensions may contribute:

- Actions
- Providers
- Tools
- Prompt Providers
- Workflows

Extensions communicate only through public extension APIs.

Internal framework objects must not be modified directly.

---

# 8. Documentation Hierarchy

Project documentation follows this hierarchy.

1. PRODUCT_ARCHITECTURE
2. RFC
3. ADR
4. Source Code

If implementation conflicts with approved architecture, the implementation should be considered incorrect until reviewed.

---

# 9. Long-Term Roadmap

Major architectural capabilities include:

- Workflow Engine
- Plugin System
- Knowledge System
- Memory System
- Provider Abstraction
- Multi-Agent Runtime
- Enterprise SDK

Each capability evolves independently while respecting the Product Architecture.

---

# 10. Conclusion

This document defines the architectural direction of Enterprise AI Builder.

Every RFC, ADR and implementation should remain consistent with this document unless an approved architectural revision explicitly supersedes it.
