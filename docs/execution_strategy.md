# Technical Execution Strategy

Our 24/7 Intelligent Code Reviewer runs entirely on Google Cloud.

Users sign up and log in through **Firebase Authentication** (with App Check to block abuse). They land on a **Next.js 16** frontend hosted on **Cloud Run**, where they can submit code and browse their review history.

Behind the scenes, a **FastAPI** backend — also on Cloud Run — takes each submission, saves it to **Firestore Enterprise** (which keeps every user's session history, scores, and past reviews), and kicks off the multi-agent review pipeline.

The agents are the heart of the system. We use the **Agent Development Kit (ADK) v1.0** on the **Gemini Enterprise Agent Platform** to run seven specialized agents — covering code quality, security, performance, testing, and historical patterns — all powered by **Gemini 3.6 Flash**. The Orchestrator fans out work in parallel, and a final Review agent consolidates everything into a single scored report (1–10).

For historical learning, we store CSV rule data in **Cloud Storage**. At startup, the backend parses the CSV (`id, type, description`), categorizes each rule by type (security, performance, formatting), and stores them in Firestore. During review, the Historical Learning agent queries matching rules by type and injects them into the specialist agents' prompts — so findings are grounded in the team's own patterns, not just generic advice.

Everything is serverless, auto-scales, and stays locked down with **IAM** and **VPC**.
