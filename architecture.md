# Architecture — Multi-Agent AI Code Reviewer

> **Version:** 1.0  
> **Last Updated:** 2026-08-18  
> **Status:** Design

---

## 1. System Overview

The Multi-Agent AI Code Reviewer is a serverless, cloud-native platform that automatically reviews code submissions using seven specialized AI agents. Authenticated users submit code through a web frontend; the platform detects the programming language, fans the code out to specialist agents in parallel, consolidates findings into a scored report (1–10), and persists every review for historical learning.

### Design Principles

| Principle | Description |
|---|---|
| **Specialist Decomposition** | Each review concern (quality, security, performance, testing, history) is owned by a dedicated agent. |
| **Orchestrated Parallelism** | The Orchestrator fans out work to all specialists simultaneously, then merges results. |
| **Explainability** | Every finding is grounded in the submitted code and scored with a clear rationale. |
| **Historical Grounding** | Reviews are enriched with team-specific patterns from ingested CSV rule data. |
| **Human-in-the-Loop** | The system advises — it never auto-approves or auto-merges code. |

---

## 2. High-Level Architecture

```mermaid
flowchart LR
    subgraph Client
        A["Next.js 16 Frontend<br/>(Cloud Run)"]
    end

    subgraph Backend
        B["FastAPI Service<br/>(Cloud Run)"]
    end

    subgraph AgentPlatform["Gemini Enterprise Agent Platform"]
        C["ADK v1.0 Agent Runtime"]
    end

    subgraph Data
        D[("Firestore Enterprise")]
        E[("Cloud Storage<br/>CSV Rules")]
    end

    subgraph Auth
        F["Firebase Auth<br/>+ App Check"]
    end

    A -- "HTTPS / REST" --> B
    A -- "Auth Tokens" --> F
    F -- "Token Validation" --> B
    B -- "Agent Invocation" --> C
    B -- "Read / Write" --> D
    B -- "Load CSV at Startup" --> E
    C -- "Persist Results" --> D
```

---

## 3. Component Architecture

### 3.1 Presentation Layer — Next.js 16 Frontend

| Aspect | Detail |
|---|---|
| **Framework** | Next.js 16 (React, server components) |
| **Hosting** | Cloud Run (containerized) |
| **Auth** | Firebase Authentication SDK with App Check |
| **Responsibilities** | Code submission form, review result display, review history & growth tracking dashboard |

**Key Pages / Routes:**

| Route | Purpose |
|---|---|
| `/login`, `/register` | User authentication flows |
| `/submit` | Code submission (paste or file upload) |
| `/reviews/:id` | Single review report with score breakdown |
| `/history` | Chronological review history with quality-score trend |

---

### 3.2 API Layer — FastAPI Backend

| Aspect | Detail |
|---|---|
| **Framework** | FastAPI (Python) |
| **Hosting** | Cloud Run (serverless, auto-scaling) |
| **Auth** | Validates Firebase ID tokens on every request |
| **Responsibilities** | Request validation, language detection, agent pipeline orchestration, persistence, CSV rule ingestion |

**Core Endpoints:**

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/reviews` | Submit code for review |
| `GET` | `/api/v1/reviews/{id}` | Retrieve a single review report |
| `GET` | `/api/v1/reviews` | List authenticated user's review history |
| `GET` | `/api/v1/health` | Service health check |

**Startup Sequence:**

```mermaid
sequenceDiagram
    participant S as FastAPI Service
    participant GCS as Cloud Storage
    participant FS as Firestore

    S->>GCS: Fetch historical CSV (id, type, description)
    GCS-->>S: CSV payload
    S->>S: Parse & categorize rules by type<br/>(security, performance, formatting, …)
    S->>FS: Upsert categorized rules
    Note over S: Ready to accept requests
