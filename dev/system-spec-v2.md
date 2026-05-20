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
    - "Provide a reliable, consistent, and provider-agnostic way for systems to handle payments without tight coupling to external payment APIs."

#### Pain Points being Solved
    - Every team integrating directly with Stripe duplicates logic
    - Handling webhooks, retries, failures is complex
    - Provider APIs can change or behave inconsistently
    - Hard to switch providers later (vendor lock-in)
    - No unified tracking of payment state across systems

#### The Payment Service System Provides
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
Fraud detection systems
Dispute/chargeback handling
Multi-provider smart routing (can come later)
Subscription billing logic

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
    - Must verify webhook signatures

#### Operational Constraints
    - System must be debuggable:
        - "What happened to this payment?" must always be answerable

### So, what are we building?
    - We are building a backend payment service that sits between client apps and payment providers like Stripe and the likes, and provides a consistent API for creating and tracking payments.
    It ensures reliability through idempotency, webhook handling, and internal state management.
    The goal is to decouple application teams from payment provider complexity while maintaining accurate and auditable payment flows.


## Stage 2 - Define Requirements

### 1. Functional Requirements - What the system does
#### Core Payment Flow

#### Client System -> Payment Service System -> Payment Provider (e.g. Stripe)

    - A Client System (e.g. checkout service, ecommerce platform, subscription service) can create a payment request through the Payment Service.
    - The Payment Service initiates payment processing through a third-party payment provider such as Stripe.
    - The Payment Service persists and tracks payment state internally throughout the payment lifecycle.

#### Payment Lifecycle
    - The system receives asynchronous updates from the provider via webhooks
    - The system validates, deduplicates, and processes incoming privider events
    - The system updates the persisted payment status based on provider event outcomes
    - The system maintains the latest payment status as the canonical source of truth
    - Client apps can retrieve the current payment status at any time.

#### Reliability & Safety
    - The system guarantees idempotent payment creation to prevent duplicate charges.
    - The system safely handles concurrent and repeated requests.
    - The system safely processes duplicate webhook deliveries from providers.
    - The system records all payment-related state transitions and provider interactions for auditing and reconciliation purposes.
    - The system ensures atomic and race-condition-safe payment processing.

#### Observability & Debugging
    - Client systems and internal operators can trace the full lifecycle of a payment.
    - The system stores provider responses and event payloads for debugging and reconciliation.
    - The system maintains immutable event history for auditability and operational analysis.

#### Extensibility (Optional / Future Enhancements)
  - The system can retry transient provider failures where retrying is safe.
  - The system supports integration with multiple payment providers through an extensible  provider adapter architecture.
  - The system can support asynchronous background processing for webhooks, retries, and reconciliation workflows.


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
For a complete but simplest viable system, the following entities would be needed:

Core Entities
    - Payment - A canonical internal representation of a payment transaction, including lifecycle state, provider references, processing metadata, and reconciliation details. It is the core business object.
    - PaymentEvent — immutable history of all changes
    - PaymentAttempt — each attempt to process a payment (handles retries cleanly)

### 2. Define the Attributes of each entity

1. Payment:- Represents the overall payment (business-level object).
    - id (UUID) - Internal unique identifier for the payment.
    - user_id / customer_reference - Who the payment belongs to.
    - amount - Payment amount in minor currency units for exact arithmetic and avoid floating-point issues
    - currency - ISO currency code.
    - status - Current business-visible payment state. (PENDING, PROCESSING, SUCCESS, FAILED, REQUIRES_ACTION, CANCELLED)
    - provider (e.g. stripe)
    - reference - the business object this payment is related to, for customer support, searching, invoices/orders
    - description - Human-readable description. E.G: "Premium subscription payment"
    - created_at
    - updated_at


#### Note: Do not store provider IDs here - keep Payment provider-agnostic

2. PaymentAttempt
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

Very important for real-world systems because:
  - payments can fail/retry
  - providers are async
  - network issues happen

3. PaymentEvent
Immutable audit/event history (a log of everything that happens).

Represents:
"What happened over time?"

Stores:
  - status transitions
  - webhook events
  - provider responses
  - retry events
  - failures/successes

    - id
    - payment_id
    - payment_attempt_id (nullable but useful)
    - event_type (CREATED, ATTEMPTED, SUCCESS, FAILED, WEBHOOK_RECEIVED)
    - provider_event_id (for deduplication)
    - payload (raw or sanitized provider data)
    - created_at
This is the audit trail + debugging tool

4. IdempotencyRecord
Handles request deduplication and retry safely.

Represents:
  Has this request already been processed safely?

Stores:
  - idempotency key
  - request hash
  - cached response
  - expiration window

This entity exists purely for:
  - reliability
  - concurrency safety
  - duplicate prevention

NOT business payment state.

