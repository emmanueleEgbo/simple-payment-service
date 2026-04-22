# System Specification - A Simple Payment Service (3rd-Party Gateway Integration)

## 1. Overview

### Problem Statement
Design a centralized payment orchestration layer that abstracts external payment gateways. It standardizes how payments are created, monitored, and reconciled, while guaranteeing:
    - no duplicate operations (idempotency)
    - high reliability despite external failures
    - a single, consistent source of truth for payment state