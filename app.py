"""
Skills Dashboard — localhost:5556
Visualiza as skills disponíveis em ~/.claude/commands/
"""

import os
import re
from pathlib import Path

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

COMMANDS_DIR = Path.home() / ".claude" / "commands"


def parse_skill(md_file: Path) -> dict:
    text = md_file.read_text(errors="replace")
    lines = text.splitlines()

    # Nome: primeira linha com # /nome — Título Amigável
    name = md_file.stem
    trigger = f"/{name}"
    title = ""
    for line in lines:
        m = re.match(r"^#\s+(/\S+)(?:\s+[—–-]+\s+(.+))?", line)
        if m:
            trigger = m.group(1)
            name = trigger.lstrip("/")
            title = (m.group(2) or "").strip()
            break

    # Descrição: primeira linha não-vazia após o heading h1
    description = ""
    past_heading = False
    for line in lines:
        if re.match(r"^#\s+", line):
            past_heading = True
            continue
        if past_heading and line.strip():
            description = line.strip()
            break

    # Seções: headings h2 como tags
    sections = [m.group(1).strip() for line in lines if (m := re.match(r"^##\s+(.+)", line))]

    # Detectar tecnologias usadas (keywords)
    tech_keywords = {
        "Google Calendar": "calendar",
        "BestBarbers": "api",
        "Flask": "web",
        "crontab": "cron",
        "NFS-e": "fiscal",
        "PTAX": "finance",
        "pró-labore": "finance",
        "Senhor Contábil": "contabil",
        "python3": "python",
        "subprocess": "shell",
        "requests": "http",
        "Playwright": "browser",
        "Slack": "slack",
        "Gmail": "email",
        "WebSearch": "web",
        "Garmin": "health",
        "garminconnect": "api",
        "Chart.js": "charts",
    }
    tags = []
    text_lower = text.lower()
    for kw, tag in tech_keywords.items():
        if kw.lower() in text_lower and tag not in tags:
            tags.append(tag)

    # Estatísticas
    n_lines = len(lines)
    n_sections = len(sections)

    # Conteúdo completo (preservado para exibição)
    content = text

    return {
        "name": name,
        "trigger": trigger,
        "title": title,
        "description": description,
        "sections": sections[:6],
        "tags": tags,
        "n_lines": n_lines,
        "n_sections": n_sections,
        "content": content,
        "file": str(md_file),
    }


def get_skills() -> list:
    if not COMMANDS_DIR.exists():
        return []
    skills = []
    for md_file in sorted(COMMANDS_DIR.glob("*.md")):
        skills.append(parse_skill(md_file))
    return skills


HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skills Dashboard</title>
<style>
:root {
  --bg:       #0d1117;
  --surface:  #161b22;
  --surface2: #1c2128;
  --border:   #30363d;
  --text:     #e6edf3;
  --muted:    #7d8590;
  --green:    #3fb950;
  --red:      #f85149;
  --yellow:   #d29922;
  --blue:     #58a6ff;
  --purple:   #bc8cff;
  --orange:   #e3b341;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
       background: var(--bg); color: var(--text); min-height: 100vh; font-size: 14px; }

/* Header */
header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 28px;
  height: 56px;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 10;
}
.logo { display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 15px; }
.logo-icon { font-size: 18px; }
.clock { font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }
.header-right { display: flex; align-items: center; gap: 16px; }
.shutdown-btn {
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--red); font-size: 12px; padding: 5px 12px;
  border-radius: 6px; cursor: pointer; transition: all 0.15s;
}
.shutdown-btn:hover { background: rgba(248,113,113,0.1); border-color: var(--red); }

/* Stats bar */
.stats-bar {
  display: flex; gap: 1px;
  background: var(--border);
  border-bottom: 1px solid var(--border);
}
.stat {
  flex: 1; background: var(--surface);
  padding: 12px 20px;
  display: flex; flex-direction: column; gap: 2px;
}
.stat-val { font-size: 22px; font-weight: 700; line-height: 1; }
.stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }

/* Grid layout */
main { padding: 24px 28px; display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }

/* Card */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  display: flex; flex-direction: column;
}
.card-header {
  padding: 16px 18px 12px;
  border-bottom: 1px solid var(--border);
}
.skill-trigger {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 16px; font-weight: 700;
  color: var(--purple);
  margin-bottom: 6px;
}
.skill-desc {
  font-size: 13px; color: var(--muted);
  line-height: 1.5;
}