### Core Mental Model:
Payment: Current business truth
PaymentAttempt: Execution boundary with provider
PaymentEvent: Historical source of truth
IdempotencyRecord: Request-level protection

### 3. Define the Relationships between entities
    - One Payment → has many PaymentAttempts / many PaymentEvents
    - One PaymentAttempt → has many PaymentEvents
    - One IdempotencyRecord -> one payment

### Problems solved by the core entities:
Current payment state   -> Payment
Retry handling          -> PaymentAttempt
Audit/debugging         -> PaymentEvent
Duplicate prevention    -> IdempotencyRecord

### Think about access patterns
Design the schema around how it's used:

#### Query 1 — Idempotent create / retry
    - SELECT * FROM payments WHERE idempotency_key = ?;
Index: idempotency_key (unique)

#### Query 2 — Get payment by ID
    - SELECT * FROM payments WHERE id = ?;
Primary key

#### Query 3 — Get latest attempt for a payment
    - SELECT * FROM payment_attempts 
    WHERE payment_id = ? 
    ORDER BY created_at DESC 
    LIMIT 1;

Index: (payment_id, created_at)

#### Query 4 — Update status from webhook
    - UPDATE payment_attempts SET status = ? WHERE provider_payment_id = ?;

Index: provider_payment_id

#### Query 5 — Deduplicate webhook events
    - SELECT * FROM payment_events WHERE provider_event_id = ?;

Index: provider_event_id (unique)

#### Query 6 — Payment history (debugging)
    - SELECT * FROM payment_events 
    WHERE payment_id = ? 
    ORDER BY created_at;

Index: (payment_id, created_at)

#### 5. Index Strategy
    - payments.id → primary key
    - payments.idempotency_key → unique index
    - payment_attempts.provider_payment_id → unique index
    - payment_attempts.payment_id, created_at → composite index
    - payment_events.provider_event_id → unique index
    - payment_events.payment_id, created_at → composite index

#### Principle:
##### Index based on access patterns, not assumptions

#### 6. Data That Changes vs Doesn’t
Stable (write once)
    - amount
    - currency
    - provider

Mutable (state machine)
    - payment.status
    - payment_attempt.status
    - updated_at

Append-only (never update)
    - payment_events

#### 7. Key Design Insight
    - Treat Payment as a derived snapshot
    - Treat PaymentEvent as the source of truth
    - Treat PaymentAttempt as the execution boundary

#### 8. What This Enables
    - Idempotent payment creation
    - Safe retry handling
    - Webhook deduplication
    - Full audit trail
    - Clear debugging (“what happened and when?”)
    - Clean separation of concerns

#### Why this is the simplest complete design
This avoids:

    - Overloading Payment with provider logic
    - Losing retry information
    - Mixing state and history

While still supporting:
    - Real-world async flows
    - Multiple attempts
    - Provider integration


## Stage 5 - Design the System (Top-Down)

### Level 1 - Simplest Possible System

Start with the minimal architecture:
[Client] -> [Backend API] -> [Database]
                  ↓
                [Payment Provider]

### Level 2: Add the components you know you need
Now name the technologies based on your requirements from Stage 2 and Stage 3:

[Client Application]
        │
        ▼ HTTP
[API Service]
        │
        ├──> [PostgreSQL]   (source of truth)
        │
        └──> [Provider Adapter] -> :contentReference[oaicite:1]{index=1} API

Why this works
    - PostgreSQL → ACID guarantees for payment correctness
    - Adapter layer → decouples from provider (extensibility)
    - Single service → sufficient for current scale

### Level 3 — Handle Async Work (Critical for Payments)
### Payment Flow (Synchronous + Async)
    1. Client → POST /payments
    2. API:
        - create Payment (PENDING)
        - call :contentReference[oaicite:2]{index=2}
        - store provider_payment_id
        - return response

### Webhook Flow (Async, source of truth)
:contentReference[oaicite:3]{index=3} → Webhook → [Webhook Handler]
                               │
                               ├──> validate signature
                               ├──> deduplicate event
                               └──> update Payment + insert PaymentEvent

[Webhook Handler] → [Background Worker] → [PostgreSQL]
Why:
    - Prevent blocking on webhook processing
    - Handle retries safely
    - Smooth out spikes

##### Note:- : async work must be reliable + idempotent

### Level 4 - Failure Scenarios
1. Provider (Stripe) fails:-
    - API call fails / times out
        - → Mark payment as FAILED or retry safely

External dependency = unreliable by default

2. Webhook duplication:-
    - Same event sent multiple times

#### Note: → Use provider_event_id for deduplication

3. Webhook arrives late or out of order

    - → Always treat webhook as source of truth
    - → Update state based on latest valid transition

4. API server crashes mid-request
    - Payment created but response not returned

→ Idempotency key ensures safe retry

5. Database goes down
    - Cannot read/write payments
