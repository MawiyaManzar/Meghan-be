/**
 * Shared benchmark configuration for Meghan Backend.
 * Override defaults via environment variables when running k6:
 *   BASE_URL=http://your-ec2-ip:8000 k6 run benchmarks/chat_load.js
 */

// Base URL of the running backend
export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Benchmark test user credentials
// This user will be auto-registered if it doesn't exist yet
export const TEST_EMAIL    = __ENV.TEST_EMAIL    || 'benchmark@meghan.test';
export const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'BenchTest99!';

// ─── KPI thresholds (matching Section 5 of the performance report) ────────────
export const KPI = {
  health:   { p95_ms: 150  },
  auth:     { p95_ms: 700  },
  chat:     { p95_ms: 3500 },
  voice:    { p95_ms: 7000 },
  history:  { p95_ms: 1000 },   // not explicitly in report; conservative
  insights: { p95_ms: 2000 },   // read endpoint; conservative
  errorRate: 0.01,              // < 1 %
};

// ─── Load stages (shared across all endpoint scripts) ─────────────────────────
// You can override per-script if needed.
export const STAGES = {
  smoke: [
    { duration: '30s', target: 1 },
    { duration: '30s', target: 0 },
  ],
  normal: [
    { duration: '30s', target: 10 },   // ramp up
    { duration: '3m',  target: 10 },   // sustain
    { duration: '30s', target: 0 },    // ramp down
  ],
  peak: [
    { duration: '30s', target: 25 },
    { duration: '1m',  target: 25 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 0 },
  ],
};

// Select which profile to run via LOAD_PROFILE env var (smoke | normal | peak)
export const ACTIVE_STAGES = STAGES[__ENV.LOAD_PROFILE || 'normal'];
