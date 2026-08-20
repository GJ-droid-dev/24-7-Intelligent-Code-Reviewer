# Edge Cases and Failure Modes

This document enumerates edge cases, failure modes, and non-happy-path scenarios for the Multi-Agent AI Code Reviewer described in the project architecture, product context, and implementation plan.[file:1][file:2][file:3]

## Scope

The platform accepts authenticated code submissions, detects the language, invokes seven AI agents through an orchestrated pipeline, stores findings in Firestore, and exposes review history back to each user.[file:1][file:2][file:3] The edge cases below focus on submission handling, auth, orchestration, storage, scoring, historical learning, and frontend/reporting behavior.[file:1][file:2][file:3]

## Submission inputs

- Empty or near-empty submissions, such as whitespace-only code, a title with no code, or a diff containing only comments, should be rejected early with a clear validation error instead of entering the agent pipeline.[file:2][file:3]
- Extremely large submissions, including oversized pull requests or pasted files, can exceed request, model-context, or processing limits and need chunking, truncation strategy, or hard size caps.[file:1][file:3]
- Mixed-language submissions, such as a PR containing Python backend code, SQL migrations, and TypeScript tests, can cause incorrect single-language classification and reduce review quality.[file:1][file:2][file:3]
- Generated, minified, vendored, or lockfile content can dominate the diff and create noisy findings unless the system filters non-reviewable files before fan-out.[file:2][file:3]
- Binary uploads or unsupported file encodings can break ingestion and should be rejected or normalized before persistence.[file:3]
- Duplicate submissions from impatient users retrying the same request can create redundant reviews unless idempotency keys or content hashing are used.[file:1][file:3]
- Submissions that contain secrets, tokens, or customer data require safe storage, redaction in logs, and restricted display in reports.[file:1][file:2]

## Authentication and access

- Expired Firebase ID tokens, malformed bearer headers, or missing App Check attestations should fail closed and never create a review document.[file:1][file:3]
- A user must never retrieve another user's review by guessing a review ID, so ownership checks are required both in backend logic and Firestore rules.[file:1][file:2][file:3]
- Deleted, disabled, or partially provisioned user accounts can leave orphaned reviews unless the system defines lifecycle behavior for existing data.[file:1][file:3]
- Session expiration during long-running review generation can create UI confusion if the review finishes server-side but the client can no longer poll the result.[file:1][file:3]
- Rate-limit bypass through many valid accounts or scripted authenticated traffic remains possible even with authentication and should be addressed separately from login checks.[file:1]

## Language detection

- Very short snippets can be ambiguous across languages, causing heuristic language detection to misclassify the code and route it through the wrong conventions.[file:3]
- Polyglot files, templating syntaxes, notebooks, embedded SQL, or infrastructure files can require multi-label classification instead of a single detected language.[file:1][file:3]
- Unsupported or newly introduced languages should degrade gracefully with a partial review rather than a total pipeline failure.[file:2][file:3]
- A mismatch between user-declared language and detected language needs explicit handling so that either the user can override detection or the system can explain why it chose a different path.[file:3]

## Agent orchestration

- One specialist agent may fail, time out, or return malformed output while others succeed, so the orchestrator should support partial completion and mark degraded confidence instead of failing the whole review.[file:1][file:3]
- Parallel fan-out can produce duplicate or contradictory findings, which makes robust deduplication and conflict resolution in the Review Agent essential.[file:1][file:2][file:3]
- Agent outputs may not match the expected schema for finding category, severity, or suggested fix, requiring validation before persistence.[file:3]
- Prompt injection inside submitted code or comments can attempt to manipulate downstream agents, so code content must be treated as untrusted input and isolated from system instructions.[file:2]
- Long-running reviews can outlive HTTP request lifetimes on serverless infrastructure, which means asynchronous job handling is safer than blocking request-response execution.[file:1][file:3]
- If the Historical Learning Agent surfaces a rule that conflicts with current secure coding guidance, the Review Agent needs precedence logic rather than blindly applying history.[file:1][file:2][file:3]

## Historical learning

- The seed CSV schema is simple (`id, type, description`), so malformed rows, duplicate IDs, missing types, or unexpected delimiters can corrupt ingestion unless validated on startup.[file:1][file:3]
- Historical rules may be stale, overly generic, or no longer aligned with the codebase, which can cause irrelevant findings and lower trust.[file:1][file:2]
- Similarity matching may overfit on keywords and claim a past-issue match where the current code is materially different.[file:2][file:3]
- If the rules collection is empty because startup ingestion failed, the system should continue with other agents and mark historical learning as unavailable.[file:1][file:3]
- Concurrent startup instances on Cloud Run can race while upserting the same rules, so ingestion should be idempotent.[file:1][file:3]