→ Hence System unavailable

    - For v1: acceptable
    - For v2: add replica / failover

6. Background worker fails (if used)
    - Webhooks not processed immediately
→ Use retry mechanism / queue

#### Important: events must not be lost

### Key Trade-Offs
Sync vs Async
    - Payment creation → sync
    - Final state → async (webhooks)

### Simplicity vs Reliability
    - Keep system simple (monolith)
    - Add reliability where needed:
        - idempotency
        - event logging
        - webhook handling

### Final Architecture (v1):-

[Client]
   │
   ▼
[API Service]
   │
   ├──> [PostgreSQL]
   │
   ├──> [Provider Adapter] → :contentReference[oaicite:5]{index=5}
   │
   └──> [Webhook Handler]
              │
              └──→ [PostgreSQL]

Final Check

Does this handle our requirements and scale?
Yes:
    - Handles ~10 req/sec easily
    - Ensures correctness (ACID + idempotency)
    - Handles async provider behavior
    Keeps system simple

## Stage 6 - Identify the Risks
### 1. Technical Risks
### Duplicate Payments (Idempotency)
Problem:
Retries can create multiple charges

Decision:
Mitigate with idempotency keys enforced at API + DB level

### Webhook Reliability
Problem:
Webhooks can be duplicated, delayed, or out of order

Decision:

Mitigate with:
    - event deduplication (provider_event_id)
    - state machine for valid transitions

### External Provider Failure
Problem:
Stripe may fail or timeout

Decision:
    Mitigate + Accept
    - retries + timeouts
    - cannot fully control external dependency

### 2. Operational Risks
### Missed Webhooks / Incorrect State

Problem:
    - System state diverges from provider

Decision:
    - Mitigate with reconciliation jobs + event logs

### Traffic Spikes

Problem:
    - Sudden increase in payment volume

Decision:
    - Mitigate with horizontal scaling (API layer)

#### 3. Business Risk
### Vendor Lock-In

Problem:
    - Tight coupling to Stripe

Decision:
    - Mitigate via provider adapter layer

### Core Insight
The primary risk is incorrect payment state, not scale or latency.

### Focus areas:

Idempotency
Webhook handling
State consistency

Everything else is secondary at this stage.

## Stage 7 - Plan the Build (Iterative)
### Build Strategy

Build end-to-end slices, not layers

Goal:
    - Working system as early as possible
    - Validate assumptions quickly
    - Reduce rework

### Slice 1 - Core Happy Path 
Goal:
Create a payment and store it

Scope:
    - POST /payments
    - Save Payment in DB (PENDING)
    - Call Stripe (or mock)
    - Store provider_payment_id
    - Return response

After this:
We have a working payment flow (even if incomplete)

### Slice 2 — Payment Status Retrieval
Goal:

Be able to read payment state

Scope:
    - GET /payments/{id}
    - Fetch from DB
    - Return current status
Now:
System is observable and testable

### Slice 3 — Webhook Handling (Critical Path)
Goal:

Handle async provider updates

Scope:
    - Webhook endpoint (POST /webhooks/stripe)
    - Validate signature (basic)
    - Store PaymentEvent
    - Update Payment status
Now:
Full payment lifecycle works end-to-end

### Slice 4 — Idempotency
Goal:

Prevent duplicate payments

Scope:
    - Add idempotency_key
    - Enforce uniqueness in DB
    - Return existing payment on retry
Now:
Safe for real-world usage

### Slice 5 — Error Handling
Goal:
Handle failures gracefully

Scope:
    - Provider API failures
    - Invalid inputs
    - Missing payments
    - Basic retry logic (safe cases only)

Now:
System is robust, not just functional

### Slice 6 — Event Logging & Debugging
Goal:
Make system observable

Scope:
    - Store all PaymentEvents
    - Log provider responses
    - Add simple tracing (request → webhook)

Now:
We can debug real issues

### Slice 7 — (Optional) Async Processing
Goal:
Improve reliability under load

Scope:
    - Queue webhook processing
    - Background worker
    - Retry failed events

Only if needed (based on scale)

### Correct Build Order (Why this works)
    1. Happy path → prove system works
    2. Read path → visibility
    3. Async flow (webhooks) → real-world behavior
    4. Idempotency → correctness
    5. Error handling → robustness
    6. Observability → maintainability
    7. Performance → only if needed

### Key Insight
You are building a payment lifecycle, not just endpoints

Each slice adds:
    - correctness
    - reliability
    - confidence

### What NOT to do
    1. Build all DB models first
    2. Build full provider abstraction upfront
    3. Add queues before you need them
    4. Over-design for scale

### End Result

After Slice 3–4, you already have:
    1. Payment creation
    2. Provider interaction
    3. Webhook handling
    4. State updates
    5. Idempotency

That’s a real, working payment system