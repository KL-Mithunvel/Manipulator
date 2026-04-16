# Claude Log

A running record of what was done each session, prompt by prompt.

---

## Session 2 — 2026-04-17

### Prompt 1
User asked Claude to read all documents and understand the project.

**What was done:**
- Read `claude_to_do.md`, `claude_log.md`, `RRR/sim_create.py`, `RRR/sim_view.py`, `RRR/README.md`, `docs/project.md`
- Summarised current state: FK working, 9 known debt items, IK not yet built

### Prompt 2
User asked for an IK version of `sim_create.py` with all the same features.

**What was done:**
- Described plan in full (3 files), waited for confirmation
- User confirmed ("ok go ahead")
- Created `core/__init__.py` — empty package marker
- Created `core/kinematics.py` — shared `deg2rad`, `rad2deg`, `safe_float`, `clamp`, `fk()`, `ik()` (both elbow-up and elbow-down, returns None per solution if unreachable)
- Created `RRR/ik_create.py` — full IK GUI: px/py/φ sliders + textboxes, elbow UP/DOWN toggle, active solution solid, alternate solution dashed grey, red X target marker, base position controls, yellow box controls, save/clear/export CSV, pose list — all matching sim_create.py structure
- Both files compile clean (`python -m py_compile`)

---

## Session 1 — 2026-03-23

### Prompt 1
User asked Claude to review and format the existing `CLAUDE.md` (which was the template library file).

**What was done:**
- Read and analysed `CLAUDE.md` in full
- Identified formatting issues: nested fenced code blocks in the Deployment Notes example, inconsistent table separators, ambiguous `.js` frontend entry, missing trailing newline
- Described proposed changes to user and waited for confirmation
- User did not confirm this pass — moved to providing project context instead

---

### Prompt 2
User gave project context: building a FK/IK GUI for robot manipulators (RRR first, then LLR, LOO, etc.), wants it robust and reusable.

**What was done:**
- Asked clarifying questions (GUI framework, 2D vs 3D, IK interaction model, joint notation, reusability pattern)

---

### Prompt 3
User shared that existing code is in `RRR/` folder and asked Claude to review it. Also requested:
- `docs/project.md` — detailed project document
- `CLAUDE.md` updated to project-specific format
- `README.md` — proper welcome and intro

**What was done:**
- Read `RRR/sim_create.py`, `RRR/sim_view.py`, `RRR/data/arm_poses_5.csv`
- Analysed both files — found 9 issues (L2 inconsistency, DRY violations, globals in sim_view, hardcoded paths, missing IK, no tests, no requirements.txt, not extensible)
- Presented full analysis and plan to user, waited for confirmation

---

### Prompt 4
User confirmed ("yes") — proceed with all three files.

**What was done:**
- User interrupted mid-execution and said "just fix plan 3" (README only)
- Wrote `README.md` with welcome, feature summary, manipulator type table, project structure, getting started commands

---

### Prompt 5
User asked to proceed with CLAUDE.md and docs updates, and also requested a `claude/` folder with `claude_to_do.md` and `claude_log.md`.

**What was done:**
- Rewrote `CLAUDE.md` as a full project-specific brief (Project Overview, Running, Architecture, Key Modules, Known Tech Debt, Dev Rules, TODO, User Rules verbatim)
- Created `docs/project.md` — full project brief including goals, current state, target architecture, RRR kinematics reference, CSV format, open questions
- Created `claude/claude_to_do.md` — full TODO list by priority
- Created `claude/claude_log.md` — this file
- User also asked to reference `claude_log` and `claude_to_do` in `CLAUDE.md`

---

### Prompt 6
User asked for a `RRR/README.md` that:
- Describes the RRR arm (it's an excavator-style digger — θ3 is a bucket end-effector)
- The yellow box = target dig zone to excavate
- Documents what needs to be done: IK, coverage path planning, Arduino export
- Highlights that servo specs (model, orientation, PWM range, zero position, direction) must be gathered from the physical hardware before IK or Arduino code can be written

**What was done:**
- Created `RRR/README.md` with: arm description, joint/role diagram, hardware servo table (blank — to be filled from physical build), link dimension table, FK reference, IK geometric solution, dig zone coverage strategy (raster sweep), Arduino conversion plan, file status table, known issues, immediate next steps