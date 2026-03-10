/**
 * Benchmark: GET /api/chat/conversations/{id}/messages
 * KPI target (Section 5): P95 < 1000 ms (read path; conservative), error rate < 1%
 *
 * Run:
 *   k6 run benchmarks/history_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=peak k6 run benchmarks/history_load.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, KPI, ACTIVE_STAGES } from './config.js';
import { setupBenchmark, authGetHeaders } from './helpers.js';

export const options = {
  stages: ACTIVE_STAGES,
  thresholds: {
    'http_req_duration{name:chat_history}': [`p(95)<${KPI.history.p95_ms}`],
    'http_req_failed{name:chat_history}':   [`rate<${KPI.errorRate}`],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

export function setup() {
  return setupBenchmark();
}

export default function (data) {
  const { token, conversationId } = data;

  const res = http.get(
    `${BASE_URL}/api/chat/conversations/${conversationId}/messages`,
    {
      headers: authGetHeaders(token),
      tags:    { name: 'chat_history' },
    }
  );

  check(res, {
    'GET .../messages → 200':          (r) => r.status === 200,
    'GET .../messages → has messages': (r) => {
      try { return Array.isArray(r.json('messages')); } catch { return false; }
    },
    'GET .../messages → p95 <1000ms':  (r) => r.timings.duration < 1000,
  });

  sleep(0.5);
}
