# RFC-0001: Overall Architecture

- **Status:** Accepted
- **Version:** 1.0
- **Authors:** Enterprise AI Builder Team
- **Created:** 2026-07
- **Last Updated:** 2026-07

---

# 1. Purpose

This RFC defines the overall architecture of Enterprise AI Builder.

It establishes the major architectural layers, dependency rules, module responsibilities, and extension model for the framework.

All future architecture RFCs must remain compatible with this document unless explicitly superseded.

---

# 2. Goals

The architecture should:

- Be simple to understand
- Scale with project growth
- Encourage modular development
- Minimize coupling
- Maximize extensibility
- Keep public APIs stable
- Support long-term maintenance

---

# 3. Architectural Principles

Enterprise AI Builder follows these principles:

- Layered Architecture
- Dependency Inversion
- Single Responsibility
- Explicit Dependencies
- Composition over Inheritance
- API First Design
- Plugin First Extension

---

# 4. High-Level Architecture

The framework is organized into the following logical layers:

```text
+------------------------------------------------------+
|                  Application Layer                   |
+------------------------------------------------------+
|                      Kernel                          |
+------------------------------------------------------+
|                     Runtime                          |
+------------------------------------------------------+
|              Actions / Workflows                     |
+------------------------------------------------------+
|                       Core                           |
+------------------------------------------------------+
```

Each layer has a clearly defined responsibility.

---

# 5. Layer Responsibilities

## Application

Responsible for:

- Public API
- Application lifecycle
- Bootstrap
- Configuration entry point

The Application layer is the primary entry point for framework users.

---

## Kernel

Responsible for:

- Service Container
- Dependency Injection
- Plugin Management
- Service Lifecycle

Kernel coordinates the framework.

Kernel does not execute workflows directly.

---

## Runtime

Responsible for:

- Workflow execution
- Runtime context
- Execution pipeline
- Runtime state

Runtime should remain infrastructure-focused.

---

## Actions / Workflows

Responsible for:

- Business execution units
- Workflow definitions
- Action implementations

Actions should remain small and focused.

---

## Core

Responsible for:

- Shared abstractions
- Base interfaces
- Common exceptions
- Shared utilities

Core should have minimal external dependencies.

---

# 6. Dependency Rules

Dependencies always move downward.

```text
Application
    ↓
Kernel
    ↓
Runtime
    ↓
Actions
    ↓
Core
```

Reverse dependencies are not allowed.

Circular dependencies are not allowed.

---

# 7. Public API

Framework users should primarily interact with:

- Application
- Workflow
- Plugin
- Tool
- Agent
- Knowledge
- Config

Internal modules are not considered stable APIs.

---

# 8. Extension Model

Framework extensibility should rely on:

- Plugins
- Registries
- Dependency Injection
- Providers

Core framework code should rarely require modification when new capabilities are added.

---

# 9. Module Design Rules

Modules should:

- Have a single primary responsibility
- Minimize dependencies
- Expose a small public API
- Be independently testable

Large modules should be decomposed before becoming difficult to maintain.

---

# 10. Architecture Governance

Significant architectural changes require:

- RFC
- Architecture Review
- Implementation
- Tests
- Documentation

Architecture evolves intentionally.

---

# 11. Future Evolution

Future RFCs may introduce:

- Event Bus
- Capability System
- Tool Framework
- Agent Framework
- Knowledge Framework
- Distributed Runtime

These additions must respect the dependency rules defined in this RFC.

---

# 12. Out of Scope

This RFC does not define:

- Plugin API details
- Runtime execution model
- Dependency Injection implementation
- Workflow syntax
- Tool API
- Agent behavior

These topics are covered by dedicated RFCs.

---

# 13. Conclusion

The architecture emphasizes simplicity, modularity, and long-term maintainability.

Every future component should integrate into this layered architecture without violating dependency direction or increasing unnecessary complexity.
