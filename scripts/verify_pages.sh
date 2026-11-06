#!/usr/bin/env bash
# Curl-verify GitHub Pages hero URLs (run after push; retries while build propagates).
set -euo pipefail
BASE="${PAGES_BASE:-https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit}"
PATHS=(
  "/"
  "/predictions-live.html"
  "/wire-beater.html"
  "/pce/index.html"
  "/data/wire-beater-status.json"
  "/data/latest-scores.json"
)
attempts="${VERIFY_PAGES_ATTEMPTS:-12}"
sleep_s="${VERIFY_PAGES_SLEEP:-15}"

check() {
  local url="$1"
  curl -fsS -o /dev/null -w "%{http_code}" "$url"
}

for path in "${PATHS[@]}"; do
  url="${BASE}${path}"
  ok=0
  for ((i = 1; i <= attempts; i++)); do
    code="$(check "$url" || echo "000")"
    echo "attempt $i $code $url"
    if [[ "$code" == "200" ]]; then
      ok=1
      break
    fi
    sleep "$sleep_s"
  done
  if [[ "$ok" != "1" ]]; then
    echo "FAIL: $url never returned 200" >&2
    exit 1
  fi
done
echo "All Pages URLs returned 200."
