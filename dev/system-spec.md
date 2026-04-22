# System Specification - A Simple Payment Service (3rd-Party Gateway Integration)

## 1. Overview

### Problem Statement
Design a centralized payment orchestration layer that abstracts external payment gateways. It standardizes how payments are created, monitored, and reconciled, while guaranteeing:
    - no duplicate operations (idempotency)
    - high reliability despite external failures
    - a single, consistent source of truth for payment state

### 2. Goals & Non-Goals

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

### 3. Users & Use Cases

#### User Types
  - Client Applications: SaaS apps initiating payments
  - End Users: Paying customers
  - Admin/System Operators: Monitoring and reconciliation

#### Core Use Cases
  - Create a payment intent
  - Process payment via provider (e.g. Stipe)
  - Retrieve payment status
  - Retry failed payments (where safe)
  - Reconcile internal state with provider state