import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

COMMANDS_DIR = Path(r"C:\Users\Hogar\.claude\commands")
SKILLS_DIR   = Path(r"C:\Users\Hogar\.claude\skills")
TASKS_FILE   = Path(__file__).parent / "tasks.json"

CATEGORIES = {
    "Engineering": ["investigate", "health", "qa", "qa-only", "review", "ship", "retro",
                    "browse", "diagram", "canary", "guard", "freeze", "unfreeze"],
    "Planning":    ["plan-tune", "plan-ceo-review", "plan-design-review",
                    "plan-devex-review", "plan-eng-review", "autoplan", "spec"],
    "Design":      ["design-review", "design-html", "design-consultation",
                    "design-shotgun", "ios-design-review"],
    "Context":     ["context-save", "context-restore", "learn", "careful", "pair-agent"],
    "Content":     ["make-pdf", "scrape", "hackernews-frontpage", "document-generate",
                    "document-release", "landing-report"],
    "iOS":         ["ios-fix", "ios-qa", "ios-clean", "ios-sync"],
    "GStack":      ["gstack-main", "gstack-upgrade", "gstack-openclaw-ceo-review",
                    "gstack-openclaw-investigate", "gstack-openclaw-office-hours",
                    "gstack-openclaw-retro", "open-gstack-browser", "land-and-deploy"],
    "Assistant":   ["office-hours", "find-skills", "benchmark", "benchmark-models",
                    "codex", "sync-gbrain", "setup-gbrain"],
}

CAT_LOOKUP = {skill: cat for cat, skills in CATEGORIES.items() for skill in skills}


# ─── Skills ─────────────────────────────────────────────────────────────

def _parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    fm = text[3:end]
    result = {}
    for m in re.finditer(r'^(\w[\w-]*):\s*(.+)$', fm, re.MULTILINE):
        result[m.group(1)] = m.group(2).strip().strip('"')
    return result


def get_skills():
    skills = []
    seen   = set()
    for f in sorted(COMMANDS_DIR.glob("*.md")):
        name = f.stem
        if name in seen:
            continue
        seen.add(name)
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""
        fm   = _parse_frontmatter(text)
        desc = fm.get("description", "").strip('"') or f"Run /{name}"
        desc = re.sub(r'\s*\(gstack\)$', '', desc)
        skills.append({
            "name":        name,
            "description": desc,
            "category":    CAT_LOOKUP.get(name, "General"),
            "type":        "command",
        })
    return skills


# ─── Tasks ─────────────────────────────────────────────────────────────

def load_tasks():
    if not TASKS_FILE.exists():
        return []
    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_tasks(tasks):
    TASKS_FILE.write_text(
        json.dumps(tasks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ─── Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/skills")
def api_skills():
    return jsonify(get_skills())


@app.route("/api/tasks", methods=["GET"])
def api_tasks_get():
    return jsonify(load_tasks())


@app.route("/api/tasks", methods=["POST"])
def api_tasks_post():
    data  = request.get_json(silent=True) or {}
    tasks = load_tasks()
    task  = {
        "id":         str(uuid.uuid4()),
        "title":      data.get("title", "").strip(),
        "category":   data.get("category", "Tarea"),
        "subject":    data.get("subject", "").strip(),
        "due_date":   data.get("due_date", ""),
        "done":       False,
        "created_at": datetime.now().isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(task), 201


@app.route("/api/tasks/<task_id>", methods=["PUT"])
def api_tasks_put(task_id):
    data  = request.get_json(silent=True) or {}
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            for k, v in data.items():
                if k != "id":
                    t[k] = v
            save_tasks(tasks)
            return jsonify(t)
    return jsonify({"error": "not found"}), 404


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def api_tasks_delete(task_id):
    tasks = [t for t in load_tasks() if t["id"] != task_id]
    save_tasks(tasks)
    return jsonify({"ok": True})


@app.route("/api/run")
def api_run():
    skill = request.args.get("skill", "").strip()
    args  = request.args.get("args",  "").strip()
    if not skill:
        return jsonify({"error": "No skill"}), 400

    prompt = f"/{skill}" + (f" {args}" if args else "")

    def generate():
        yield f"data: {json.dumps({'type': 'start', 'prompt': prompt})}\n\n"
        try:
            proc = subprocess.Popen(
                ["claude", "-p", prompt, "--output-format", "text"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=r"C:\Users\Hogar",
                env={**os.environ},
            )
            for line in proc.stdout:
                yield f"data: {json.dumps({'type': 'output', 'text': line})}\n\n"
            proc.wait()
            yield f"data: {json.dumps({'type': 'done', 'code': proc.returncode})}\n\n"
        except FileNotFoundError:
            yield f"data: {json.dumps({'type': 'error', 'text': 'claude not found on PATH'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"V.A.U.L.T. running at http://localhost:{port}")
    app.run(debug=False, port=port, threaded=True)
