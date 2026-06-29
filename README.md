# V.A.U.L.T.

**Visual Agent Utility Launcher & Terminal**

A local web dashboard for [Claude Code](https://claude.ai/code) that lets you browse, search, and launch all your skills in one click — while keeping your school tasks and calendar right next to your dev tools.

![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/license-MIT-teal?style=flat-square)

---

## 🎬 Part of the Agentic OS Series

This project is built following **["Build an Agentic OS with Claude Code"](https://www.youtube.com/watch?v=HRw-vP0j8OM)** — a series on building a personal operating system powered by AI agents.

VAULT covers **Phases 3 & 4** of the series:

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Claude Code fundamentals & terminal workflow | 🔜 Coming soon |
| 2 | Skills, hooks & custom commands setup | 🔜 Coming soon |
| **3** | **Custom UI launcher with skill cards** | ✅ **This project** |
| **4** | **Publishing & distributing via GitHub** | ✅ **This repo** |

Phases 1 and 2 will be documented here as the series progresses.

---

## Why VAULT?

The terminal requires you to remember exact syntax. VAULT shows you everything at once.

| Without VAULT | With VAULT |
|---|---|
| Remember `/investigate`, `/qa`, `/ship` from memory | Browse 38+ skills organized by category |
| Close the terminal and lose your output | Output persists in the browser |
| Dev tools and life admin in separate apps | School deadlines + Claude skills in one view |
| Discover a skill by accident or not at all | Search bar surfaces everything instantly |

> It's like working from the terminal, but with discoverability, a warm UI, and your school deadlines in the sidebar.

---

## Features

- 🗂 **Skill browser** — all Claude Code skills as cards, organized in 9 categories (Engineering, Planning, Design, Context, Content, iOS, GStack, Assistant, General)
- 🔍 **Instant search** — filter by name, description, or category in real time
- ▶ **One-click launch** — click a card, add optional args, stream output live
- 📡 **SSE streaming** — skill output appears line by line directly in the browser
- 📅 **School calendar** — mini monthly calendar with task due-date highlights
- ✅ **Task tracker** — add exams, homeworks, and activities with due dates and subjects
- 🎨 **Mid-century modern design** — California Bungalow palette, DM Serif Display + DM Sans typography
- 📊 **Run counter** — tracks executions across sessions via `localStorage`

---

## Getting Started

### Requirements

- Python 3.8+
- [Claude Code CLI](https://claude.ai/code) installed and authenticated
- Skills living in `~/.claude/commands/` (auto-detected on every load)

### Install

```bash
git clone https://github.com/Anton-mapa/V.A.U.L.T.
cd V.A.U.L.T.
pip install flask
python app.py
```

Then open **http://localhost:5000**.

### Windows launcher

```powershell
.\start.ps1
```

Kills any previous instance on port 5000, starts Flask in the background, waits for it to be ready, and opens the browser automatically.

---

## Usage

### Launching a skill

1. Click any card in the skill grid
2. A dialog opens — type optional arguments (URL, file path, etc.)
3. Click **▶ Ejecutar** and watch the output stream live at the bottom

### Adding a task

1. Click **+ Agregar tarea** in the left sidebar
2. Fill in: title, category (Tarea / Examen / Actividad / Clase / Otro), subject, due date
3. Tasks are saved in `tasks.json` and sorted automatically by due date

### Searching skills

Type in the search bar — filters by name, description, or category without page reload.

---

## Project Structure

```
V.A.U.L.T./
├── app.py              # Flask backend — skills API, tasks CRUD, SSE runner
├── static/
│   └── index.html      # Full frontend in a single file (HTML + CSS + JS)
├── tasks.json          # Local task storage — auto-created, gitignored
├── start.ps1           # Windows launcher script
└── requirements.txt    # Python dependencies
```

Skills are auto-detected from `~/.claude/commands/*.md`. Category assignments live in `app.py`; anything unmapped falls into **General**.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3, Flask, Server-Sent Events (SSE) |
| Frontend | Vanilla HTML/CSS/JS — no bundler, no framework |
| Typography | DM Serif Display + DM Sans (Google Fonts) |
| Skills source | `~/.claude/commands/*.md` (frontmatter parsed) |
| Task storage | `tasks.json` (local file, no database) |
| Color palette | California Bungalow — teal `#2A7A7A`, terracotta `#C4614A`, ivory `#FEFAF4` |

---

## Roadmap

Next steps, following the video series and personal needs:

- [ ] **Google Calendar integration** — auto-import exams and activities from Google Calendar (OAuth2)
- [ ] **Always-visible input bar** — type `/skill args` or free-form text directly into Claude
- [ ] **Wider sidebar** (300px) with full-month navigation and bigger calendar cells
- [ ] **shadcn-inspired components** — consistent button/input system in vanilla CSS
- [ ] **Toast notifications** — feedback when tasks are added or skills complete
- [ ] **Phases 1 & 2 documentation** — terminal fundamentals and skills setup guide

---

## License

MIT — fork it, extend it, make it yours.

---

<p align="center">
  Built with <a href="https://claude.ai/code">Claude Code</a> &nbsp;·&nbsp; Part of the <a href="https://www.youtube.com/watch?v=HRw-vP0j8OM">Agentic OS series</a>
</p>
