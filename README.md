# Enterprise AI Builder

> Enterprise-grade AI Workflow Framework for building maintainable, extensible, and production-ready AI applications.

---

## Overview

Enterprise AI Builder is an open-source framework for building AI-powered applications using a structured workflow architecture.

The framework is designed around long-term maintainability, modularity, and predictable engineering practices rather than rapid feature accumulation.

Its goal is to provide a stable foundation for enterprise AI systems that can evolve for many years.

---

## Core Principles

- Architecture Before Features
- API First Design
- Plugin First Extension
- Explicit Dependencies
- Stable Public APIs
- Long-Term Maintainability

---

## High-Level Architecture

```text
Application
    ↓
Kernel
    ↓
Runtime
    ↓
Actions / Workflows
    ↓
Core
```

For detailed architecture, see:

- RFC-0000 – Project Vision & Philosophy
- RFC-0001 – Overall Architecture
- ADR-0001 – Adopt a Layered Architecture

---

## Project Structure

```text
enterprise-ai-builder/
├── actions/
├── builder/
├── cli/
├── compiler/
├── docs/
│   ├── architecture/
│   │   ├── adr/
│   │   ├── diagrams/
│   │   └── rfc/
│   ├── developer/
│   └── reference/
├── kernel/
├── registry/
├── runtime/
├── tests/
├── validator/
├── workflows/
└── README.md
```

---

## Documentation

Architecture documentation is located under:

```text
docs/architecture/
```

Important documents:

- RFC-0000 — Project Vision & Philosophy
- RFC-0001 — Overall Architecture
- ADR-0001 — Adopt a Layered Architecture

Future architectural changes should be documented through RFCs and ADRs.

---

## Development Philosophy

Enterprise AI Builder follows an RFC-driven development process.

The typical workflow is:

```text
Idea
    ↓
Requirement
    ↓
RFC
    ↓
Architecture Review
    ↓
Implementation
    ↓
Testing
    ↓
Documentation
```

Major architectural changes should not be implemented without an approved RFC.

---

## Current Status

Current phase:

> Framework Engineering

Current focus:

- Repository Foundation
- Documentation
- Architecture
- Kernel Design

---

## Roadmap

Planned major milestones include:

- Kernel
- Dependency Injection
- Plugin System
- Workflow Engine
- Tool Framework
- Agent Runtime
- Knowledge Framework
- Event System
- Distributed Runtime

---

## Contributing

Contribution guidelines will be published in:

```text
CONTRIBUTING.md
```

---

## License

License information will be added before the first public release.

---

## Vision

Build an enterprise AI framework that remains understandable, maintainable, and extensible for years to come.
