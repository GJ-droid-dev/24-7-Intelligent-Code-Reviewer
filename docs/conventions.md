# Engineering & Architecture Conventions

> **Project:** 24/7 Intelligent Code Reviewer (Multi-Agent AI Code Reviewer)  
> **Source Documents:** [`architecture.md`](./architecture.md), [`context.md`](./context.md), [`implementation-plan.md`](./implementation-plan.md)  
> **Target Audience:** Core Contributors, AI Agents, Reviewers  
> **Version:** 1.0  
> **Last Updated:** 2026-08-19  

---

## 1. System Design & Architectural Principles

### 1.1 Core Mission & Boundary
1. **Advisory Role Only:** The AI system provides structured, scored, and explainable recommendations. It **never** auto-approves, auto-rejects, auto-merges, or auto-deploys code.
2. **Multi-Agent Specialist Separation:** Every specialist agent has a strictly bounded scope:
   - **Code Quality Agent:** Structure, readability, naming, maintainability, separation of concerns, duplication, complexity.
   - **Security Agent:** Authentication, authorization, injection, secrets, sensitive data exposure, cryptography, input validation.
   - **Performance Agent:** Algorithmic complexity, database access, N+1 queries, pagination, caching, async blocking, memory/resource leaks.
   - **Test & Edge-Case Agent:** Positive/negative test coverage, boundary cases, auth tests, error-path tests, assertion quality, test flakiness.
   - **Historical Learning Agent:** Repository-specific past defect patterns, CSV rules matching, incident/convention alignment.
   - **Orchestrator Agent:** Pipeline coordination, context normalization, parallel execution management, failure handling.
   - **Review Agent:** Grounding validation, cross-agent deduplication, priority sorting, weighted score calculation, final report synthesis.
3. **Evidence-Based Grounding:** No agent may invent files, functions, database schemas, or production traffic. Every finding must point to concrete code evidence in the submitted diff or context.

---

## 2. Technology Stack & Directory Conventions

### 2.1 Technology Standards
| Tier | Technology | Version / Spec |
|---|---|---|
| **Frontend** | Next.js, React, TypeScript | Next.js 16 (App Router), React 19, TypeScript 5.x |
| **Styling** | Tailwind CSS / CSS Modules | Dark/Light Mode, Glassmorphism, Modern typography |
| **Backend API** | FastAPI, Python, Uvicorn | Python 3.12+, Pydantic v2, AsyncIO |
| **Database** | Google Cloud Firestore | Native/Enterprise Mode, strict Security Rules |
| **Storage** | Google Cloud Storage | Regional bucket (`*-historical-rules`) |
| **AI Runtime** | Google ADK / Gemini API | Gemini 3.6 Flash (`temperature: 0.1`) |
| **Authentication** | Firebase Authentication | Google OAuth + Email/Password + App Check |
| **Infrastructure** | Google Cloud Run, Cloud Build | Serverless containerized deployment |

### 2.2 Canonical Directory Structure
```
├── backend/                             # FastAPI Backend Application
│   ├── app/
│   │   ├── main.py                      # FastAPI entrypoint & lifecycle
│   │   ├── config.py                    # Environment & runtime settings
│   │   ├── dependencies.py              # Auth & DB dependency injection
│   │   ├── middleware/                  # Auth & security middleware
│   │   ├── routers/                     # HTTP route handlers (/reviews, /health)
│   │   ├── services/                    # Business logic (CSV, Language Detection, Reviews)
│   │   └── agents/                      # Multi-Agent Subsystem
│   │       ├── base.py                  # BaseAgent abstract class
│   │       ├── config.py                # Agent configuration loader
│   │       ├── orchestrator.py          # Orchestrator & parallel fan-out
│   │       ├── code_quality.py          # Code Quality Agent
│   │       ├── security.py              # Security Agent
│   │       ├── performance.py           # Performance Agent
│   │       ├── test_edge_case.py        # Test & Edge-Case Agent
│   │       ├── historical_learning.py   # Historical Learning Agent
│   │       ├── review.py                # Review Synthesis Agent
│   │       ├── pipeline.py              # Pipeline execution facade
│   │       ├── prompts/                 # Agent system prompts (*_system.prompt.md)
│   │       └── configs/                 # Agent YAML configuration files (*.yaml)
│   ├── tests/                           # Unit & integration test suite
│   ├── requirements.txt                 # Backend dependencies
│   └── Dockerfile                       # Backend container definition
├── frontend/                            # Next.js 16 Frontend Web Application
│   ├── app/                             # App Router (dashboard, reviews, rules)
│   ├── components/                      # UI components (Radar charts, Monaco editor, cards)
│   ├── lib/                             # Firebase client, API fetcher, types
│   ├── public/                          # Static assets
│   ├── package.json                     # Frontend dependencies
│   └── Dockerfile                       # Frontend container definition
├── infrastructure/                      # GCP & Firebase Infrastructure
│   ├── firestore/                       # firestore.rules & firestore.indexes.json
│   ├── storage/                         # storage.rules
│   ├── cloudbuild/                      # cloudbuild.yaml CI/CD pipeline
│   └── seed/                            # historical_reviews.csv & seed_firestore.py
└── docs/                                # Project Specifications & Architecture
    ├── architecture.md                  # System architecture
    ├── context.md                       # Product requirements & problem statement
    ├── implementation-plan.md           # 6-phase technical execution plan
    ├── execution_strategy.md            # Execution overview
    └── conventions.md                   # This conventions document
```

---

## 3. Code Quality & Style Standards

