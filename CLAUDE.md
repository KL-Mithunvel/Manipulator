# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Repository Purpose

This repo is a curated library of `CLAUDE.md` files from **KL Mithunvel's** projects. Each file serves as a project brief for AI-assisted development sessions — capturing architecture, rules, conventions, and status so that Claude Code can contribute effectively without needing to re-discover project context from scratch.

The files here are used as **standard templates and reference material** for future projects.

---

## Repo Structure

| File | Project |
|------|---------|
| `herc.md` | HERC-26 — rover telemetry and control system (Team MOVIS, Human Exploration Rover Challenge) |
| `MGIT.md` | MGitPi — menu-driven, cyber-styled Git control interface for Raspberry Pi |

New entries follow the same naming convention: `<short-project-id>.md`.

---

## How to Use These Files

When starting a new project or a new AI session on an existing project:

1. Copy the relevant `.md` file into the project root and rename it `CLAUDE.md`.
2. Update the **Project Overview**, **Architecture**, **Current Status**, and **TODO List** sections to match the actual project state.
3. Keep the **Development Rules** and **User Rules** sections verbatim — they are standard across all projects unless explicitly overridden.
4. Fill in `Schema Reference` and `Key Conventions` for any project with a database or non-obvious data encoding. Delete them only if the project has no data layer at all.
5. Fill in `Deployment Notes` for any project with a hardware or remote server target.

---

## Standard User Rules (Apply to Every Project)

These rules carry over to every `CLAUDE.md` derived from this library. Copy this entire section into derived files verbatim.

### Interaction Rules

- **Every git commit must include a co-author trailer** for `kl mithunvel <klm@smtw.in>`. Add the following line at the end of every commit message body (after a blank line):
  ```
  Co-authored-by: kl mithunvel <klm@smtw.in>
  ```

- **Always explain before acting.** Before making any code changes, edits, or file writes, describe exactly what you are going to do and wait for explicit confirmation from the user. List every file that will be changed and what will change in each. Do not proceed until the user says to go ahead.

### Deployment Model

**The hard rule: write and test on the development machine first. Hardware comes last.**

This applies to every project that has a hardware target (Raspberry Pi, Arduino, embedded Linux, remote server). It is not optional.

#### Stages — always in this order

1. **Code on dev machine** — write all logic, module interfaces, and data flows on the laptop/desktop. The dev machine is Windows or Linux; it has no GPIO, no I2C, no serial ports.
2. **Test on dev machine** — run the full test suite (`pytest`). Verify the feature works end-to-end using the simulation/dev stack (fake sensors, mock hardware, local SQLite). Fix all failures before moving on.
3. **Review for hardware impact** — before touching the device, explicitly state which parts of the change touch real hardware (GPIO pins, I2C addresses, serial ports, baud rates) and which parts are pure logic.
4. **Deploy to hardware** — only after steps 1–3 are complete. Transfer code via `git pull`, `rsync`, `scp`, or `arduino-cli` as appropriate for the project. Run the hardware smoke test.
5. **Verify on hardware** — run the hardware-specific test or verification script. Note any behaviour difference from simulation. If there is a discrepancy, fix it on the dev machine (step 1) and repeat — never patch directly on the device.

#### Rules that follow from this

- **Every hardware driver must have a simulated equivalent** that runs on the dev machine and produces the same data shape and exceptions. Code written without a simulation path cannot be tested in stage 2 and breaks the workflow.
- **Never hardcode hardware addresses, port names, or pin numbers in driver files.** They go in `config.xml` / `config.yaml` and are passed as parameters. This lets the same code run in simulation (with dev values) and on hardware (with real values).
- **When proposing a change**, always separate it into: (a) logic that can be fully verified on the dev machine, and (b) hardware-specific parts that need device testing. State both explicitly so the user knows what to test where.
- **Never instruct the user to "just run it on the Pi"** as a substitute for a dev-machine test. If a test cannot be run on the dev machine due to hardware dependency, say so clearly and explain what the device test will verify.

### Commands & Workflow

