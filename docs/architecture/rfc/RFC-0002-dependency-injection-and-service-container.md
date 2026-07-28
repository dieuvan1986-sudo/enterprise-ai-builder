# RFC-0002: Dependency Injection and Service Container

- **Status:** Draft
- **Author:** Enterprise AI Builder Team
- **Created:** 2026-07
- **Related RFCs:** RFC-0000, RFC-0001
- **Related ADRs:** ADR-0001

---

# Purpose

This RFC defines the Dependency Injection (DI) model and the Service Container architecture used throughout Enterprise AI Builder.

The goal is to establish a unified mechanism for creating, registering, resolving, and managing framework services while keeping modules loosely coupled and highly testable.

---

# Motivation

As the framework grows, more shared services will be introduced, including:

- Action Registry
- Plugin Manager
- Knowledge Providers
- Prompt Providers
- Event Bus
- Logger
- Metrics
- Configuration
- LLM Providers

Without a Dependency Injection mechanism, modules will gradually become tightly coupled through direct object creation and cross-module imports.

This RFC establishes a single source of truth for service management.

---

# Current Problems

Today several components create dependencies directly.

Example:

```python
self.registry = create_action_registry()
```

Although acceptable during early development, this approach introduces several limitations:

- Difficult to replace implementations
- Harder to test
- Reduced modularity
- Plugin integration becomes more complex
- Lifecycle management is impossible

---

# Goals

The Dependency Injection system must provide:

- Loose coupling
- Explicit dependencies
- Testability
- Replaceable implementations
- Plugin extensibility
- Predictable service lifecycle
- Minimal runtime overhead

---

# Non-Goals

The framework does **not** aim to become a full-featured IoC container comparable to Spring Framework or Autofac.

Features intentionally excluded include:

- Reflection-based injection
- Automatic constructor scanning
- Runtime code generation
- Annotation-driven dependency injection

The design should remain explicit and predictable.

---

# Architecture

The Dependency Injection architecture consists of four primary components.

```text
Kernel
   │
   ▼
ServiceContainer
   │
   ├─────────────┐
   ▼             ▼
Registry      Plugin Manager
   │             │
   └──────┬──────┘
          ▼
     Runtime Engine
```

The ServiceContainer becomes the central location responsible for resolving framework services.

---

# Service Registration

Services are registered during application bootstrap.

Example:

```text
container.register(ActionRegistry)

container.register(Logger)

container.register(Configuration)

container.register(PluginManager)
```

Registration should be explicit.

Implicit discovery is intentionally avoided.

---

# Service Resolution

Components should request dependencies rather than construct them.

Preferred:

```text
RuntimeEngine
      │
      ▼
ActionRegistry
```

Instead of:

```text
RuntimeEngine
      │
      ▼
create_action_registry()
```

The RuntimeEngine should receive an ActionRegistry instance from the ServiceContainer.

---

# Service Lifetime

The framework defines three service lifetimes.

## Singleton

One shared instance during application lifetime.

Examples:

- Configuration
- Logger
- Plugin Manager
- Action Registry

---

## Scoped

One instance per workflow execution.

Examples:

- Workflow Context
- Execution Context

---

## Transient

New instance every time the service is requested.

Examples:

- Temporary helper objects
- Builders
- Validators

---

# Kernel Responsibilities

The Kernel is responsible for:

- Initializing the ServiceContainer
- Registering built-in services
- Loading plugins
- Managing service lifecycle
- Providing dependency resolution

The Kernel should **not** execute workflows.

---

# Runtime Responsibilities

The Runtime Engine should:

- Request required services
- Execute workflows
- Never construct framework services directly

---

# Plugin Integration

Plugins may register new services during initialization.

Example:

```text
Plugin
   │
   ▼
register_services(container)
```

Plugins should never modify existing core services directly.

Extension should occur through registration or decoration.

---

# Testing

Dependency Injection greatly simplifies testing.

Example:

```text
Mock Action Registry

↓

Inject into Runtime Engine

↓

Run isolated tests
```

No production registry is required.

---

# Future Evolution

Future framework capabilities may build upon the same container:

- Tool Providers
- Knowledge Providers
- Agent Providers
- Scheduler
- Event Bus
- Distributed Runtime
- Remote Service Registry

No architectural changes should be required.

---

# Alternatives Considered

## Direct Object Construction

Simple but tightly coupled.

Rejected.

---

## Global Singleton

Easy to implement but introduces hidden dependencies.

Rejected.

---

## Third-party DI Framework

Provides advanced features but increases complexity and external dependencies.

Rejected.

---

# Backward Compatibility

Existing code may continue to use direct construction during migration.

Future development should adopt the ServiceContainer as the preferred approach.

---

# Conclusion

Enterprise AI Builder adopts an explicit Dependency Injection model centered around a lightweight ServiceContainer.

The design prioritizes simplicity, modularity, maintainability, and long-term extensibility over advanced IoC features.