### 3.1 Python (Backend)
- **Formatting & Linting:** PEP 8 compliance, formatted with `black` and `ruff`.
- **Type Hinting:** Mandatory type annotations on all function signatures (`pydantic.BaseModel`, `Optional`, `List`, `Dict`, `Union`).
- **Asynchronous Execution:** All I/O operations (Firestore reads/writes, HTTP requests, Gemini calls) must be `async`/`await`. Avoid blocking standard library I/O in async request paths.
- **Error Handling:** Use custom HTTPException responses with standard error payloads (`{"detail": "..."}`). Never leak stack traces or raw database exceptions to clients.
- **Logging:** Structured logging using Python standard `logging` with appropriate levels (`INFO`, `WARNING`, `ERROR`). Redact sensitive secrets, API keys, and user credentials.

### 3.2 TypeScript / React (Frontend)
- **Strict Typing:** `strict: true` in `tsconfig.json`. Explicit interfaces/types for all API payloads and component props. Avoid `any`.
- **Component Architecture:** Functional components with React 19 hooks. Clean separation between UI presentation and data fetching.
- **State Management:** React hooks (`useState`, `useEffect`, `useCallback`) and custom hooks for Firebase Auth / Firestore real-time listeners.
- **Aesthetic Excellence:** High-contrast accessible color palette, glassmorphism accents, smooth micro-interactions, responsive grid layout for desktop and mobile.

---

## 4. Multi-Agent Pipeline Conventions

### 4.1 Agent Execution Lifecycle
1. **Parallel Fan-Out:** Specialist agents (`code_quality`, `security`, `performance`, `test_edge_case`, `historical_learning`) must execute concurrently via `asyncio.gather` with isolated timeout guards (default: 20–30 seconds).
2. **Graceful Degradation:** A single specialist failure or timeout must **not** abort the entire pipeline. The pipeline logs the failure in `agentStatuses` and passes surviving results to the Review Agent with a `partial` status flag.
3. **Structured JSON Contracts:** Every agent must output valid, schema-compliant JSON only — without markdown fences, preamble, or trailing commentary.

### 4.2 Quality Scoring & Safety Floors
Overall quality score is calculated on a scale of **1 to 10** using the standard weighted formula:

$$\text{Score} = 0.30 \cdot S_{\text{security}} + 0.20 \cdot S_{\text{performance}} + 0.20 \cdot S_{\text{quality}} + 0.20 \cdot S_{\text{testing}} + 0.10 \cdot S_{\text{historical}}$$

#### Safety Floor Rules:
- If a **Critical Security / Data Integrity** finding is confirmed: **Max Overall Score = 4**.
- If a **High Security** finding is confirmed: **Max Overall Score = 6**.
- If multiple **High** severity issues exist across dimensions: **Max Overall Score = 6**.

#### Score Labels & Recommendations:
| Score Range | Label | Recommendation | Condition |
|---|---|---|---|
| **9 – 10** | Excellent | `safe_to_merge` | No blocking issues, clean maintainable code |
| **7 – 8** | Good | `merge_with_non_blocking_changes` | Safe to merge; minor improvements suggested |
| **5 – 6** | Fair | `changes_required` | Needs remediation before merging |
| **3 – 4** | Poor | `changes_required` | Significant structural, security, or performance issues |
| **1 – 2** | Critical | `changes_required` | Fundamental vulnerabilities or severe defects |

---

## 5. Security & Data Protection Conventions

### 5.1 Untrusted Input & Prompt Injection Resistance
1. **User Code as Data:** User-submitted code, diffs, PR titles, and descriptions must be treated as **untrusted data**.
2. **Boundary Delimitation:** Prompts must clearly isolate user content using markdown sections or boundaries (`## Code or Unified Diff`).
3. **Instruction Precedence:** System prompt instructions always override instructions contained inside reviewed code (e.g., `"ignore security warnings"` in comments must be ignored).
4. **No Code Execution:** Submitted code is statically analyzed by LLMs. It is **never** executed, compiled, or evaluated in a live runtime.

### 5.2 Secrets & Credential Management
- **Never Commit Secrets:** Service account JSON keys (`*firebase-adminsdk*.json`), private keys, and `.env` files are strictly excluded via `.gitignore`.
- **GCP Secret Manager:** Sensitive credentials (e.g., `firebase-admin-sdk-key`) are retrieved via GCP Secret Manager in production or passed via environment variables.
- **Output Redaction:** Any detected passwords, tokens, or private keys in code snippets must be replaced with `[REDACTED]` in finding descriptions and output JSON.

### 5.3 Firestore Multi-Tenant Isolation
- All review and finding documents are scoped per user: `resource.data.userId == request.auth.uid`.
- Read/Write security rules are enforced at the Firestore database layer.

---

## 6. Git & Testing Conventions

### 6.1 Git Commit Messages
Use the Conventional Commits specification:
- `feat: ...` — New features or agent implementations.
- `fix: ...` — Bug fixes or edge-case handling.
- `test: ...` — Adding or updating test cases.
- `docs: ...` — Updating documentation, plans, or conventions.
- `refactor: ...` — Code restructuring without feature changes.
- `chore: ...` — Dependency updates, CI/CD, or repository maintenance.

### 6.2 Testing Standards
1. **Unit Tests:** Every service, router, utility, and agent must have corresponding unit tests in `backend/tests/`.
2. **Mocking External I/O:** Unit tests must mock external network calls, Firestore, and Gemini APIs (`unittest.mock.AsyncMock`).
3. **Smoke Tests:** Live integration tests (`backend/smoke_test.py`) verify end-to-end connectivity with Firestore and cloud services.
4. **Pre-Push Validation:** All tests must pass (`pytest backend/tests -v`) before committing and pushing to `main`.
