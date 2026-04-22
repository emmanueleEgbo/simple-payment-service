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


### 2. What problem does it actually solve?
#### Surface Problem
    - "Process payments using Stripe (or similar providers)"

#### Real Problem (deeper)
    - "Provide a reliable, consistent, and provider-agnostic way for systems to handle payments without tightly coupling to external payment APIs."

#### Pain Points You Are Solving
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
