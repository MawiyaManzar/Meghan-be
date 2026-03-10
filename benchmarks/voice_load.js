/**
 * Benchmark: POST /api/chat/conversations/{id}/voice
 * KPI target (Section 5): P95 < 7000 ms, error rate < 1%
 *
 * ⚠️  IMPORTANT before running:
 *   1. Generate the test audio file first:
 *        python benchmarks/generate_test_audio.py
 *   2. For a real end-to-end measurement (STT → AI reply), replace
 *      benchmarks/test_audio.wav with a real short speech clip (< 10 MB).
 *      A silent WAV will return HTTP 400 because AssemblyAI returns empty transcript.
 *   3. Voice tests consume AssemblyAI credits and Bedrock tokens — use
 *      LOAD_PROFILE=smoke for initial validation.
 *
 * Run:
 *   python benchmarks/generate_test_audio.py
 *   k6 run benchmarks/voice_load.js
 *   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=smoke k6 run benchmarks/voice_load.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, KPI, ACTIVE_STAGES } from './config.js';
import { setupBenchmark, authGetHeaders } from './helpers.js';

// k6 reads the file once at init time (not per VU call)
// The path is relative to the working directory where k6 is run from
const AUDIO_DATA = open('./benchmarks/test_audio.wav', 'b');

export const options = {
  // Voice tests are expensive — use a lighter profile by default
  stages: ACTIVE_STAGES,
  thresholds: {
    // KPI: P95 < 7000 ms  (upload + STT + AI pipeline)
    'http_req_duration{name:voice}': [`p(95)<${KPI.voice.p95_ms}`],
    // KPI: error rate < 1%
    'http_req_failed{name:voice}': [`rate<${KPI.errorRate}`],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

export function setup() {
  return setupBenchmark();
}

export default function (data) {
  const { token, conversationId } = data;

  // Build multipart form-data request with the audio file
  const formData = {
    audio: http.file(AUDIO_DATA, 'test_audio.wav', 'audio/wav'),
  };

  const res = http.post(
    `${BASE_URL}/api/chat/conversations/${conversationId}/voice`,
    formData,
    {
      headers: { Authorization: `Bearer ${token}` },  // NO Content-Type: multipart is set by k6
      tags:    { name: 'voice' },
      timeout: '30s',  // STT + Bedrock pipeline; generous timeout
    }
  );

  check(res, {
    'POST .../voice → 201':                (r) => r.status === 201,
    'POST .../voice → has user_message':   (r) => {
      try { return r.json('user_message') !== undefined; } catch { return false; }
    },
    'POST .../voice → has ai_response':    (r) => {
      try { return r.json('ai_response') !== undefined; } catch { return false; }
    },
    'POST .../voice → p95 <7000ms':        (r) => r.timings.duration < 7000,
  });

  // Longer sleep — voice calls are expensive; avoid thundering herd
  sleep(5);
}
