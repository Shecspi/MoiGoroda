#!/usr/bin/env bash
set -euo pipefail

readonly SUDO_PASSWORD="password"

echo "$SUDO_PASSWORD" | sudo -S systemctl daemon-reload
echo "$SUDO_PASSWORD" | sudo -S systemctl restart gunicorn