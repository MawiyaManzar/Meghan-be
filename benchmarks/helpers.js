/**
 * Shared helper functions for Meghan benchmark scripts.
 * Used by the setup() function in each k6 script.
 */
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, TEST_EMAIL, TEST_PASSWORD } from './config.js';

/**
 * Register the benchmark test user.
 * Ignores 400 (already exists) — safe to call every run.
 */
export function registerBenchmarkUser() {
  http.post(
    `${BASE_URL}/api/auth/register`,
    JSON.stringify({ email: TEST_EMAIL, password: TEST_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  // intentionally ignore response — 400 just means user already exists
}

/**
 * Login as the benchmark user and return the JWT access token.
 * Throws if login fails.
 */
export function loginBenchmarkUser() {
  const res = http.post(
    `${BASE_URL}/api/auth/login-json`,
    JSON.stringify({ email: TEST_EMAIL, password: TEST_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  const ok = check(res, {
    'setup: login 200': (r) => r.status === 200,
    'setup: token present': (r) => r.json('access_token') !== undefined,
  });

  if (!ok) {
    throw new Error(`[setup] Login failed: HTTP ${res.status} — ${res.body}`);
  }

  return res.json('access_token');
}

/**
 * Create a benchmark conversation and return its ID.
 * Throws if creation fails.
 */
export function createBenchmarkConversation(token) {
  const res = http.post(
    `${BASE_URL}/api/chat/conversations`,
    JSON.stringify({ tier: 'Green', mood: 'Grounded', source: 'Career/Academics' }),
    { headers: authHeaders(token) }
  );

  const ok = check(res, {
    'setup: conversation 201': (r) => r.status === 201,
    'setup: conversation id present': (r) => r.json('id') !== undefined,
  });

  if (!ok) {
    throw new Error(`[setup] Conversation creation failed: HTTP ${res.status} — ${res.body}`);
  }

  return res.json('id');
}

/**
 * Full setup: register → login → create conversation.
 * Returns { token, conversationId } for use in default().
 */
export function setupBenchmark() {
  registerBenchmarkUser();
  const token = loginBenchmarkUser();
  const conversationId = createBenchmarkConversation(token);
  console.log(`[setup] Ready — conversationId=${conversationId}`);
  return { token, conversationId };
}

/**
 * Build standard JSON + auth headers from a bearer token.
 */
export function authHeaders(token) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

/**
 * Build auth-only headers (no Content-Type) for GET requests.
 */
export function authGetHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
  };
}
