# 24/7 Intelligent Code Reviewer

A **Multi-Agent AI Code Reviewer** that automatically reviews code submissions using seven specialized AI agents — covering code quality, security, performance, testing, and historical team patterns.

> **Key Principle:** The system advises — it never auto-approves or auto-merges code. Specialized AI agents analyze different aspects of a code change, collaborate through an orchestrator, and provide developers with structured, scored, and explainable review feedback.

---

## 🏗️ Architecture

```
Developer ──▶ Next.js Frontend ──▶ FastAPI Backend ──▶ Agent Pipeline (ADK v1.0)
                                        │                    │
                                   Firestore            Gemini 3.6 Flash
                                   (persistence)        (7 agents)
```

### Agent Pipeline

| # | Agent | Responsibility |
|---|---|---|
| 1 | **Orchestrator** | Plans, delegates, combines findings, computes score |
| 2 | **Code Quality** | Structure, readability, maintainability, conventions |
| 3 | **Security** | Vulnerabilities, access-control, data exposure |
| 4 | **Performance** | Scalability, DB efficiency, runtime bottlenecks |
| 5 | **Test & Edge-Case** | Test coverage, missing scenarios, assertion quality |
| 6 | **Historical Learning** | Team-specific patterns from past reviews & CSV rules |
| 7 | **Review** | Validate, deduplicate, prioritize, finalize report |

### Quality Score (1–10)

| Score | Label | Recommendation |
|---|---|---|
| 9–10 | Excellent | Production-ready |
| 7–8 | Good | Safe to merge |
| 5–6 | Fair | Address issues first |
| 3–4 | Poor | Significant problems |
| 1–2 | Critical | Do not merge |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React, TypeScript |
| Backend | FastAPI (Python 3.12+) |
| Authentication | Firebase Auth + App Check |
| Database | Firestore Enterprise |
| Object Storage | Cloud Storage |
| AI Agents | ADK v1.0, Gemini 3.6 Flash |
| Platform | Gemini Enterprise Agent Platform |
| Infrastructure | Google Cloud Run (serverless) |
| Security | VPC, IAM, Secret Manager |

---

## 📁 Project Structure

```
├── backend/                 # FastAPI backend service
│   ├── app/                 # Application code
│   ├── tests/               # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Next.js 16 frontend
│   ├── app/                 # App Router pages
│   ├── components/          # Reusable UI components
│   ├── lib/                 # Utilities & API client
│   ├── Dockerfile
│   └── package.json
├── infrastructure/          # GCP infrastructure config
│   ├── firestore/           # Security rules & indexes
│   ├── cloudbuild/          # CI/CD pipeline
│   └── seed/                # Seed data & CSV rules
├── docs/                    # Documentation
│   ├── architecture.md
│   ├── implementation-plan.md
│   └── context.md
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Google Cloud SDK (`gcloud`)
- Firebase CLI (`firebase-tools`)

### Local Development

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

---

## 📄 Documentation

- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Context & Problem Statement](docs/context.md)

---

## 📜 License

This project is part of an academic / portfolio demonstration of multi-agent AI systems.
