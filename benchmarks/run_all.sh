#!/usr/bin/env bash
# =============================================================================
# Meghan Backend — Full Benchmark Suite Runner
# =============================================================================
# Usage:
#   ./benchmarks/run_all.sh
#   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=normal ./benchmarks/run_all.sh
#   BASE_URL=http://your-ec2:8000 LOAD_PROFILE=peak   ./benchmarks/run_all.sh
#
# Prerequisites:
#   - k6 installed: https://k6.io/docs/get-started/installation/
#   - Python 3 (for test audio generation)
#   - Backend running and reachable at BASE_URL
# =============================================================================

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_URL="${BASE_URL:-http://localhost:8000}"
LOAD_PROFILE="${LOAD_PROFILE:-normal}"
RESULTS_DIR="benchmarks/results/$(date +%Y%m%d_%H%M%S)"
SCRIPTS_DIR="benchmarks"

export BASE_URL
export LOAD_PROFILE

echo "============================================================"
echo "  Meghan Backend Benchmark Suite"
echo "  Date:         $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Base URL:     $BASE_URL"
echo "  Load profile: $LOAD_PROFILE"
echo "  Results dir:  $RESULTS_DIR"
echo "============================================================"
echo ""

# ─── Dependency checks ────────────────────────────────────────────────────────
if ! command -v k6 &>/dev/null; then
  echo "ERROR: k6 is not installed."
  echo "Install it from: https://k6.io/docs/get-started/installation/"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is not found. Needed to generate test audio."
  exit 1
fi

# ─── Prepare results directory ────────────────────────────────────────────────
mkdir -p "$RESULTS_DIR"
echo "Results will be saved to: $RESULTS_DIR"
echo ""

# ─── Generate test audio file for voice tests ─────────────────────────────────
echo ">>> Step 1/2 — Generating test audio file..."
python3 "$SCRIPTS_DIR/generate_test_audio.py"
echo ""

# ─── Health check before running suite ───────────────────────────────────────
echo ">>> Step 2/2 — Verifying backend is reachable at $BASE_URL/health ..."
if curl -sf "$BASE_URL/health" >/dev/null; then
  echo "    Backend is up."
else
  echo "ERROR: Cannot reach $BASE_URL/health — make sure the app is running."
  exit 1
fi
echo ""

# ─── Helper: run one k6 script ────────────────────────────────────────────────
run_benchmark() {
  local script="$1"
  local label="$2"
  local output_json="$RESULTS_DIR/${label}.json"
  local output_txt="$RESULTS_DIR/${label}.txt"

  echo "------------------------------------------------------------"
  echo "  Running: $label  ($script)"
  echo "------------------------------------------------------------"

  # Run k6 — save full JSON summary + human-readable summary
  k6 run \
    --out "json=$output_json" \
    --summary-export "$RESULTS_DIR/${label}_summary.json" \
    "$script" 2>&1 | tee "$output_txt"

  echo ""
  echo "  Saved: $output_json"
  echo "  Saved: $output_txt"
  echo ""
}

# ─── Run each benchmark ───────────────────────────────────────────────────────

run_benchmark "$SCRIPTS_DIR/health_load.js"   "01_health"
run_benchmark "$SCRIPTS_DIR/auth_load.js"     "02_auth"
run_benchmark "$SCRIPTS_DIR/chat_load.js"     "03_chat_messages"
run_benchmark "$SCRIPTS_DIR/history_load.js"  "04_chat_history"
run_benchmark "$SCRIPTS_DIR/insights_load.js" "05_insights_weekly"

echo "------------------------------------------------------------"
echo "  Voice test (requires real audio for full STT round-trip)"
echo "  Skipping by default — run manually when audio is ready:"
echo "    k6 run benchmarks/voice_load.js"
echo "------------------------------------------------------------"
echo ""

# ─── Summary ──────────────────────────────────────────────────────────────────
echo "============================================================"
echo "  All benchmarks complete."
echo "  Results saved in: $RESULTS_DIR/"
echo ""
echo "  To fill in the report table (Section 6), look for these"
echo "  values in each *_summary.json file:"
echo "    http_req_duration → avg, p(95), p(99)"
echo "    http_reqs         → count / test duration = RPS"
echo "    http_req_failed   → rate (multiply by 100 for %)"
echo "============================================================"