## Persistence and consistency

- A review document may be created with `status=processing` but never updated if the pipeline crashes after persistence, leaving permanently stuck reviews unless retries or dead-letter handling exist.[file:1][file:3]
- Findings can be partially written if the final report update is non-atomic, producing inconsistent score and finding counts in the UI.[file:1][file:3]
- Re-running a review for the same submission may overwrite earlier findings or create divergent history unless versioning rules are defined.[file:1][file:3]
- Firestore index gaps can break list queries or filtered history views only after deployment to production-scale data.[file:3]
- Timestamp ordering issues across regions or retries can display history out of sequence unless the system uses a consistent server-generated clock.[file:1][file:3]

## Scoring and report quality

- The architecture defines weighted dimensions and a 1 to 10 score, but missing agent outputs can make the overall score unstable unless weights are renormalized under degraded execution.[file:1]
- Duplicate findings from multiple agents can artificially depress scores if each one is counted separately.[file:1][file:2]
- Severe but low-frequency issues, especially authorization flaws, must dominate the score even when code quality and tests look strong.[file:1][file:2]
- The report can become hard to trust if the numeric score says `Good` while the findings still include blocking issues, so score-label consistency checks are needed.[file:1][file:2]
- Suggested fixes may be too generic or not grounded in the actual submitted code, which undermines explainability promised in the design principles.[file:1][file:2]

## Frontend and UX

- Users need clear states for `processing`, `complete`, and `error`; otherwise refreshes or navigation away from the page can make reviews appear lost.[file:1][file:3]
- History dashboards can mislead users if failed or partial reviews are plotted alongside completed reviews without status-aware filtering.[file:1][file:3]
- Polling too aggressively from the frontend can create unnecessary backend load during long-running reviews on Cloud Run.[file:1][file:3]
- Copying and rendering code snippets in the browser can expose sensitive data to screen recordings, browser extensions, or shared workstations unless redaction controls exist.[file:1]
- Markdown or HTML in findings should be sanitized to prevent stored cross-site scripting when reports are rendered.[file:1][file:3]

## Security abuse cases

- Attackers can submit adversarial code specifically crafted to exhaust tokens, increase latency, or trigger worst-case model behavior, so quotas and size controls are needed.[file:1][file:2][file:3]
- Source code comments can contain instructions like "ignore previous guidance" that target LLM-based agents, making prompt injection defenses a first-class requirement.[file:2]
- Sensitive code from one tenant must never be retrievable through logs, shared caches, analytics tooling, or accidental prompt carryover between requests.[file:1]
- Review reports themselves can leak exploitable details, for example by echoing secrets or showing raw stack traces, so output filtering matters as much as input filtering.[file:1][file:2]
- If a user uploads proprietary code under restrictive terms, retention and deletion behavior must be explicit to avoid compliance and trust issues.[file:1][file:3]

## Operations and deployment

- Cold starts are amplified because startup includes CSV ingestion, so repeated scale-to-zero events can increase latency or create ingestion failures during burst traffic.[file:1][file:3]
- Secret rotation for Firebase, GCP services, or agent credentials can break running deployments if startup validation is incomplete.[file:1][file:3]
- Cloud dependency outages in Firestore, Cloud Storage, Firebase Auth, or the agent runtime should produce graceful degradation and actionable errors rather than silent failures.[file:1][file:3]
- Observability gaps can make it hard to distinguish model failure, schema failure, auth failure, and persistence failure inside one review request.[file:1][file:3]
- Cost spikes can occur when parallel agents process very large diffs or repeated retries, so guardrails are required at both request and orchestration levels.[file:1][file:3]

## Test scenarios to prioritize

1. Empty, duplicate, huge, and mixed-language submissions.[file:2][file:3]
2. Invalid token, cross-user access, and expired-session retrieval attempts.[file:1][file:2][file:3]
3. Single-agent timeout, malformed agent output, and partial pipeline success.[file:1][file:3]
4. Broken CSV ingestion, stale rules, and empty historical rule store.[file:1][file:3]
5. Stuck `processing` reviews, non-atomic writes, and retry idempotency.[file:1][file:3]
6. Prompt injection in code comments, secret redaction, and unsafe report rendering.[file:1][file:2][file:3]

## Design implications

The current design is strong on decomposition, explainability, historical grounding, and per-user isolation, but it needs explicit decisions for degraded execution, idempotency, asynchronous processing, prompt-injection resistance, and lifecycle management for stored reviews.[file:1][file:2][file:3] A robust first production version should define validation limits, fallback paths, retry semantics, report consistency rules, and secure redaction behavior before optimization features like growth dashboards are treated as complete.[file:1][file:3]
