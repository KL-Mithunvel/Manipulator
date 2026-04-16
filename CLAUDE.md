# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

---

## Claude Tracking Files

| File | Purpose |
|------|---------|
| `claude/claude_to_do.md` | Running list of all pending work, bugs, and features — updated every session |
| `claude/claude_log.md` | Session-by-session log of what was discussed and done — one entry per prompt |

Always read both files at the start of a new session to restore context. Update `claude_to_do.md` when tasks are completed or added. Append to `claude_log.md` at the end of every session.

---

## Project Overview

**Manipulator** is a Python-based interactive GUI toolkit for visualising and computing **forward and inverse kinematics** of robot manipulators in 2D.

- **Author:** KL Mithunvel (klm@smtw.in)
- **Entry point (FK creator):** `python RRR/sim_create.py`
- **Entry point (playback):** `python RRR/sim_view.py`
- **Python:** 3.10+ (uses `list[Pose]` type hint syntax)
- **GUI layer:** matplotlib (embedded widgets — sliders, buttons, textboxes)
- **Target:** Windows dev machine for now; no hardware dependency

The project starts with a **planar 2D RRR** (three revolute joints) manipulator and is designed to be extended to other types (LLR, LOO, RRP, etc.) as modular additions.

---

## Running the System

```bash
# Activate venv first — always
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# FK pose creator (interactive joint control + CSV export)
python RRR/sim_create.py

# Playback viewer (animate a saved pose CSV)
python RRR/sim_view.py

# Lint check
python -m py_compile RRR/sim_create.py
python -m py_compile RRR/sim_view.py

# Tests (once tests/ exists)
pytest tests/
```

---

## Architecture

### Current file layout

| File | Role |
|------|------|
| `RRR/sim_create.py` | FK pose creator — interactive sliders, text inputs, pose save + CSV export |
| `RRR/sim_view.py` | CSV playback animator — load poses, Play/Pause/Scrub/Speed |
| `RRR/data/arm_poses_5.csv` | Sample pose data (2 rows, minimal) |

### Data flow

```
sim_create.py
  sliders / textboxes
        |
        v
      fk()  ──>  matplotlib canvas (2D arm plot)
        |
    save_pose()
        |
    export_csv()  ──>  arm_poses_export.csv
                              |
                              v
                       sim_view.py
                      np.interp() over time
                              |
                        FuncAnimation  ──>  matplotlib canvas
```

### Planned target layout (modular / reusable)

```
Manipulator/
├── core/
│   ├── kinematics.py     # shared fk(), ik(), deg2rad(), safe_float()
│   └── config.py         # load/save YAML config (link lengths, limits)
├── RRR/
│   ├── sim_create.py     # RRR FK GUI (uses core/)
│   ├── sim_view.py       # RRR playback (uses core/)
│   └── ik_solver.py      # RRR IK (geometric / numerical) — planned
├── LLR/                  # future
├── tests/
├── docs/
│   └── project.md
└── claude/
    ├── claude_to_do.md
    └── claude_log.md
```

---

## Key Modules

### `RRR/sim_create.py`

- **`fk(th1_deg, th2_deg, th3_deg, base_xy)`** → `(p0, p1, p2, pb)` — returns joint positions as (x, y) tuples. L1=140mm, L2=140mm, LB=55mm (hardcoded — known debt).
- **`ArmGUI`** — main GUI class. Holds `self.poses: list[Pose]`, sliders, textboxes, canvas. `update()` redraws on every slider change.
- **`Pose`** — dataclass: `time_s`, `th1`, `th2`, `th3`.
- **`export_csv()`** — writes sorted poses to `arm_poses_export.csv` in the working directory.
- **`_lock`** — bool guard to prevent slider↔textbox feedback loops.

### `RRR/sim_view.py`

- **`fk()`** — same formula as sim_create, but **L2=130mm** (inconsistency — known debt).
- **`angles_at(time_s)`** — `np.interp` over loaded CSV arrays.
- **`FuncAnimation`** loop — advances `current_time` by `(1/FPS) * speed.val` per frame.
- Uses **module-level globals** for state (`playing`, `current_time`, `base_x`, etc.) — not class-based (known debt).
- CSV path hardcoded at top of file (known debt).

---

## Known Technical Debt

1. **Duplicated `fk()`, `deg2rad()`, `safe_float()`** across `sim_create.py` and `sim_view.py` — violates DRY. Extract to `core/kinematics.py`.
2. **L2 inconsistency** — `sim_create.py` uses L2=140mm, `sim_view.py` uses L2=130mm. Must be unified in a single config.
3. **Hardcoded link lengths** in both files. Must move to `config.yaml` or a config dataclass passed at runtime.
4. **`sim_view.py` uses module-level globals** instead of a class. Refactor to match `ArmGUI` pattern.
5. **Hardcoded CSV path** in `sim_view.py` (`CSV_PATH = "data/arm_poses_5.csv"`). Should be a CLI arg or file-picker.
6. **No inverse kinematics** — not yet implemented.
7. **No `requirements.txt`** — dependencies not tracked.
8. **No `tests/`** — no test coverage at all.
9. **Not extensible** — no shared base class or interface for different manipulator types.

