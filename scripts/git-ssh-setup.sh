#!/usr/bin/env bash
set -e
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat > ~/.ssh/config <<CFG
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/replit
  IdentitiesOnly yes
CFG
chmod 600 ~/.ssh/config
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null || true
chmod 644 ~/.ssh/known_hosts
eval "$(ssh-agent -s)"
ssh-add -D >/dev/null 2>&1 || true
ssh-add ~/.ssh/replit
ssh -T git@github.com || true
