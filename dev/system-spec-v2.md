# System Specification - A Simple Payment Service (3rd-Party Gateway Integration)

## Stage 1 - Understand the problem

### Problem Statement 
The payment service system sits between Client Apps and 3rd-party payment providers like Stripe and it standardizes how payments are created, monitored, and reconciled, while guaranteeing:
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


### 2. What problem does it actually solve?
#### Surface Problem
    - "Process payments using Stripe (or similar providers)"

#### Real Problem (deeper)
    - "Provide a reliable, consistent, and provider-agnostic way for systems to handle payments without tightly coupling to external payment APIs."

#### Pain Points being Solved
    - Every team integrating directly with Stripe duplicates logic
    - Handling webhooks, retries, failures is complex
    - Provider APIs can change or behave inconsistently
    - Hard to switch providers later (vendor lock-in)
    - No unified tracking of payment state across systems

#### Your System Provides
    - A single internal API
    - A consistent payment lifecycle model
    - Abstraction over providers
    - Reliability layer on top of unreliable external systems

### 3. What does success look like?
#### Functional Success
    - Payments are created and completed correctly
    - Payment status is always accurate

#### System-Level Success
    - No duplicate charges (Idempotency works)
    - No "lost" payments (every request is tracked)
    - Webhooks are processed reliably

#### Business-Level Success
    - Teams can integrate payments quickly
    - Switching from Stripe to another provider is low effort
    - Minimal operational incidents

#### Failure Definition
    - Payment marked "success" internally but failed externally
    - Duplicate charge due to retry
    - Webhook missed -> incorrect state

### 4. What is explicitly out of scope?
Storing or processing raw card data (PCI scope)
Building a UI/dashboard
Fraud detection systems
Dispute/chargeback handling
Multi-provider smart routing (can come later)
Subscription billing logic

#### Why this is important:
You are building:
    - A payment orchestration layer, not a full payment platform

### 5. Constraints
#### Technical Constraints
    - Must rely on external providers like Stripe
    - Must handle asynchronous workflows (webhooks)
    - Must support idempotent operations

#### System Constraints
    - External APIs can:
        - Fail
        - Timeout
        - Return inconsistent states
    - Webhooks can:
        - Arrive late
        - Arrive multiple times
        - Arrive out of order

#### Security Constraints
    - Must avoid handling sensitive card details directly
    - Must verify webhook signatures

#### Operational Constraints
    - System must be debuggable:
        - "What happened to this payment?" must always be answerable

### So, what are we building?
    - We are building a backend payment service that sits between client apps and payment providers like Stripe and provides a consistent API for creating and tracking payments.
    It ensures reliability through idempotency, webhook handling, and internal state management.
    The goal is to decouple application teams from payment provider complexity while maintaining accurate and auditable payment flows.


## Stage 2 - Define Requirements

### 1. Functional Requirements - What the system does
#### Core Payment Flow

#### Client System -> Payment Service System -> Payment Provider (e.g. Stripe)

    - A Client System (external app e.g. checkout service) can create a payment request (ask out payment service to initiate a payment) 
    - Our payment service system then sends the payment request to a third-party provider (e.g. Stripe)
    - The payment service system then stores and tracks the payment status internally

#### Payment Lifecycle
    - The system receives asynchronous updates from the provider via webhooks
    - The system validates, deduplicates, and processes incoming events
    - The system updates the persisted payment status based on provider events
    - The system maintain the latest payment status as the source of truth
    - Client apps can query the current status of a payment at anytime

#### Reliability & Safety
    - The system ensures idempotency for payment creation (no duplicate charges)
    - The system logs all payment-related events for audit purposes
    - The system handles duplicate or repeated webhook events safely

#### Observability & Debugging
A client (or internal user) can trace the lifecycle of a payment
The system records provider responses for debugging and reconciliation

#### Optional / Nice-to-Have
    - The system can retry failed provider requests (where safe)
    - The system can support multiple payment providers (extensible design)


### 2. Non-Functional Requirements — How the system does what it does
#### Availability: 
Question: How often can the system be down?
Decision:
    - Target:- 99.9%+ uptime
    - Payment creation should always be available
    - Temporary degradation acceptable for non-critical operations (e.g. logs)

Why it matters:
    - If payment fail during checkout -> direct revenue loss

#### Latency
Question: How fast must responses be?
Decision:
    - Payment initiation: < 500ms (excluding provider delays)
    - Webhook processing: near real-time but not user-facing

Important nuance:
    - Final payment confirmation is asynchronous, so latency is less critical there

#### Consistency
Question: Must all systems see the same data immediately?
Decision:
    - Strong consistency for internal payment state
    - Accept eventual consistency with provider state
Why:
    - You depend on Stripe → you don’t control final state timing

#### Scalability
Question: How much can load grow?
Decision:
    - Must handle spikes in payment requests (e.g. flash sales)
    - System should scale horizontally:
        - API layer
        - webhook processing

Key insight:
Webhooks can spike independently of API traffic

#### Durability
Question: Can we lose data?
Decision:
    - Never lose payment records
    - Never lose payment state transitions

Relaxation:
    - Debug logs can be lossy
    - Metrics can be sampled

#### Reliability (Critical for payments)
Question: What happens when things go wrong?
Decision:

    - All operations must be idempotent
    - System must tolerate:
        - duplicate requests
        - duplicate webhooks
        - partial failures
    - Retry only safe operations

