/**
 * Benchmark: POST /api/auth/login-json
 * KPI target (Section 5): P95 < 700 ms, error rate < 1%
 *
 * Run:
 *   k6 run benchmarks/auth_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=peak k6 run benchmarks/auth_load.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, TEST_EMAIL, TEST_PASSWORD, KPI, ACTIVE_STAGES } from './config.js';
import { registerBenchmarkUser } from './helpers.js';

export const options = {
  stages: ACTIVE_STAGES,
  thresholds: {
    // KPI: P95 < 700 ms
    'http_req_duration{name:auth}': [`p(95)<${KPI.auth.p95_ms}`],
    // KPI: error rate < 1%
    'http_req_failed{name:auth}': [`rate<${KPI.errorRate}`],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

// setup() runs once before all VUs start; return value is passed to default()
export function setup() {
  // Ensure benchmark user exists
  registerBenchmarkUser();
  console.log(`[setup] Benchmark user ready: ${TEST_EMAIL}`);
}

export default function () {
  const payload = JSON.stringify({
    email:    TEST_EMAIL,
    password: TEST_PASSWORD,
  });

  const res = http.post(`${BASE_URL}/api/auth/login-json`, payload, {
    headers: { 'Content-Type': 'application/json' },
    tags:    { name: 'auth' },
  });

  check(res, {
    'POST /api/auth/login-json → 200':     (r) => r.status === 200,
    'POST /api/auth/login-json → token':   (r) => r.json('access_token') !== undefined,
    'POST /api/auth/login-json → p95 <700ms': (r) => r.timings.duration < 700,
  });

  sleep(1);
}
