#!/bin/bash
# Sobe o Skills Dashboard (se ainda nao estiver no ar) e abre no navegador.
# Reusado pelo Skills-Dash.app (Dock) e pela skill /skills-dash.
DIR="/Users/igorcleto/skills_dashboard"
PY="/Library/Frameworks/Python.framework/Versions/3.8/bin/python3"
cd "$DIR" || exit 1
if ! lsof -ti:5556 >/dev/null 2>&1; then
  "$PY" "$DIR/app.py" >/tmp/skills_dash.log 2>&1 &
  for _ in $(seq 1 25); do
    lsof -ti:5556 >/dev/null 2>&1 && break
    sleep 0.3
  done
fi
open "http://localhost:5556"
