# Software Engineering Lab 1: Requirements Engineering & UML Use-Case Modelling

**Course**: SE Lab 1 — PES University (Dept. of CSE)  
**Problem Statement ID**: #43  
**Domain**: Developer Tools & IT Operations  
**Topic**: Feature Flag & Dynamic Config Manager  

---

## Deliverables Summary

| Deliverable File | Format | Description |
|---|---|---|
| [`Requirements_Table.pdf`](Requirements_Table.pdf) | PDF (`.pdf`) | Requirements Table featuring 5 FRs (FR-001 to FR-005) and 2 NFRs (NFR-001 & NFR-002) with ID, Type, Description, Priority, Acceptance Criteria, Rationale & Comments. |
| [`Use_Case_Diagram.png`](Use_Case_Diagram.png) | Image (`.png`) | Vector UML Use-Case Diagram depicting all 3 actors, 5 primary use cases, boundary box, `«include»`, and `«extend»` stereotypes. |
| [`Use_Case_Flow_Specification.pdf`](Use_Case_Flow_Specification.pdf) | PDF (`.pdf`) | 1-page Use-Case Flow Specification document for core use case `UC-01: Evaluate Feature Flag & Dynamic Config`. |
| [`43_SE_Lab1_SE_Problem_Statements (1).pdf`](43_SE_Lab1_SE_Problem_Statements%20%281%29.pdf) | PDF (`.pdf`) | Original Lab 1 Problem Statement #43 document. |

---

## 1. System Requirements Table

### Functional Requirements (FR)
- **FR-001 [High]**: *User Cohort Flag Evaluation* — Evaluate user targeting rules (User ID hash, Beta cohort) and return accurate boolean feature flag states. *(Given Sample)*
- **FR-002 [High]**: *Percentage-Based Rollout Configuration* — Allow Release Managers to configure percentage-based rollout rules for specified application environments.
- **FR-003 [High]**: *Environment-Specific Config Overrides* — Allow Software Engineers to define environment overrides (Development, Staging, Production).
- **FR-004 [Medium]**: *Real-time SDK Synchronization* — Push real-time flag update notifications to connected Client SDKs via SSE or WebSockets.
- **FR-005 [Medium]**: *Audit Logging & Version Rollback* — Maintain immutable audit trail of config changes and support zero-downtime rollback to prior versions.

### Non-Functional Requirements (NFR)
- **NFR-001 [High, Performance & Security]**: *Low Latency Flag Evaluation* — Flag evaluation API must execute in under 15 ms (p99) to minimize overhead in client critical paths. *(Given Sample)*
- **NFR-002 [High, Availability & Fault Tolerance]**: *99.99% Uptime & SDK Local Cache Fallback* — SDK falls back to cached local rules during network partition events without throwing unhandled exceptions.

---

## 2. UML Use-Case Diagram Overview

![UML Use-Case Diagram](Use_Case_Diagram.png)

### Actors:
1. **Software Engineer** (Primary Actor)
2. **Release Manager** (Primary Actor)
3. **Client SDK / Application** (Secondary System Actor)

### Use Cases:
- **UC-01**: Evaluate Feature Flag & Dynamic Config
- **UC-02**: Configure Rollout Rules & User Cohorts
- **UC-03**: Manage Environment Overrides
- **UC-04**: Synchronize Real-time SDK Flags
- **UC-05**: Rollback Configuration Version

### Stereotype Relationships:
- `UC-01` includes `Validate API Key & Auth Context` (`«include»`)
- `Fallback to Local SDK Cache` extends `UC-01` (`«extend»`) on network failure
- `Record Immutable Audit Log` extends `UC-02` (`«extend»`)

---

## 3. Use-Case Flow Specification (UC-01)

- **Main Success Scenario**:
  1. Client SDK sends evaluation request (`flag_key`, `user_id`, `attributes`).
  2. System validates API key and environment permissions.
  3. System retrieves active feature flag targeting rules.
  4. System evaluates environment overrides.
  5. System evaluates user attribute targeting rules.
  6. System hashes `user_id` using consistent hashing algorithm for percentage rollout bucket.
  7. System determines effective boolean flag state (`true`/`false`).
  8. System caches evaluated state in edge Redis memory store.
  9. System returns HTTP 200 OK with evaluated flag payload.
  10. Client SDK receives response and host app executes feature branch.

- **Alternate Flow (2a: Network Timeout / Cache Fallback)**:
  2a1. Client SDK detects network socket timeout (>50ms).  
  2a2. SDK catches exception without interrupting host execution.  
  2a3. SDK retrieves last valid flag state from local disk/memory cache.  
  2a4. If cache empty, SDK uses developer hardcoded fallback value.  
  2a5. SDK logs offline warning telemetry and schedules background retry.  
  2a6. Use case completes with fallback state.
