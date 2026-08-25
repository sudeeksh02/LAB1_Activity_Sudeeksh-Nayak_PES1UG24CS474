# Software Engineering Lab 1: Requirements Engineering & UML Use-Case Modelling

**Course**: Software Engineering Lab — PES University (Dept. of CSE)  
**Student Name**: Sudeeksh Nayak  
**SRN**: PES1UG24CS474  
**Problem Statement ID**: #43  
**Domain**: Developer Tools & IT Operations  
**Topic**: Feature Flag & Dynamic Config Manager  

---

## Deliverables Summary

| Deliverable File | Format | Description |
|---|---|---|
| [`Requirements_Table.pdf`](Requirements_Table.pdf) | PDF (`.pdf`) | Requirements Table featuring 5 FRs (FR-001 to FR-005) and 2 NFRs (NFR-001 & NFR-002) with ID, Type, Description, Priority, Acceptance Criteria, Rationale & Comments. |
| [`Use_Case_Diagram.png`](Use_Case_Diagram.png) | Image (`.png`) | Vector UML Use-Case Diagram depicting all 3 actors, 5 primary use cases, boundary box, `«include»`, and `«extend»` stereotypes. |
| [`Use_Case_Diagram.pdf`](Use_Case_Diagram.pdf) | PDF (`.pdf`) | High-resolution PDF export of the vector UML Use-Case Diagram. |
| [`Use_Case_Flow_Specification.pdf`](Use_Case_Flow_Specification.pdf) | PDF (`.pdf`) | 1-page Use-Case Flow Specification document for core use case `UC-01: Evaluate Feature Flag & Dynamic Config`. |
| [`Alternate_Flow_Activity_Diagram.png`](Alternate_Flow_Activity_Diagram.png) | Image (`.png`) | UML Activity Diagram illustrating the step-by-step logic of the Cache Fallback alternate flow. |
| [`Alternate_Flow_Activity_Diagram.pdf`](Alternate_Flow_Activity_Diagram.pdf) | PDF (`.pdf`) | PDF vector export of the UML Activity Diagram. |
| [`Exception_Flow_Specification.pdf`](Exception_Flow_Specification.pdf) | PDF (`.pdf`) | PDF version of the Exception Use-Case Flow Specification document detailing HTTP 401, 403, and 500 exceptions. |
| [`Exception_Flow_Specification.docx`](Exception_Flow_Specification.docx) | Word (`.docx`) | Word document version of the Exception Use-Case Flow Specification. |
| [`43_SE_Lab1_SE_Problem_Statements (1).pdf`](43_SE_Lab1_SE_Problem_Statements%20%281%29.pdf) | PDF (`.pdf`) | Original Lab 1 Problem Statement #43 document provided by instructor. |

---

## 1. System Requirements Table

### Functional Requirements (FR)
- **FR-001 [High]**: *User Cohort Flag Evaluation* — The system shall evaluate user targeting rules (e.g., User ID hash, Beta cohort) and return accurate boolean feature flag states. *(Given Sample)*
- **FR-002 [High]**: *Percentage-Based Rollout Configuration* — The system shall allow Release Managers to configure percentage-based rollout rules for specified application environments.
- **FR-003 [High]**: *Environment-Specific Config Overrides* — The system shall allow Software Engineers to define environment-specific configuration overrides (e.g., Development, Staging, Production).
- **FR-004 [Medium]**: *Real-time SDK Synchronization* — The system shall push real-time flag update notifications to connected Client SDKs via Server-Sent Events (SSE) or WebSockets.
- **FR-005 [Medium]**: *Audit Logging & Version Rollback* — The system shall log all configuration changes and enable Release Managers to rollback flag state to any previous version.

### Non-Functional Requirements (NFR)
- **NFR-001 [High, Performance & Security]**: *Low Latency Flag Evaluation* — The feature flag evaluation API must execute in under 15 ms (p99) to minimize overhead when integrated into client critical paths. *(Given Sample)*
- **NFR-002 [High, Availability & Fault Tolerance]**: *99.99% Uptime & SDK Local Cache Fallback* — The system shall maintain 99.99% service availability and fallback to local SDK cached rules during network partition events without throwing unhandled exceptions.

---

## 2. UML Use-Case Diagram Overview

![UML Use-Case Diagram](Use_Case_Diagram.png)

