# System Specification - A Simple Payment Service (3rd-Party Gateway Integration)

## Stage 1 - Understand the problem
## Overview
### Problem Statement
Design a centralized payment orchestration layer that abstracts external payment gateways. It standardizes how payments are created, monitored, and reconciled, while guaranteeing:
    - no duplicate operations (idempotency)
    - high reliability despite external failures
    - a single, consistent source of truth for payment state


### Clarifying Questions

### 1. Who is using this?
### Primary Users
    - Client applications (businesses / backend services)
        - e.g. SaaS platforms, marketplaces, e-commerce systems
    - Not end users directly — they interact through the client app

### Secondary Users
    - End customers
        - The people actually making payments
    - Internal operators / developers
        - Monitor, debug, reconcile payments

## Key Insight
This is not a consumer product.
It is:
A backend infrastructure service used by other systems

That means:
    - API design matters more than UI
    - Reliability matters more than features
    - Observability is critical