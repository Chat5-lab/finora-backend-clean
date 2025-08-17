cd ~/workspace; sed -i '/^\.replit$/d' .gitignore 2>/dev/null || true; cat > .replit <<'EOF2'
language = "bash"
run = "bash run.sh"
[[ports]]
localPort = 8000
externalPort = 80
EOF2
cat > run.sh <<'EOF3'
#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv || python -m venv .venv
export PIP_CONFIG_FILE=/dev/null
export PYTHONNOUSERSITE=1
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
exec ./.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port "\${PORT:-8000}" --reload
EOF3
chmod +x run.sh