```

---

### 3.3 Agent Layer — ADK v1.0 on Gemini Enterprise Agent Platform

All agents run on the **Gemini Enterprise Agent Platform** using the **Agent Development Kit (ADK) v1.0** and are powered by **Gemini 3.6 Flash**.

#### Agent Inventory

```mermaid
flowchart TD
    subgraph Pipeline
        O["① Orchestrator Agent"]
        CQ["② Code Quality Agent"]
        SA["③ Security Agent"]
        PA["④ Performance Agent"]
        TE["⑤ Test & Edge-Case Agent"]
        HL["⑥ Historical Learning Agent"]
        RA["⑦ Review Agent"]
    end

    O -- "parallel fan-out" --> CQ
    O -- "parallel fan-out" --> SA
    O -- "parallel fan-out" --> PA
    O -- "parallel fan-out" --> TE
    O -- "parallel fan-out" --> HL

    CQ --> RA
    SA --> RA
    PA --> RA
    TE --> RA
    HL --> RA

    RA --> FR["Final Review Report<br/>(Score 1–10)"]
```

#### Agent Specifications

| # | Agent | Model | Input | Output |
|---|---|---|---|---|
| 1 | **Orchestrator** | Gemini 3.6 Flash | PR diff, metadata, detected language | Review plan; delegates to specialists; computes overall score |
| 2 | **Code Quality** | Gemini 3.6 Flash | Diff, coding guidelines, linter output | Readability, maintainability, refactoring findings |
| 3 | **Security** | Gemini 3.6 Flash | Diff, auth logic, API routes, env config | Vulnerabilities, access-control gaps, data-exposure risks |
| 4 | **Performance** | Gemini 3.6 Flash | DB queries, API code, data-volume assumptions | Scalability issues, N+1 queries, missing pagination |
| 5 | **Test & Edge-Case** | Gemini 3.6 Flash | Test files, API spec, diff | Missing test scenarios, assertion quality |
| 6 | **Historical Learning** | Gemini 3.6 Flash | Current diff + Firestore rules (by type) | Pattern matches from CSV rule base, past PR parallels |
| 7 | **Review** | Gemini 3.6 Flash | Combined specialist outputs | Deduplicated, prioritized, scored final report |

---

## 4. Data Architecture

### 4.1 Firestore Enterprise — Collections

```mermaid
erDiagram
    USERS ||--o{ REVIEWS : "submits"
    REVIEWS ||--|{ FINDINGS : "contains"
    RULES ||--o{ FINDINGS : "may match"

    USERS {
        string uid PK
        string email
        string displayName
        timestamp createdAt
    }

    REVIEWS {
        string id PK
        string userId FK
        string language
        text codeSnippet
        int overallScore
        map scoreBreakdown
        timestamp submittedAt
        string status
    }

    FINDINGS {
        string id PK
        string reviewId FK
        string agentSource
        string category
        string severity
        text description
        text suggestedFix
        string matchedRuleId
    }

    RULES {
        string id PK
        string type
        text description
    }
```

### 4.2 Cloud Storage — Historical CSV

| Bucket Path | Purpose |
|---|---|
| `gs://<project>/rules/historical_reviews.csv` | Source-of-truth CSV with schema `id, type, description` |

The CSV is loaded at service startup, parsed into typed rule objects, and upserted into the `RULES` Firestore collection. During a review, the Historical Learning Agent queries rules by `type` and injects matched rules into specialist agent prompts.

---

## 5. Request Lifecycle — End-to-End Flow

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant FE as Next.js Frontend
    participant Auth as Firebase Auth
    participant API as FastAPI Backend
    participant ADK as ADK Agent Runtime
    participant FS as Firestore

    Dev->>FE: Submit code
    FE->>Auth: Verify session / get ID token
    Auth-->>FE: ID token
    FE->>API: POST /api/v1/reviews<br/>(code + ID token)
    API->>Auth: Validate ID token
    Auth-->>API: UID + claims
    API->>API: Detect language
    API->>FS: Create REVIEW document (status: "processing")
    API->>ADK: Invoke Orchestrator Agent<br/>(code, language, user context)

    par Parallel Fan-Out
        ADK->>ADK: Code Quality Agent
        ADK->>ADK: Security Agent
        ADK->>ADK: Performance Agent
        ADK->>ADK: Test & Edge-Case Agent
        ADK->>ADK: Historical Learning Agent<br/>(queries Firestore rules)
    end

    ADK->>ADK: Review Agent<br/>(validate, dedupe, score)
    ADK-->>API: Final report + score
    API->>FS: Update REVIEW (findings, score, status: "complete")
    API-->>FE: 200 OK + review report
    FE-->>Dev: Display scored review
```

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

| Layer | Mechanism |
|---|---|
| **Identity** | Firebase Authentication (email/password; extensible to OAuth) |
| **Abuse Prevention** | Firebase App Check — blocks unauthenticated and bot traffic |
| **API Auth** | Every backend request validated against Firebase ID token |
| **Per-User Isolation** | Firestore security rules + backend checks: users access only their own data |

### 6.2 Network & Infrastructure

| Control | Implementation |
|---|---|
| **Transport** | HTTPS / TLS everywhere |
| **IAM** | Google Cloud IAM — least-privilege service accounts for Cloud Run, Firestore, Cloud Storage |
| **VPC** | Backend services deployed within a VPC for network isolation |
| **Secrets** | No secrets in code — managed via Google Secret Manager or environment variables |

### 6.3 Data Protection

- Submitted code is stored encrypted at rest in Firestore (Google-managed encryption).
- No raw customer data is logged — the Security Agent itself enforces PII-awareness in reviews.
- CSV rule data in Cloud Storage is access-controlled via IAM.

---

## 7. Scoring Model

The Orchestrator computes an **overall quality score (1–10)** by aggregating dimension scores from each specialist agent.

### Dimension Breakdown

| Dimension | Agent Source | Weight |
|---|---|---|
| Security | Security Agent | High |
| Performance | Performance Agent | Medium–High |
| Code Quality | Code Quality Agent | Medium |
| Test Coverage | Test & Edge-Case Agent | Medium |
| Historical Patterns | Historical Learning Agent | Low–Medium |

### Score Interpretation

| Score Range | Label | Recommendation |
|---|---|---|
| **9–10** | Excellent | Production-ready, no significant issues |
| **7–8** | Good | Minor suggestions, safe to merge |
| **5–6** | Fair | Notable issues to address before merging |
| **3–4** | Poor | Significant bugs, security, or design problems |
| **1–2** | Critical | Fundamental flaws, do not merge |

---

## 8. Infrastructure Topology

```mermaid
flowchart TB
    subgraph GCP["Google Cloud Platform"]
        subgraph VPC["VPC Network"]
            CR1["Cloud Run<br/>Next.js Frontend"]
            CR2["Cloud Run<br/>FastAPI Backend"]
            GEAP["Gemini Enterprise<br/>Agent Platform<br/>(ADK v1.0)"]
        end

        FS[("Firestore<br/>Enterprise")]
        GCS[("Cloud Storage<br/>CSV Rules")]
        FA["Firebase Auth<br/>+ App Check"]
        IAM["Cloud IAM"]
        SM["Secret Manager"]
    end

    Internet(("Internet")) --> FA
    Internet --> CR1
    CR1 --> CR2
    CR2 --> GEAP
    CR2 --> FS
    CR2 --> GCS
    IAM -.->|"least privilege"| CR1
    IAM -.->|"least privilege"| CR2
    SM -.->|"secrets"| CR2
```

### Deployment Characteristics

| Property | Detail |
|---|---|
| **Compute** | Fully serverless — Cloud Run auto-scales to zero |
| **Scaling** | Request-based autoscaling; agent calls parallelized |
| **Cold Start** | CSV rule ingestion occurs on container startup |
| **Observability** | Cloud Logging, Cloud Trace, Cloud Monitoring |
| **CI/CD** | Container images built and deployed via Cloud Build (recommended) |

---

## 9. Multi-Language Support

| Capability | Detail |
|---|---|
| **Detection** | The Orchestrator Agent auto-detects the programming language from the submitted code |
| **Language-Aware Analysis** | Specialist agents apply language-specific linting rules, idioms, and best practices |
| **Multi-Language Reports** | Findings reference the correct language conventions (e.g., Python PEP 8, JavaScript ESLint rules) |

---

## 10. Technology Summary

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React |
| Backend API | FastAPI (Python) |
| Authentication | Firebase Auth + App Check |
| Database | Firestore Enterprise |
| Object Storage | Cloud Storage |
| AI Agents | ADK v1.0, Gemini 3.6 Flash |
| Agent Platform | Gemini Enterprise Agent Platform |
| Infrastructure | Google Cloud Run (serverless) |
| Networking | VPC, IAM, HTTPS/TLS |
| Secrets | Google Secret Manager |