/* Tags */
.tags-row { padding: 10px 18px; display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: .05em;
  padding: 2px 8px; border-radius: 99px;
}
.tag-api      { background: #1a2d3a; color: var(--blue);   border: 1px solid #2a4a5c; }
.tag-calendar { background: #1a2a1a; color: var(--green);  border: 1px solid #2a5c2a; }
.tag-web      { background: #2d1a2a; color: var(--purple); border: 1px solid #5c2a5c; }
.tag-cron     { background: #2d2a1a; color: var(--yellow); border: 1px solid #5c501a; }
.tag-fiscal   { background: #2d1a1a; color: var(--red);    border: 1px solid #5c2a2a; }
.tag-finance  { background: #2a1a3a; color: #d2a8ff;       border: 1px solid #4a2a6c; }
.tag-contabil { background: #2d2a1a; color: var(--orange); border: 1px solid #5c4a1a; }
.tag-python   { background: #1a2a2d; color: #79c0ff;       border: 1px solid #1a4a5c; }
.tag-shell    { background: #1c2128; color: var(--muted);  border: 1px solid var(--border); }
.tag-http     { background: #1a2d1a; color: var(--green);  border: 1px solid #1a5c35; }
.tag-browser  { background: #2a1a2d; color: #f0abfc;       border: 1px solid #5c2a5c; }
.tag-slack    { background: #1a2d2a; color: #6ee7b7;       border: 1px solid #2a5c4a; }
.tag-email    { background: #2d2a1a; color: #fcd34d;       border: 1px solid #5c4a1a; }

/* Meta info */
.meta-row {
  padding: 10px 18px;
  border-top: 1px solid var(--border);
  display: flex; gap: 20px;
  background: var(--surface2);
}
.meta-item { display: flex; flex-direction: column; gap: 1px; }
.meta-label { font-size: 10px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.meta-value { font-size: 12px; font-weight: 500; color: var(--muted); }

/* Sections list */
.sections-row { padding: 10px 18px 0; flex: 1; }
.sections-title { font-size: 10px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin-bottom: 6px; }
.section-item {
  font-size: 12px; color: var(--text);
  padding: 3px 0;
  display: flex; align-items: center; gap: 6px;
}
.section-item::before { content: '§'; color: var(--muted); font-size: 10px; }

/* Expandable content */
.expand-row { padding: 10px 18px 14px; }
details summary {
  cursor: pointer;
  font-size: 12px; color: var(--blue);
  user-select: none;
  list-style: none;
  display: flex; align-items: center; gap: 6px;
}
details summary::before { content: '▶'; font-size: 9px; transition: transform .2s; }
details[open] summary::before { transform: rotate(90deg); }
details summary::-webkit-details-marker { display: none; }
.content-box {
  margin-top: 10px;
  background: #010409;
  border: 1px solid var(--border);
  border-radius: 8px;
  max-height: 400px; overflow-y: auto;
  padding: 14px;
}
.content-box pre {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11.5px; line-height: 1.65;
  white-space: pre-wrap; word-break: break-word;
  color: #c9d1d9;
}
/* Simple markdown colorization in pre */
</style>
</head>
<body>

<header>
  <div class="logo">
    <span class="logo-icon">⚡</span>
    <span>Skills Dashboard</span>
  </div>
  <div class="header-right">
    <span class="clock" id="clock"></span>
    <button class="shutdown-btn" onclick="doShutdown()">&#9632; Encerrar</button>
  </div>
</header>

<div class="stats-bar">
  <div class="stat">
    <span class="stat-val" style="color:var(--purple)">{{ skills|length }}</span>
    <span class="stat-label">Skills disponíveis</span>
  </div>
  <div class="stat">
    <span class="stat-val" style="color:var(--blue)">{{ skills|sum(attribute='n_sections') }}</span>
    <span class="stat-label">Seções totais</span>
  </div>
  <div class="stat">
    <span class="stat-val" style="color:var(--muted)">{{ skills|sum(attribute='n_lines') }}</span>
    <span class="stat-label">Linhas de documentação</span>
  </div>
</div>

<main>
{% for skill in skills %}
<div class="card">

  <div class="card-header">
    <div class="skill-trigger">{{ skill.trigger }}{% if skill.title %} <span style="color:var(--muted);font-weight:400;font-size:13px">— {{ skill.title }}</span>{% endif %}</div>
    {% if skill.description %}
    <div class="skill-desc">{{ skill.description }}</div>
    {% endif %}
  </div>

  {% if skill.tags %}
  <div class="tags-row">
    {% for tag in skill.tags %}
    <span class="tag tag-{{ tag }}">{{ tag }}</span>
    {% endfor %}
  </div>
  {% endif %}

  {% if skill.sections %}
  <div class="sections-row">
    <div class="sections-title">Seções</div>
    {% for sec in skill.sections %}
    <div class="section-item">{{ sec }}</div>
    {% endfor %}
  </div>
  {% endif %}

  <div class="meta-row">
    <div class="meta-item">
      <span class="meta-label">Arquivo</span>
      <span class="meta-value">{{ skill.name }}.md</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Linhas</span>
      <span class="meta-value">{{ skill.n_lines }}</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Seções</span>
      <span class="meta-value">{{ skill.n_sections }}</span>
    </div>
  </div>

  <div class="expand-row">
    <details>
      <summary>Ver conteúdo completo</summary>
      <div class="content-box">
        <pre>{{ skill.content }}</pre>
      </div>
    </details>
  </div>

</div>
{% endfor %}
</main>

<script>
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleDateString('pt-BR') + ' ' + now.toLocaleTimeString('pt-BR');
}
setInterval(updateClock, 1000);
updateClock();

async function doShutdown() {
  if (!confirm('Encerrar o Skills Dashboard?')) return;
  try { await fetch('/shutdown', {method: 'POST'}); } catch(e) {}
  document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;color:#7d8a9a;font-family:system-ui;font-size:16px;">Dashboard encerrado.</div>';
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    skills = get_skills()
    return render_template_string(HTML, skills=skills)


@app.route("/shutdown", methods=["POST"])
def shutdown():
    import signal
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify(ok=True)


if __name__ == "__main__":
    print("Skills Dashboard: http://localhost:5556")
    app.run(host="127.0.0.1", port=5556, debug=False)
