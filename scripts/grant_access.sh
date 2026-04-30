#!/usr/bin/env bash
# Grant read access to .env for all users listed in .env.access.
#
# Usage: bash scripts/grant_access.sh

set -euo pipefail

REPO_DIR="/vol/projects/CIIM/agentic_central"
ENV_FILE="${REPO_DIR}/.env"
ACCESS_FILE="${REPO_DIR}/.env.access"

if [[ ! -f "${ACCESS_FILE}" ]]; then
    echo "Error: ${ACCESS_FILE} not found."
    exit 1
fi

echo "Applying ACL entries from ${ACCESS_FILE} to ${ENV_FILE}..."

while IFS= read -r line; do
    # Strip inline comments and whitespace
    username="$(echo "${line}" | sed 's/#.*//' | tr -d '[:space:]')"
    [[ -z "${username}" ]] && continue

    setfacl -m "u:${username}:r" "${ENV_FILE}"
    echo "  granted: ${username}"
done < "${ACCESS_FILE}"

echo ""
echo "People with access to .env:"
while IFS= read -r entry; do
    username="$(echo "${entry}" | cut -d: -f2)"
    perms="$(echo "${entry}" | cut -d: -f3)"
    [[ -z "${username}" ]] && continue   # skip owner line (user::rw-)
    fullname="$(getent passwd "${username}" 2>/dev/null | cut -d: -f5 | sed 's/,.*//' || true)"
    [[ -z "${fullname}" ]] && fullname="?"
    printf "  %-12s %-30s %s\n" "${username}" "${fullname}" "${perms}"
done < <(getfacl "${ENV_FILE}" 2>/dev/null | grep "^user:")
