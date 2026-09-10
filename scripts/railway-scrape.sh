#!/bin/sh
set -eu

: "${GITHUB_SSH_PRIVATE_KEY:?GITHUB_SSH_PRIVATE_KEY is required}"
: "${JCDECAUX_API_KEY:?JCDECAUX_API_KEY is required}"

job_root="$(mktemp -d)"
ssh_root="$(mktemp -d)"

cleanup() {
    rm -rf "$job_root" "$ssh_root"
}
trap cleanup EXIT HUP INT TERM

printf '%s\n' "$GITHUB_SSH_PRIVATE_KEY" > "$ssh_root/id_ed25519"
chmod 600 "$ssh_root/id_ed25519"
cp /app/deploy/github_known_hosts "$ssh_root/known_hosts"

export GIT_SSH_COMMAND="ssh -i $ssh_root/id_ed25519 -o IdentitiesOnly=yes -o UserKnownHostsFile=$ssh_root/known_hosts"

git clone \
    --branch main \
    --depth 1 \
    --single-branch \
    git@github.com:MaxHalford/bike-sharing-history.git \
    "$job_root/repo"

cd "$job_root/repo"
timeout --signal=TERM 10m python scrape/scrape_city_branches.py
