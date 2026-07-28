# RFC-0004: Service Registration API

- **Status:** Draft
- **Author:** Enterprise AI Builder Team
- **Created:** 2026-07
- **Related RFCs:** RFC-0002, RFC-0003
- **Related ADRs:** ADR-0001

---

# Purpose

This RFC defines how services are registered into the ServiceContainer.

The goal is to provide an explicit, predictable, and extensible registration API while preserving backward compatibility.

---

# Motivation

As the framework evolves, services may be registered from:

- the Kernel;
- plugins;
- extensions;
- SDKs;
- user applications.

A consistent registration model is required to avoid ambiguity and ensure predictable behavior.

---

# Design Principles

The registration API shall follow these principles:

- Explicit over implicit.
- Backward compatible.
- Easy to understand.
- Easy to extend.
- Independent of reflection.
- Independent of runtime inspection.

---

# Public Registration API

The ServiceContainer exposes the following public methods.

## register()

Registers an existing singleton instance.

This method is retained for backward compatibility.

Example:

```python
container.register("logger", logger)
```

---

## register_singleton()

Registers a singleton instance explicitly.

Example:

```python
container.register_singleton("logger", logger)
```

---

## register_factory()

Registers a factory responsible for creating service instances.

The factory implementation is defined by future RFCs.

Example:

```python
container.register_factory(
    "plugin_manager",
    create_plugin_manager,
)
```

---

## register_transient()

Registers a transient service.

A new instance will be created whenever the service is resolved.

Example:

```python
container.register_transient(
    "validator",
    WorkflowValidator,
)
```

---

# Registration Rules

The following rules apply.

- Service names must be unique.
- Registration is explicit.
- Registration order is deterministic.
- Lifetime is always declared.
- Hidden registrations are prohibited.

---

# Duplicate Registration

Duplicate service names should raise an exception by default.

Future RFCs may introduce explicit override mechanisms.

Silent replacement is prohibited.

---

# Naming Convention

Service names should:

- use lowercase;
- use snake_case;
- describe responsibilities rather than implementations.

Examples:

- logger
- configuration
- plugin_manager
- workflow_parser

Avoid:

- Logger
- MyLogger
- LoggerServiceV2

---

# Plugin Registration

Plugins should register services through the same public API.

Plugins must not manipulate internal ServiceContainer state.

---

# Backward Compatibility

Existing code using:

```python
container.register(...)
```

shall continue to function without modification.

Internally, register() behaves as register_singleton().

---

# Future Evolution

Future RFCs may introduce:

- scoped registration;
- conditional registration;
- service replacement;
- decorators;
- lazy registration.

---

# Open Questions

The following items remain intentionally undefined:

- service priorities;
- service aliases;
- automatic registration;
- assembly scanning.

---

# Conclusion

Enterprise AI Builder adopts an explicit registration model based on a small public API.

The design prioritizes readability, predictable behavior, backward compatibility, and long-term maintainability.