### Actors:
1. **Software Engineer** (Primary Actor) — Manages configuration overrides, monitors SDK integration.
2. **Release Manager** (Primary Actor) — Configures progressive rollouts, cohorts, and performs rollbacks.
3. **Client SDK / Application** (Secondary System Actor) — Requests flag evaluation in real-time and receives updates.

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

### Use Case: Evaluate Feature Flag & Dynamic Config
- **Primary Actor**: Client SDK / Application (also Software Engineer)
- **Preconditions**:
  1. Client SDK is initialized with a valid API key.
  2. Flag targeting rules are active in system database.
- **Postconditions**:
  1. System evaluates & returns boolean/JSON flag payload.
  2. Telemetry event is recorded.

- **Main Success Scenario**:
  1. Client SDK sends an evaluation request payload specifying `flag_key`, `user_id`, and `user_attributes` over HTTP/gRPC.
  2. System validates client request header, verifying API key authenticity and environment permissions.
  3. System retrieves active feature flag schema and rollout rules for the target environment.
  4. System evaluates environment-specific overrides (e.g., Development vs. Production).
  5. System evaluates user attribute targeting rules (e.g., country code, beta tester status).
  6. System hashes `user_id` using consistent hashing (MurmurHash3) to derive rollout bucket (0–100%).
  7. System compares user bucket percentage against configured rollout threshold to determine flag state.
  8. System caches evaluated flag state in edge memory (Redis) for rapid sub-millisecond future lookups.
  9. System returns HTTP 200 OK containing boolean state, variation key, and evaluation metadata.
  10. Client SDK receives response, updates internal state, and host app executes target feature branch.

- **Alternate Flow (2a: Network Timeout / Fallback to Local Cache)**:
  2a1. Client SDK detects network socket timeout (>50ms) or central API service returns HTTP 5xx error.  
  2a2. Client SDK catches the timeout exception without interrupting host application execution thread.  
  2a3. Client SDK retrieves the most recent valid flag state from its persistent local disk/memory cache.  
  2a4. If local cache is empty, SDK defaults to system hardcoded fallback flag value defined by developer.  
  2a5. SDK logs offline warning telemetry event and schedules background sync retry.  
  2a6. Use case completes successfully with fallback state.

---

## 4. Alternate Flow UML Activity Diagram

![UML Activity Diagram](Alternate_Flow_Activity_Diagram.png)

The activity diagram models the detailed control flow and functional activities triggered by Alternate Flow **2a (Network Timeout / Fallback to Local Cache)**:
- Exception handling boundaries for Client SDK.
- Sequential cache query execution.
- Diamond-decision branch checking if local cache is empty.
- Fallback value assignment vs. cached configuration loading.
- System merging activities to log telemetry and schedule background retry threads.

---

## 5. Exception Flow Specifications

Detailed specs for when preconditions fail or system errors prevent successful evaluations:

### Exception Flow 1b (HTTP 401): Invalid or Expired API Key
- **1b1.** Client SDK sends evaluation request with an expired or invalid API key.
- **1b2.** System fails validation check of client API key in the auth database.
- **1b3.** System logs an authentication failure security event with metadata.
- **1b4.** System returns HTTP 401 Unauthorized with error payload.
- **1b5.** Client SDK catches 401 error, throws a fatal initialization exception to the host application, and the use case terminates.

### Exception Flow 1c (HTTP 403): Environment Access Denied
- **1c1.** Client SDK sends evaluation request targeting a specific restricted environment (e.g., Production).
- **1c2.** System determines that the API key scope is limited to Development or Staging only.
- **1c3.** System logs environment access authorization violation alert.
- **1c4.** System returns HTTP 403 Forbidden with access restriction error payload.
- **1c5.** Client SDK catches 403 response, logs permissions failure telemetry, falls back to the hardcoded developer default, and terminates.

### Exception Flow 1d (HTTP 500 & Empty Cache): Database Outage & Empty Cache
- **1d1.** Client SDK sends evaluation request payload.
- **1d2.** System database queries fail (database service offline / internal timeouts).
- **1d3.** Redis backup memory cache queries fail, returning HTTP 500 Internal Server Error to the SDK.
- **1d4.** Client SDK detects HTTP 500 and queries its local disk/memory rules cache.
- **1d5.** Client SDK determines that the local rules cache is empty (first-time application boot).
- **1d6.** SDK applies the hardcoded developer fallback value, logs a critical system failure warning to local diagnostics, schedules background sync retry task, and terminates.
