/**
 * Benchmark: POST /api/chat/conversations/{id}/messages
 * KPI target (Section 5): P95 < 3500 ms, error rate < 1%
 *
 * This endpoint calls Bedrock AI — latency includes real LLM inference time.
 * Recommended: run smoke profile first to verify setup before normal/peak.
 *
 * Run:
 *   k6 run benchmarks/chat_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=smoke k6 run benchmarks/chat_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=peak  k6 run benchmarks/chat_load.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, KPI, ACTIVE_STAGES } from './config.js';
import { setupBenchmark, authHeaders } from './helpers.js';

export const options = {
  stages: ACTIVE_STAGES,
  thresholds: {
    // KPI: P95 < 3500 ms
    'http_req_duration{name:chat_message}': [`p(95)<${KPI.chat.p95_ms}`],
    // KPI: error rate < 1%
    'http_req_failed{name:chat_message}': [`rate<${KPI.errorRate}`],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

// Rotate through a small set of realistic test messages
const TEST_MESSAGES = [
  'I have been feeling overwhelmed with my studies lately.',
  'I am struggling to find balance between work and personal life.',
  'I had a difficult conversation with my roommate today.',
  'I feel like I am not making enough progress on my goals.',
  'I am anxious about an upcoming presentation at university.',
];

export function setup() {
  // Register user, login, create a conversation
  return setupBenchmark();
}

export default function (data) {
  const { token, conversationId } = data;

  // Pick a message based on VU iteration to vary traffic
  const msgIndex = (__ITER % TEST_MESSAGES.length);
  const payload = JSON.stringify({
    role:    'user',
    content: TEST_MESSAGES[msgIndex],
  });

  const res = http.post(
    `${BASE_URL}/api/chat/conversations/${conversationId}/messages`,
    payload,
    {
      headers: authHeaders(token),
      tags:    { name: 'chat_message' },
      timeout: '15s',  // Bedrock can be slow; give generous timeout
    }
  );

  check(res, {
    'POST .../messages → 200 or 201':  (r) => r.status === 200 || r.status === 201,
    'POST .../messages → has content': (r) => {
      try { return r.json('content') !== undefined; } catch { return false; }
    },
    'POST .../messages → p95 <3500ms': (r) => r.timings.duration < 3500,
  });

  sleep(2); // pacing: avoid hammering Bedrock; adjust for load profile
}