- **Always activate the project virtualenv before running any Python command.** Use `source venv/bin/activate` (Linux/macOS/Pi) or `venv\Scripts\activate` (Windows). Never invoke `python` or `pip` bare without the venv active.
- Track all dependencies in `requirements.txt`. Pin at least the major version. Run `pip freeze > requirements.txt` after installing anything new.
- A migration to `uv` is planned. Flag `uv` as a recommended replacement whenever suggesting new tooling or packaging steps.
- Run lints (`python -m py_compile` at minimum, `flake8` or `ruff` if configured) and the test suite before every commit.

### Software Engineering Preferences

- **DRY (Don't Repeat Yourself)**: Extract shared logic into reusable functions. Avoid copy-pasting code blocks.
- **Testing is important**: Write tests for new functionality. Cover the happy path and key failure modes. Use `pytest`; tests live in `tests/`.
- **Consider edge cases**: Think about nulls, empty inputs, boundary values, and concurrent access. Clarify with me if requirements are ambiguous.
- **Explicit over implicit and clever**: Write clear, readable code. Avoid magic numbers, obscure one-liners, and hidden side effects. If someone has to puzzle over what it does, rewrite it.
- **Proper error handling**: Handle errors at the right level. Return meaningful messages. Don't silently swallow exceptions.
- **Deprecation**: Never use deprecated APIs / functions / modules. If found, rewrite to avoid them after consulting me.

### General Principles

- **Simplicity first**: Minimal, straightforward code. No over-engineering.
- **Explain Always**: Document your code and decisions. Make it easy for me to understand. Explain choices, how things work.
- **Backend-heavy**: Prefer logic in the backend; keep frontends thin.

### Tech Stack Preferences

| Layer | Choice | Notes |
|---|---|---|
| Languages | Python (latest stable), JavaScript/TypeScript | |
| Backend frameworks | Flask, FastAPI (in future) | Flag when FastAPI would be a better fit |
| Frontend frameworks | .js (keep it simple — I'm learning these) | |
| Python GUI | Tkinter | When needed |
| Database | SQLite (preferred), MS SQL (read-only source), SQLite (local/app data) | **Never write to MS SQL** |
| Python packaging | pip + venv | Planned to migrate to uv — point out if recommended |
| Configuration | YAML for settings/config files | |
| Infrastructure | Windows, Debian Raspberry Pi, Ubuntu LTS | Guard any OS-specific code |

---

## Standard Template Structure

Every `CLAUDE.md` in this library follows this skeleton. **Sections marked `[if applicable]` are included when relevant and omitted otherwise.** Each section includes a one-line description of exactly what belongs there — fill it in completely or delete it; a half-filled section is worse than a missing one.

```
# CLAUDE.md

## Project Overview
  — What the project is, who built it, the core problem it solves.
  — Author, license, entry point, minimum runtime versions.

## Running the System
  — Copy-paste-ready commands to start, test, and lint.
  — Virtualenv activation step first.
  — Dev/simulation mode commands separated from hardware/production commands.
  — Any seed-data or one-time setup steps.

## Architecture
  — Module responsibilities table (file → role).
  — Data flow diagram (ASCII).
  — Threading or async model (background threads, queues, event loops).
  — Two modes if applicable: simulation/dev vs real/hardware, and how to switch.

## Key Modules
  — One subsection per file or logical group.
  — Public interface: function names, parameters, return types, exceptions raised.
  — Side effects and I/O (files written, network calls, hardware access).

## Schema Reference  [if applicable — any project with a DB or external data source]
  — Path to the DDL / schema file and what it covers (table count, source DB engine).
  — Read-only vs writable databases — call out explicitly which is which.
  — Any tooling for probing or inspecting the DB (probe scripts, GUIs, CLI commands).
  — Path to the annotated schema doc (SCHEMA.md or equivalent) if one exists.
  — Standing instruction: update the annotated doc whenever a new table relationship
    or encoding is discovered — do it in the same commit, not as a follow-up.

## Key Conventions  [if applicable — any non-obvious encoding, key, or domain rule]
  — Universal row keys (name, type, which tables carry it).
  — Encoded fields: encoding formula AND decode formula, both written out in full.
    Never leave the decode implicit — Claude will guess wrong without it.
  — Sentinel / special values: what NULL means, what -1 means, what empty string means.
  — "Current record" pattern: which column and which value indicate the active row.
  — Per-tenant / per-company data partitioning: directory layout, naming convention,
    and the helper function that resolves the path.
  — Environment variables: name, what it overrides, and the hard-coded default.

## Data Files
  — What is stored, where, and whether it is git-tracked.
  — Runtime-generated files (logs, caches, DBs) vs committed files.
  — Files that must never be committed (credentials, large binaries).

## Platform Constraints
  — Target OS(es) and any OS-specific branching in the code.
  — Libraries that are Linux/Pi-only and how each is guarded (try/except ImportError).
  — Hardware dependencies (I2C, UART, GPIO, RS485) and their dev-mode equivalents.

## Deployment Notes  [if applicable — projects with a hardware or remote server target]
  — Two environment table: dev machine (OS, Python version, what hardware is absent)
    vs deployment target (OS, Python version, what hardware is present).
  — How to transfer code: exact command (git pull / rsync / scp / arduino-cli upload).
  — One-time setup steps on the target that are NOT in requirements.txt
    (apt packages, lgpio shim install, system services, udev rules, etc.).
  — Pre-deploy checklist: what must pass on the dev machine before touching hardware.
  — Hardware smoke-test: the exact command to run on the device to confirm it works.
  — Config / env differences between dev and deployment
    (port names, GPIO chip paths, I2C addresses, env vars that change).

## Known Technical Debt
  — Existing rule violations, numbered by the rule they violate (file + line if known).
  — Temporary workarounds that must be cleaned up before the next milestone.
  — Do not omit or minimise debt — document it so it is not accidentally perpetuated.

## Development Rules
  — Binding architectural rules, each numbered and sourced (wiki page, agreed spec, etc.).
  — Rules are referenced by number in TODO items and commit messages.

## Project TODO List
  Legend: 🔴 Bug / rule violation  |  🟡 Incomplete feature  |  🟢 Not started  |  ✅ Done
  Group by severity: CRITICAL → HIGH → MEDIUM → LOW → NOT STARTED → DONE.

## User Rules
  — Paste the full Standard User Rules section here verbatim.
  — Add project-specific overrides or additions below them, clearly labelled.
```

---

## Filled-In Example: Schema Reference & Key Conventions

The two sections below are the most often under-filled. Copy this block into a new
project brief and replace every value with the project's actual data.
This example is drawn from a real payroll/HR system project.

```markdown
## Schema Reference

- `schema/schema.sql` — Full DDL exported from the source DB (~200 tables, MS SQL)
- `schema/SCHEMA.md` — Annotated interpretation: table purposes, join paths, quirks
- **The MS SQL schema is read-only — NEVER ATTEMPT TO CHANGE IT.**
- Use `tooling/probe.py <TABLE_NAME>` to fetch sample records from any table.
- Update `schema/SCHEMA.md` in the same commit whenever a new table relationship
  or field encoding is discovered. Do not leave it as a follow-up.

## Key Conventions

- **EMPID** — universal employee key across all tables; always an integer; never null.
- **MONTHYEAR** — int encoded as `YEAR * 12 + MONTH` (not YYYYMM, not a date).
  Encode: `MY = year * 12 + month`
  Decode: `month = MY % 12 or 12`,  `year = MY // 12 - (1 if month == 12 else 0)`
  Example: April 2024 → `2024*12 + 4 = 24292`; `24292 % 12 = 4`, `24292 // 12 = 2024`
- **MAS_EMPLOYEEDET**: `EFFTODATE IS NULL` = current / active record for that employee.
  Always filter with `WHERE EFFTODATE IS NULL` when you want the current state.
- **Department / Designation / Grade** are `nvarchar` text PKs, not integer IDs.
  Never assume they are integers or that a lookup table maps them to display names.
- **Per-company data** is stored under `backend/data/<DB_NAME>/` (e.g. `STANDARD_1/`).
  Always resolve this path via `_company_data_dir(db_name)` in `app.py` — never
  construct the path by hand.
- **`SARALWEB_DATA`** env var overrides the data root directory.
  Default: `backend/data/`. Set it in `.env` or the shell before starting the server.
```

### What makes these sections effective

| Property | Why it matters |
|---|---|
| Decode formula written out in full | Claude will derive the wrong formula from the name alone (`MONTHYEAR` looks like YYYYMM) |
| A worked numeric example for encoded fields | Confirms the formula is correct; catches off-by-one errors in the doc itself |
| "Current record" sentinel named explicitly | Without this, Claude queries all history rows and gets inflated results |
| PK type stated (text vs int) | Prevents type-mismatch bugs in generated SQL and ORM queries |
| Path helper named (`_company_data_dir`) | Prevents hand-rolled path strings scattered across the codebase |
| Env var default value stated | Lets Claude reason about behaviour without needing to read the source |

---

## Filled-In Example: Deployment Notes

Use this as the model for any project that targets a Raspberry Pi, embedded board,
or remote server. Replace every value. Example is drawn from the HERC-26 rover project.

```markdown
## Deployment Notes

### Environments

| | Dev machine | Raspberry Pi (deployment) |
|---|---|---|
| OS | Windows 11 / Ubuntu 22.04 | Raspberry Pi OS (Debian Bookworm, 64-bit) |
| Python | 3.12 (system or venv) | 3.11 (system) |
| Sensor hardware | None — simulated via `sensor/dev_stack.py` | TMP102, BNO055, GPS, MH-Z19C, PZEM-017, ADS1115 |
| GPIO | Not available | `/dev/gpiochip4` (Pi 5) or `/dev/gpiochip0` (Pi 4) |
| Entry point | `python main_sim.py` | `python main.py` |
| Dashboard URL | `http://127.0.0.1:5000` | `http://<pi-ip>:5000` |

### Transferring Code to the Pi

```bash
# On the Pi — pull latest from the branch
git pull origin main

# Or from dev machine — push files directly
rsync -avz --exclude '.git' --exclude 'data/' ./ pi@<pi-ip>:~/herc26/
```

### One-Time Setup on the Pi (not in requirements.txt)

```bash
sudo apt install python3-smbus python3-libgpiod python3-flask
pip install --break-system-packages ./compat   # lgpio shim for Pi 5
# pynmea2 requires a venv with --system-site-packages
python3 -m venv --system-site-packages venv && source venv/bin/activate
pip install pynmea2
```

### Pre-Deploy Checklist (must pass on dev machine first)

- [ ] `pytest tests/` passes with zero failures
- [ ] `python main_sim.py` starts and dashboard loads at `http://127.0.0.1:5000`
- [ ] SQLite log (`data/rover_logs.sqlite`) is being written each poll cycle
- [ ] No `TODO` stubs in any function that will be called during the deployment run

### Hardware Smoke Test (run on Pi after deploy)

```bash
# Verify each sensor individually before running the full stack
python sensor/tmp.py        # should print live °C readings
python sensor/imu.py        # should print orientation + g-force
python sensor/gps.py        # should print lat/lon (may show void if no fix yet)
python sensor/air.py        # should print CO2 ppm
python sensor/power_meter.py  # should print voltage / current / power

# Then run the full system
python main.py
# Open http://<pi-ip>:5000 and confirm all health LEDs are green
```

### Config / Env Differences Between Dev and Pi

| Setting | Dev value | Pi value | Where set |
|---|---|---|---|
| GPIO chip | N/A | `/dev/gpiochip4` (Pi 5) | `calibration/config.xml` |
| Mega serial port | N/A | `/dev/ttyACM0` | `calibration/config.xml` |
| GPS serial port | N/A | `/dev/ttyUSB0` | `calibration/config.xml` |
| CO2 sensor UART | N/A | `/dev/ttyAMA0` | hardcoded in `sensor/air.py` (known debt) |
| `USE_REAL_SENSORS` flag | `False` | `True` | top of `main.py` — edit before deploy |
```

---

## Commit Message Style

Use imperative mood, short subject line (≤ 72 chars), no trailing period:

```
Add CLAUDE.md for new project X
Update TODO list in herc.md after SQLite integration
Fix Key Conventions section in MGIT.md
Add Schema Reference for payroll DB
```

Do not use vague messages like "update", "fix stuff", or "changes".

---

## Quick Reference

```bash
# View all project briefs in this repo
ls *.md

# Copy a brief into a new project
cp herc.md ~/projects/new-project/CLAUDE.md

# Always activate the venv first (every session, every project)
source venv/bin/activate        # Linux / macOS / Raspberry Pi
venv\Scripts\activate           # Windows
```
