# System Specification - A Simple Payment Service (3rd-Party Gateway Integration)

## 1. Overview

### Problem Statement
Design a centralized payment orchestration layer that abstracts external payment gateways. It standardizes how payments are created, monitored, and reconciled, while guaranteeing:
    - no duplicate operations (idempotency)
    - high reliability despite external failures
    - a single, consistent source of truth for payment state

### Goals & Non-Goals

#### Goals
  - Abstract multiple payment providers behind a unified API
  - Support payment initiatiion and payment status tracking
  - Ensures idempotent payment processing
  - Handle provider failures gracefully (retry/fallback where applicable)
  - Maintain reliable payment state internally
  - Provide audit logs for all payment operations

#### Non-Goals
  - Acting as a financial institution or holding funds
  - Building fraud detection systems
  - Managing chargebacks/disputes (future scope)
  - Real-time settlement guarantees (depends on provider)