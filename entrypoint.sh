#!/usr/bin/env bash

# Exit on error
set -e
# Exit on undefined variable
set -u
# Exit if any command in a pipeline fails
set -o pipefail

CHROME_PORT=${1:-9222}
INNER_PORT=${2:-9992}

# Proxy requests from CHROME_PORT to INNER_PORT
socat tcp-listen:${CHROME_PORT},reuseaddr,fork tcp:localhost:${INNER_PORT} &

# Launch Chrome
google-chrome \
  --allow-insecure-running-content \
  --disable-dev-shm-usage \
  --disable-gpu \
  --disable-popup-blocking \
  --disable-sync \
  --js-flags="--max-old-space-size=1024" \
  --memory-pressure-off \
  --no-default-browser-check \
  --no-first-run \
  --no-sandbox \
  --remote-allow-origins=* \
  --remote-debugging-address=0.0.0.0 \
  --remote-debugging-bind-to-all \
  --remote-debugging-port=${INNER_PORT} \
  --start-maximized \
  --window-position=0,0 \
  --window-size=1280,720
