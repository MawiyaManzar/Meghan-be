# Prototype Performance Report / Benchmarking

Project: **Meghan Backend Prototype**  
Date: **Mar 5, 2026**  
Environment: **FastAPI backend with RDS (PostgreSQL), S3 media flow, Bedrock AI integration**

---

## 1) Purpose

This report measures how the prototype performs under realistic usage and identifies bottlenecks before production rollout.

Goals:
- Measure API response speed.
- Measure stability under concurrent users.
- Measure DB + S3 + Bedrock related latency impact.
- Define pass/fail criteria for MVP readiness.

---

## 2) Scope of Benchmarking

Endpoints and flows covered:

1. `GET /health` (base API readiness)
2. `POST /api/auth/login-json` (auth response speed)
3. `POST /api/chat/conversations/{id}/messages` (core AI chat flow)
4. `POST /api/chat/conversations/{id}/voice` (voice upload + STT + chat + S3 key persistence)
5. `GET /api/chat/conversations/{id}/messages` (history retrieval)
6. `GET /api/insights/weekly` (analytics/summary read path)

---

## 3) Test Environment

Hardware/Runtime (replace with exact values used):
- Server: EC2 (instance type: `________`)
- Region: `us-east-1`
- Python: `3.11+`
- App server: `uvicorn` (or gunicorn + uvicorn workers)
- Database: RDS PostgreSQL
- Storage: S3 private bucket + pre-signed URL flow
- AI: Bedrock model (`BEDROCK_MODEL_ID`)

Software setup:
- Same `.env` style as runtime.
- Same schema as current prototype.
- Warm-up requests run before capturing numbers.

---

## 4) Benchmark Methodology

Load profile used:
- **Single user smoke:** 1 virtual user, 20 requests.
- **Normal load:** 10 concurrent users, 2-5 minutes.
- **Peak load:** 25-50 concurrent users, short burst.

Metrics captured:
- Avg response time (ms)
- P50 / P95 / P99 latency
- Requests per second (RPS)
- Error rate (% non-2xx)
- Timeout count
- CPU and memory usage on app host

Notes:
- For chat endpoint, Bedrock latency is included.
- For voice endpoint, upload + STT + DB write + AI response path is included.

---

## 5) Target KPI Thresholds (MVP)

Minimum acceptable targets:
- `/health` P95 < **150 ms**
- Auth endpoint P95 < **700 ms**
- Chat message endpoint P95 < **3500 ms**
- Voice endpoint P95 < **7000 ms**
- Error rate < **1%**
- Availability during test > **99%**

These thresholds are practical for a prototype using managed AI services.

---

## 6) Benchmark Results Table

Fill with measured values after running tests.

| Endpoint / Flow | Users | Avg (ms) | P95 (ms) | P99 (ms) | RPS | Error % | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| `GET /health` | 10 | ___ | ___ | ___ | ___ | ___ | PASS/FAIL |
| `POST /api/auth/login-json` | 10 | ___ | ___ | ___ | ___ | ___ | PASS/FAIL |
| `POST /api/chat/.../messages` | 10 | ___ | ___ | ___ | ___ | ___ | PASS/FAIL |
| `POST /api/chat/.../voice` | 5 | ___ | ___ | ___ | ___ | ___ | PASS/FAIL |
| `GET /api/chat/.../messages` | 10 | ___ | ___ | ___ | ___ | ___ | PASS/FAIL |
| `GET /api/insights/weekly` | 10 | ___ | ___ | ___ | ___ | ___ | PASS/FAIL |

---

## 7) Resource Utilization Snapshot

Capture values during peak load:

| Resource | Average | Peak | Notes |
|---|---:|---:|---|
| CPU (%) | ___ | ___ | |
| Memory (%) | ___ | ___ | |
| DB connections in use | ___ | ___ | |
| Bedrock request failures | ___ | ___ | throttling/timeout? |
| S3 operation failures | ___ | ___ | |

---

## 8) Observed Bottlenecks (to complete after run)

Common expected bottlenecks:
- AI call latency (Bedrock inference time)
- DB connection pool saturation under bursts
- Voice path latency due to STT + AI serial pipeline
- Cold-start/warm-up effects if any serverless components are added

For each bottleneck, record:
1. Symptom
2. Evidence (metric/log)
3. Impact
4. Proposed fix

---

## 9) Optimization Recommendations

Priority 1 (high impact):
- Enable connection pooling tuning for SQLAlchemy/DB.
- Add short caching for repeated read endpoints (where safe).
- Use async non-blocking I/O across external calls.

Priority 2:
- Tune Bedrock prompt size to reduce token/latency overhead.
- Add request timeout + retries with jitter for external dependencies.
- Keep S3 object operations minimal in response path.

Priority 3:
- Add autoscaling policy once traffic baseline is known.
- Add periodic performance regression benchmark in CI/CD.

---

## 10) Reliability & Regression Readiness

Current engineering confidence signals:
- Core integration tests are passing for AWS integration flows.
- S3 voice flow tests are available and passing.
- Weekly insights Lambda tests are implemented and passing.
- Schema-check and health endpoints are validated.

Add latest run evidence before submission:
- `pytest` summary: `________`
- Load test report path: `________`
- CloudWatch dashboard snapshot: `________`

---

## 11) Final Assessment

Prototype status: **[Ready for pilot / Needs optimization before pilot]**

Decision rules:
- If all P95 latency targets pass and error rate < 1% -> Ready for pilot.
- If chat/voice endpoints miss targets but remain stable -> Pilot allowed with known risk.
- If error rate > 1% or frequent timeouts -> Fix blockers before pilot.

---

## 12) Reproducible Benchmark Execution (Simple)

Use one load tool consistently (`k6`, `Locust`, or `hey`).

Example with `k6` (recommended):

```bash
k6 run benchmarks/chat_load.js
```

Example run checklist:
1. Start app in production-like mode.
2. Run warm-up traffic for 2-3 minutes.
3. Execute normal load test.
4. Execute peak/burst test.
5. Export report and fill Section 6/7 tables.

---

## 13) Appendix: Benchmark Data Recording Format

Use this per test run:

```text
Run ID:
Date/Time:
Environment (EC2 size, DB tier):
Endpoint tested:
Concurrency:
Duration:
Avg latency:
P95 latency:
Error rate:
Notes:
```

This keeps performance tracking consistent across versions.