#### Security
Question: What must be protected?
Decision:
    - No storage of raw card data (handled by Stripe)
    - Webhooks must be verified (signature validation)
    - API must enforce authentication + authorization
    - Sensitive data encrypted in transit (TLS)

#### Observability
Question: Can we debug issues in production?
Decision:
    - Every payment must be traceable end-to-end
    - Logs must include:
        - request
        - provider interaction
        - webhook events
    - Metrics:
        - success rate
        - failure rate
        - latency

#### Idempotency (Call this out explicitly — senior signal)
Question: What happens if the same request is sent twice (race condition)? 
Decision:
    - All payment creation requests must support idempotency keys
    - System must return the same result for duplicate requests

### In summary, so far, we’ve implicitly defined this system as:
##### A state machine managing payments under uncertainty


## Stage 3 - Estimate the Scale

#### Assumptions
Business Context
Mid-size SaaS / marketplace

#### Traffic Estimates
    - Payments/day: 10,000 (moderate product usage baseline)
    - Peak multiplier: ~5× (accounts for bursts like sales/events likr black fridays)
    - Read/write ratio: ~3:1 (users check status, dashboards, retries)

Webhooks (provider → system):
    - ~2–3 events per payment (typical provider lifecycle: created → processing → final state)
    - ⇒ ~25,000 events/day

#### Requests per Second
Writes (payment creation)
    - 10,000 / 86,400 ≈ ~0.1 req/sec avg (spread over a day)
    - Peak: ~1 req/sec

Reads (status checks)
    - ~30,000/day → ~0.3 req/sec avg (3× writes)
    - Peak: ~3–5 req/sec

Webhooks (provider → system)
    - 25,000 / 86,400 ≈ ~0.3 req/sec avg (event-driven, not user-driven)
    - Peak: ~3 req/sec

#### Total Peak Load
    - Writes: ~1 req/sec
    - Reads: ~5 req/sec
    - Webhooks: ~3 req/sec

👉 ~10 req/sec total

#### Storage Estimates
Payment records:
    - ~1 KB per record (IDs, status, metadata, timestamps)
    - ~11M over 3 years → ~11 GB (10,000/day * 365 * 3 years aprox equals 11M records)
    - => ~11 GB

Event logs (webhooks):
    - ~1 KB per event(store provider payload + status changes)
    - 25,000/day × 365 × 3 years ≈ ~27M events
    - ~27M events → ~27 GB

Total storage (3 years):
    - ~40 GB over 3 years (fits comfortably in a single DB instance)

#### Bandwidth Estimation
API traffic
    - ~10 req/sec × ~2 KB ≈ ~20 KB/sec (small JSON payloads)

Webhooks
    - ~3 req/sec × ~2 KB ≈ ~6 KB/sec

<50 KB/sec total (negligible)

#### Key Observations
    - System operates at low–moderate scale (~10 req/sec peak)
    - Storage is manageable on a single relational database
    - Webhooks are a core workload (async, duplicate-prone, not just API traffic)
    - System is correctness-heavy, not scale-heavy

Architectural Implication
Question: Given this scale, what is the simplest architecture that handles this load with room to grow?:
Answer:
    - The simplest system that works:
        - Modular monolith backend (one backend service)
        - Single relational database (e.g. PostgreSQL)
        - Optional async processing for webhooks (can evolve later)

Final Check
No need yet for:
    - Microservices
    - Distributed queues
    - Sharding or complex scaling strategies
These are anti-patterns to avoid. No need for over-engineering from get go when our numbers says different.

### The Most Important Insight from Stage 3
Our system is:
    - A low-scale, high-correctness system with external dependencies


## Stage 4 — Design the Data

### 1. Identify Core Entities
For a complete but simplest viable system, we'd need:

Core Entities
    - Payment — current state of a payment
    - PaymentEvent — immutable history of all changes
    - PaymentAttempt — each attempt to process a payment (handles retries cleanly)

### 2. Define Attributes

Payment:- Represents the overall payment (business-level object).
    - id (UUID)
    - user_id (from client system)
    - amount
    - currency
    - status (PENDING, PROCESSING, SUCCESS, FAILED)
    - provider (e.g. stripe)
    - idempotency_key (prevents duplicate payment creation)
    - created_at
    - updated_at

#### Note: Do not store provider IDs here - keep Payment provider-agnostic

PaymentAttempt
Represents a single attempt to execute a payment with a provider.
    - id
    - payment_id
    - provider
    - provider_payment_id (e.g. Stripe payment_intent_id)
    - status (INITIATED, REQUIRES_ACTION, SUCCESS, FAILED)
    - created_at
    - updated_at

    Why this exists:
        - Handles retries without corrupting the main Payment
        - Clean separation between business payment and provider interaction

PaymentEvent
Immutable log of everything that happens.
    - id
    - payment_id
    - payment_attempt_id (nullable but useful)
    - event_type (CREATED, ATTEMPTED, SUCCESS, FAILED, WEBHOOK_RECEIVED)
    - provider_event_id (for deduplication)
    - payload (raw or sanitized provider data)
    - created_at
This is your audit trail + debugging tool

### 3. Relationships
    - One Payment → many PaymentAttempts
    - One Payment → many PaymentEvents
    - One PaymentAttempt → many PaymentEvents

#### Core Mental Model
    - Payment = current snapshot (what clients read)
    - PaymentAttempt = execution layer (interaction with provider)
    - PaymentEvent = source of truth (what actually happened)