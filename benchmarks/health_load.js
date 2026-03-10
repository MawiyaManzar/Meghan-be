/**
 * Benchmark: GET /health
 * KPI target (Section 5): P95 < 150 ms, error rate < 1%
 *
 * Run:
 *   k6 run benchmarks/health_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=peak k6 run benchmarks/health_load.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, KPI, ACTIVE_STAGES } from './config.js';

export const options = {
  stages: ACTIVE_STAGES,
  thresholds: {
    // KPI: P95 < 150 ms
    'http_req_duration{name:health}': [`p(95)<${KPI.health.p95_ms}`],
    // KPI: error rate < 1%
    'http_req_failed{name:health}': [`rate<${KPI.errorRate}`],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

export default function () {
  const res = http.get(`${BASE_URL}/health`, {
    tags: { name: 'health' },
  });

  check(res, {
    'GET /health → 200':        (r) => r.status === 200,
    'GET /health → status=healthy': (r) => r.json('status') === 'healthy',
    'GET /health → p95 < 150ms': (r) => r.timings.duration < 150,
  });

  sleep(0.5); // pacing: ~2 req/s per VU
}
