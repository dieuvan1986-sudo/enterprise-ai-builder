# RFC-0003: Service Lifetime Model

- **Status:** Draft
- **Author:** Enterprise AI Builder Team
- **Created:** 2026-07
- **Related RFCs:** RFC-0002
- **Related ADRs:** ADR-0001

---

# Purpose

This RFC defines the service lifetime model used by the Dependency Injection system of Enterprise AI Builder.

The objective is to establish a simple, explicit, and predictable lifecycle model that remains suitable for long-term framework evolution.

---

# Motivation

Framework services do not all share the same lifecycle.

Some services should exist for the lifetime of the application.

Others should exist only during workflow execution.

Some should be created every time they are requested.

Without a consistent lifetime model:

- resources become difficult to manage;
- testing becomes inconsistent;
- plugin behavior becomes unpredictable;
- future distributed execution becomes harder.

---

# Goals

The service lifetime model shall:

- remain simple;
- be explicit;
- support testing;
- support plugins;
- support future distributed runtime;
- avoid hidden behavior.

---

# Non-Goals

This RFC intentionally excludes:

- automatic lifetime inference;
- annotation-based scopes;
- reflection-based injection;
- thread-local containers;
- request-based web scopes.

These concerns may be evaluated in future RFCs.

---

# Lifetime Types

Enterprise AI Builder defines exactly three service lifetimes.

## Singleton

One instance exists during the entire lifetime of the framework.

Typical examples:

- Configuration
- Logger
- PluginManager
- ActionRegistry
- LLM Provider Registry

---

## Scoped

One instance exists during one workflow execution.

Typical examples:

- WorkflowState
- ActionContext
- ExecutionContext

---

## Transient

A new instance is created whenever requested.

Typical examples:

- Validators
- Builders
- Temporary helper classes

---

# Responsibilities

## ServiceContainer

Responsible for:

- storing registrations;
- resolving services;
- enforcing lifetime behavior.

---

## KernelBootstrap

Responsible for:

- creating the ServiceContainer;
- registering built-in services;
- initializing singleton services.

---

## RuntimeEngine

Responsible for:

- consuming services;
- never creating framework services directly.

---

# Constraints

The following rules apply.

- Lifetime must always be explicit.
- Services must not silently change lifetime.
- Runtime components must not create singleton services.
- Plugins must respect lifetime definitions.
- Circular dependencies remain unsupported.

---

# Migration Strategy

Existing services may continue using direct construction during migration.

Future framework code should progressively migrate to ServiceContainer-based resolution.

Backward compatibility should be preserved whenever practical.

---

# Future Evolution

Future RFCs may introduce:

- Factory Registration
- Lazy Resolution
- Service Decoration
- Service Replacement
- Child Containers
- Distributed Containers

These extensions must remain compatible with the three core lifetime types.

---

# Open Questions

The following topics remain intentionally undecided:

- asynchronous service initialization;
- lifecycle events;
- service disposal;
- scoped nested containers.

These will be addressed in future RFCs if needed.

---

# Conclusion

Enterprise AI Builder adopts a lightweight service lifetime model consisting of:

- Singleton
- Scoped
- Transient

This model prioritizes clarity, maintainability, predictable behavior, and long-term extensibility while avoiding unnecessary complexity.
