# System Specification - A Simple Payment Service (3rd-Party Gateway Integration)

## 1. Overview

### Problem Statement
Design a simplified payment service that acts as an abstraction layer over 3rd-party payment providers (e.g., Stripe). The system allows applications to initiate, track, and reconcile payments without directly interacting with payment gateways.

The service must ensure reliability, idempotency, and consistent payment state tracking across external providers