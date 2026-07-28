# Enterprise AI Builder - Development Roadmap

**Version:** 1.0  
**Status:** Active

---

# Vision

Build Enterprise AI Builder into an enterprise-grade AI Workflow Framework.

Applications such as AI Money Factory are built **on top of** the framework rather than inside it.

---

# Development Principles

Every feature follows the same workflow:

```
Idea
    ↓
RFC
    ↓
Architecture Review
    ↓
Implementation
    ↓
Unit Tests
    ↓
Documentation Update
    ↓
Regression Tests
    ↓
Done
```

Code is never implemented before architecture approval.

---

# Overall Progress

| Epic | Name | Status |
|------|------|--------|
| EP-000 | Foundation | ✅ Completed |
| EP-001 | Product Architecture | ✅ Completed |
| EP-002 | Runtime Core | 🚧 In Progress |
| EP-003 | Plugin Framework | ⏳ Planned |
| EP-004 | Provider Abstraction | ⏳ Planned |
| EP-005 | Knowledge Engine | ⏳ Planned |
| EP-006 | Memory System | ⏳ Planned |
| EP-007 | Agent Runtime | ⏳ Planned |
| EP-008 | SDK | ⏳ Planned |
| EP-009 | Reference Applications | ⏳ Planned |

---

# Epic 002 - Runtime Core

## Goal

Build a deterministic, extensible and observable Runtime.

### Sprint Status

| Sprint | Description | Status |
|---------|-------------|--------|
| RT-001 | Runtime Lifecycle | ✅ Completed |
| RT-002 | Execution Context | 🚧 In Progress |
| RT-003 | Event System | Planned |
| RT-004 | Middleware Pipeline | Planned |
| RT-005 | Error Model | Planned |
| RT-006 | Metrics & Tracing | Planned |
| RT-007 | Cancellation & Timeout | Planned |

---

# Epic 003 - Plugin Framework

Planned components:

- Plugin Manifest
- Plugin Loader
- Plugin Registry
- Plugin Lifecycle
- Plugin Dependency Resolution

---

# Epic 004 - Provider Abstraction

Planned components:

- LLM Provider
- Embedding Provider
- Vector Database Provider
- Storage Provider

---

# Epic 005 - Knowledge Engine

Planned components:

- Knowledge Sources
- Document Loader
- Chunking
- Embedding Pipeline
- Retrieval

---

# Epic 006 - Memory System

Planned components:

- Session Memory
- Long-term Memory
- Conversation Memory
- Memory Store

---

# Epic 007 - Agent Runtime

Planned components:

- Agent
- Multi-Agent
- Planner
- Coordinator
- Tool Execution

---

# Epic 008 - SDK

Planned components:

- Python SDK
- CLI SDK
- Public APIs
- Developer Experience

---

# Epic 009 - Reference Applications

Applications built using Enterprise AI Builder.

Examples:

- AI Money Factory
- Research Assistant
- Customer Service Agent
- Internal Enterprise Copilot

---

# Definition of Done

An Epic is considered complete only if:

- Architecture approved
- RFC approved
- Implementation completed
- Unit tests passed
- Regression tests passed
- Documentation updated
- Public APIs reviewed

---

# Current Focus

Current Epic:

**EP-002 – Runtime Core**

Current Sprint:

**RT-002 – Execution Context**

Next Sprint:

**RT-003 – Event System**
