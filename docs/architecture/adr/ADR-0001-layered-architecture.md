# ADR-0001: Adopt a Layered Architecture

- **Status:** Accepted
- **Date:** 2026-07
- **Deciders:** Enterprise AI Builder Team
- **Supersedes:** None
- **Superseded By:** None

---

# Context

Enterprise AI Builder is intended to become a long-term framework for building enterprise AI applications.

As the project grows, additional capabilities such as plugins, agents, tools, knowledge providers, event systems, and distributed execution will be introduced.

Without a clearly defined architectural structure, the project would become increasingly difficult to maintain and evolve.

A foundational architectural decision is therefore required.

---

# Decision

Enterprise AI Builder adopts a **Layered Architecture** as its primary architectural style.

The logical dependency hierarchy is:

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

Dependencies always flow downward.

Reverse dependencies are prohibited.

Circular dependencies are prohibited.

---

# Rationale

Layered Architecture provides several advantages for this project.

## Simplicity

The dependency direction is easy to understand.

New contributors can quickly identify where functionality belongs.

---

## Maintainability

Each layer has a clearly defined responsibility.

Changes remain localized.

---

## Extensibility

New framework capabilities can usually be introduced by adding components within existing layers rather than restructuring the architecture.

---

## Testability

Each layer can be tested independently.

Lower layers can be mocked when testing higher layers.

---

## Long-Term Evolution

The framework can continue to grow without requiring major architectural redesign.

---

# Alternatives Considered

## Clean Architecture

Pros:

- Strong separation of concerns
- Excellent dependency control

Cons:

- Additional complexity for framework contributors
- More abstraction than currently required

Decision:

Some Clean Architecture principles will be adopted internally, but the overall project remains Layered.

---

## Hexagonal Architecture

Pros:

- Strong isolation from infrastructure
- Excellent for business applications

Cons:

- Less suitable as the primary structure for a reusable framework
- Introduces additional adapter complexity

Decision:

Hexagonal concepts may be used inside individual modules where appropriate.

---

## Microkernel Architecture

Pros:

- Excellent extensibility

Cons:

- Requires a mature plugin ecosystem
- Introduces unnecessary complexity at the current stage

Decision:

Plugin capabilities will be added incrementally while retaining the layered foundation.

---

# Consequences

Positive:

- Clear dependency direction
- Easier onboarding
- Better maintainability
- Stable architectural foundation

Negative:

- Some cross-layer interactions require explicit APIs
- Certain advanced patterns may require additional abstractions in the future

---

# Related RFCs

- RFC-0000 Project Vision & Philosophy
- RFC-0001 Overall Architecture

---

# Notes

Future ADRs should refine architectural decisions without contradicting RFC-0000 or RFC-0001.

If an ADR conflicts with an approved RFC, the RFC takes precedence.
