/**
 * Benchmark: GET /api/insights/weekly
 * KPI target (Section 5): P95 < 2000 ms (read/analytics path), error rate < 1%
 *
 * Run:
 *   k6 run benchmarks/insights_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=peak k6 run benchmarks/insights_load.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, KPI, ACTIVE_STAGES } from './config.js';
import { setupBenchmark, authGetHeaders } from './helpers.js';

export const options = {
  stages: ACTIVE_STAGES,
  thresholds: {
    'http_req_duration{name:insights_weekly}': [`p(95)<${KPI.insights.p95_ms}`],
    'http_req_failed{name:insights_weekly}':   [`rate<${KPI.errorRate}`],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

export function setup() {
  return setupBenchmark();
}

export default function (data) {
  const { token } = data;

  const res = http.get(
    `${BASE_URL}/api/insights/weekly`,
    {
      headers: authGetHeaders(token),
      tags:    { name: 'insights_weekly' },
    }
  );

  check(res, {
    'GET /api/insights/weekly → 200':       (r) => r.status === 200,
    'GET /api/insights/weekly → has data':  (r) => {
      try { return r.json('week_starting') !== undefined; } catch { return false; }
    },
    'GET /api/insights/weekly → p95 <2000ms': (r) => r.timings.duration < 2000,
  });

  sleep(1);
}
