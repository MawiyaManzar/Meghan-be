# Project Meghan – Execution Plan with Dates (Planner, 2026-01-21)

This is a **date-committed plan** for a junior developer. Follow week by week. Each item has clear deliverables and simple acceptance criteria. Stack decisions mirror the tech-lead guidance.

## Stack Assumptions (locked for this plan)
- Frontend: **Next.js (React)**, Tailwind, TanStack Query for server state, Zustand/Redux Toolkit for light client state.
- Backend: **FastAPI (async)**, Pydantic v2, SQLAlchemy (async), BackgroundTasks now; Celery/RQ later if needed.
- Datastores: **Neon Postgres** = source of truth (auth, profiles, communities, hearts ledger, therapist roles). **MongoDB** = content/high-volume (chat logs, journals, micro-expressions, transcripts, community posts). Do not cross responsibilities.
- AI: **Phase 1 Gemini** for intent/emotion/chat/summarize; **Phase 2 OSS** (Mistral/Llama via vLLM/Ollama/Replicate) for tagging/goals/risk. No direct DB writes from LLMs.
- Safety: Every AI call passes sanitize → classify → intent → safety check → respond → log (no raw PII). Crisis module is isolated.

## Non-Negotiables
- Safety gate on all AI and community inputs; block risky content from public feeds.
- Ledger is append-only; never mutate balances.
- No PII or emotional content leaves the service without explicit consent/anon mode.
- Rate-limit and audit-log key endpoints (`/auth`, `/chat`, `/communities`, `/posts`, `/hearts`).

## Timeline (by calendar weeks)

### Week 0 – Foundations (Jan 21 – Jan 27, 2026)
- Repo, CI, env files, secrets loading.
- FastAPI app + health checks; DB connections to Postgres + Mongo.
- Auth endpoints alive; minimal Next.js shell with login/register (or guest token).
- Acceptance: Can register/login, hit a protected endpoint, and see both DB health checks green.

### Week 1 – Core MVP Part A (Jan 28 – Feb 03, 2026)
- Onboarding API: profile basics (life_stage, age_range), struggles tags, privacy choice.
- Auto community assignment service; store first emotional check-in.
- Frontend onboarding wizard (Welcome → Profile → Struggles → Privacy → First mood).
- Acceptance: New user completes onboarding, lands on Home; profile + struggles + privacy + first mood + community memberships persist.

### Week 2 – Core MVP Part B (Feb 04 – Feb 10, 2026)
- AI Chat Talk/Plan modes with intent prompt; store conversation + mode.
- Daily check-in endpoint + home dashboard v0 (today’s mood, hearts, weekly summary stub).
- Calm resources endpoint (static list) + session logging.
- Acceptance: User can start Talk vs Plan chat and see different behavior; Calm session logs and adds hearts; dashboard pulls backend data.

### Week 3 – Core MVP Part C (Feb 11 – Feb 17, 2026)
- Communities: list/join (with anonymity), feed read, create micro-expression, respond.
- Hearts ledger: earn hooks for chat, check-ins, calm, journal; `GET /hearts/balance`, `GET /hearts/catalog`, `POST /hearts/redeem` (basic).
- Journal/Reflect: prompts + create entry; hearts awarded.
- Acceptance: User posts in a community, others can respond; hearts increase on actions; redemption works for at least one item.

### Week 4 – Safety & Quality Part A (Feb 19 – Feb 25, 2026)
- Risk detection service (keywords + classifier) wired into chat/community/journal inputs.
- Safety middleware: block/flag risky content; Crisis event entity; soft alert + resources response.
- Moderation endpoints (list flagged items) and basic therapist/ops view (API first).
- Acceptance: High-risk phrase triggers crisis response, flags content, and appears in moderation/therapist list.

### Week 5 – Safety & Quality Part B (Feb 26 – Mar 03, 2026)
- Escalation flow: lock risky actions where needed; notify therapist list; acknowledge/unlock path.
- Insights v1: weekly aggregation endpoint (mood trends, triggers, hearts summary) + frontend chart.
- Acceptance: Therapist (or admin) can see crisis events and mark handled; Insights tab shows weekly data with at least one textual insight.

### Week 6 – AmiConnect (Optional) (Mar 04 – Mar 10, 2026)
- Link + sync endpoints; map skill progress → hearts; readiness gate.
- Frontend status + sync button; minimal error handling.
- Acceptance: User can link, sync skills, and see hearts from skill progress.

### Buffer / Hardening (Mar 11 – Mar 17, 2026)
- Bug fixes, perf, rate limiting, logging polish, UX smoothing.
- Stretch: swap in OSS LLM for tagging/risk behind a feature flag.

## Test & Ship Checklist (repeat per week)
- Unit tests for new services; integration tests for new endpoints.
- Manual happy-path through UI for the week’s deliverables.
- Smoke deploy to staging; run health + basic flows.
- Review safety gates and logging before shipping.
