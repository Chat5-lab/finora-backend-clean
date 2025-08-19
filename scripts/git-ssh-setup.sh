#!/usr/bin/env bash
set -euo pipefail

# Rebuild ~/.ssh from secret
mkdir -p ~/.ssh && chmod 700 ~/.ssh

if [ -z "${GITHUB_SSH_KEY:-}" ]; then
  echo "ERROR: GITHUB_SSH_KEY secret not set. Add it in Replit → Tools → Secrets." >&2
  exit 1
fi

printf "%s\n" "$GITHUB_SSH_KEY" > ~/.ssh/id_ed25519_finora
chmod 600 ~/.ssh/id_ed25519_finora

cat > ~/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_finora
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config

# Trust GitHub host key (avoid prompt)
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null || true
chmod 644 ~/.ssh/known_hosts

# Fresh agent; load key
eval "$(ssh-agent -s)"
ssh-add -D >/dev/null 2>&1 || true
ssh-add ~/.ssh/id_ed25519_finora >/dev/null
ssh-add -l
