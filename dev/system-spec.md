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

### 4. Functional Requirements
  - Create payment intents
  - Route payments to selected provider (Stripe, etc.)
  - Store payment state internally
  - Handle asynchronous payment confirmation (webhooks)
  - Support idempotent requests
  - Provide payment status query API
  - Log all provider interactions

### 5. Non-Functional Requirements
  - Consistency: Strong consistency for internal payment state
  - Reliability: No lost payment intents, No duplicated payment intents
  - Availability: 99.9%
  - Latency: <500ms for payment initiation  (excluding provider delay)
  - Scalability: Horizontal scaling for API and webhooks processing (should be able to handle growing traffic by: 1. adding more API servers when more payment requests come in and, 2. adding more workers to process incoming webhook events)
  - Security: PCI-aware design (no raw card storage)

### 6. Assumptions & Constraints
  - External payment providers handle actual fund movement
  - System stores only metadata + transaction state
  - Card data never touches system (tokenized via provider)
  - Multiple providers may be added in future
  - Webhooks are the source of truth for final payment status

### 7. High-Level Architecture

### Big Picture 
The payment service system sits in the middle:
Application (needing payment service) -> Payment Service -> External Providers(like Stripe)

The payment service system also listens for updates coming back from those providers

### Components
  - API Gateway
  - Payment Service (core orchestration)
  - Provider Adapter Layer (StripeAdapter, etc)
  - Webhook Handler Service
  - Database (payment state store)
  - Message Queue (optional but recommended)
  - Provider APIs (Stripe, etc.)