---

## Development Rules

1. **All shared maths (fk, ik, deg2rad, safe_float) live in `core/kinematics.py`** — never duplicate across manipulator modules.
2. **Link lengths, joint limits, and hardware parameters go in config** — never hardcode them in logic files.
3. **Every manipulator module must expose the same interface** — `fk()`, `ik()` with consistent signatures — so the GUI shell can be reused.
4. **`sim_view.py` must be refactored to a class** before any new features are added to it.
5. **No writing to MS SQL** (if any DB integration is added in future).
6. **Tests live in `tests/`** and cover at least: FK correctness for known angles, IK round-trip (FK(IK(target)) ≈ target).

---

## Project TODO List

Legend: 🔴 Bug / rule violation | 🟡 Incomplete feature | 🟢 Not started | ✅ Done

### CRITICAL
- 🔴 Fix L2 inconsistency between sim_create (140mm) and sim_view (130mm)

### HIGH
- 🔴 Extract duplicated `fk()`, `deg2rad()`, `safe_float()` into `core/kinematics.py`
- 🔴 Move link lengths to config (YAML or dataclass) — remove all hardcoded values
- 🟡 Refactor `sim_view.py` from module globals to a class

### MEDIUM
- 🟢 Replace hardcoded CSV path in `sim_view.py` with CLI arg or file dialog
- 🟢 Add `requirements.txt`
- 🟢 Create `tests/` with FK correctness tests

### NOT STARTED
- 🟢 Implement RRR inverse kinematics (geometric closed-form solution)
- 🟢 IK GUI panel — target (x, y, φ) input → solve → display joint angles
- 🟢 Workspace reachability visualisation
- 🟢 Design shared manipulator interface for LLR, LOO, RRP, etc.
- 🟢 LLR manipulator module
- 🟢 LOO manipulator module

---

## User Rules

### Interaction Rules

- **Every git commit must include a co-author trailer** for `kl mithunvel <klm@smtw.in>`. Add the following line at the end of every commit message body (after a blank line):
  ```
  Co-authored-by: kl mithunvel <klm@smtw.in>
  ```

- **Always explain before acting.** Before making any code changes, edits, or file writes, describe exactly what you are going to do and wait for explicit confirmation from the user. List every file that will be changed and what will change in each. Do not proceed until the user says to go ahead.

### Deployment Model

**The hard rule: write and test on the development machine first. Hardware comes last.**

This project is currently dev-machine only (no hardware target). All development and testing happens on Windows.

### Commands & Workflow

- **Always activate the project virtualenv before running any Python command.** Use `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS). Never invoke `python` or `pip` bare without the venv active.
- Track all dependencies in `requirements.txt`. Pin at least the major version. Run `pip freeze > requirements.txt` after installing anything new.
- A migration to `uv` is planned. Flag `uv` as a recommended replacement whenever suggesting new tooling or packaging steps.
- Run lints (`python -m py_compile` at minimum, `flake8` or `ruff` if configured) and the test suite before every commit.

### Software Engineering Preferences

- **DRY**: Extract shared logic into reusable functions. Avoid copy-pasting code blocks.
- **Testing is important**: Write tests for new functionality. Cover the happy path and key failure modes. Use `pytest`; tests live in `tests/`.
- **Consider edge cases**: Think about nulls, empty inputs, boundary values. Clarify if requirements are ambiguous.
- **Explicit over implicit**: Write clear, readable code. Avoid magic numbers, obscure one-liners, hidden side effects.
- **Proper error handling**: Handle errors at the right level. Return meaningful messages. Don't silently swallow exceptions.
- **Deprecation**: Never use deprecated APIs / functions / modules. Rewrite if found.

### General Principles

- **Simplicity first**: Minimal, straightforward code. No over-engineering.
- **Explain Always**: Document code and decisions. Explain choices and how things work.
- **Backend-heavy**: Prefer logic in the backend; keep frontends thin.

### Tech Stack Preferences

| Layer | Choice | Notes |
|---|---|---|
| Language | Python (latest stable) | |
| GUI | matplotlib (current) → Tkinter (planned) | Tkinter preferred for production GUI |
| Maths | `math`, `numpy` | |
| Database | SQLite (if needed) | Never write to MS SQL |
| Config | YAML | |
| Packaging | pip + venv | Planned migration to uv |
| Testing | pytest | |
| Platform | Windows (dev), Ubuntu LTS (future) | Guard OS-specific code |