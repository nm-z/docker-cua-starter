#!/usr/bin/env bash

# Exit on error
set -e
# Exit on undefined variable
set -u
# Exit if any command in a pipeline fails
set -o pipefail

# No Chrome or socat logic needed. Entrypoint is now a no-op.

exec "$@"
