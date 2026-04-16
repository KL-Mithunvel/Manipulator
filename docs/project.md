# Project Brief — Manipulator

**Last updated:** 2026-03-23
**Author:** KL Mithunvel (klm@smtw.in)

---

## What This Project Is

**Manipulator** is an interactive Python GUI toolkit for robot kinematics — specifically for visualising and computing **forward kinematics (FK)** and **inverse kinematics (IK)** of multi-joint robot arms in 2D.

The project is structured to be modular and reusable: each manipulator type (RRR, LLR, LOO, etc.) is its own module that shares a common core of kinematics utilities and a common GUI shell. The aim is to make it easy to drop in a new manipulator type without rewriting the interface or the maths infrastructure.

---

## Goals

1. **RRR manipulator** — complete, polished FK + IK GUI with pose sequencing, CSV export, and animated playback.
2. **Reusable core** — shared kinematics library (`core/kinematics.py`) so FK/IK logic is never duplicated.
3. **Config-driven** — link lengths, joint limits, and workspace parameters come from a YAML config, not hardcoded constants.
4. **Extensible** — a clean interface so LLR, LOO, RRP, and other types can be added as drop-in modules.
5. **Proper project hygiene** — `requirements.txt`, `tests/`, and a venv before any further features are built.

---

## Manipulator Types Planned

| Type | Joints | Notes | Status |
|------|--------|-------|--------|
| RRR | 3 revolute | Planar 2D | In progress |
| LLR | 2 prismatic + 1 revolute | Planar 2D | Planned |
| LOO | 1 prismatic + 2 ? | TBD — notation to be confirmed | Planned |
| RRP | 2 revolute + 1 prismatic | SCARA-like | Planned |

> **Note on notation:** R = revolute joint, L = linear (prismatic) joint. The meaning of O needs to be confirmed with the user before implementing LOO.

---

## Current State (as of 2026-03-23)

### Files

| File | What it does |
|------|-------------|
| `RRR/sim_create.py` | FK pose creator — interactive sliders and text inputs for θ1/θ2/θ3, live 2D canvas, configurable target box, pose save + CSV export |
| `RRR/sim_view.py` | Playback animator — loads a pose CSV, interpolates angles at any `t`, animates with Play/Pause/Scrub/Speed |
| `RRR/data/arm_poses_5.csv` | Minimal sample data (2 rows) |

### What works

- 2D planar FK for RRR is correctly implemented in `sim_create.py`
- The GUI in `sim_create.py` is well-structured (class-based `ArmGUI`)
- Slider ↔ textbox sync with lock guard works correctly
- Pose save + sorted CSV export works
- Playback interpolation (`np.interp`) in `sim_view.py` works
- Movable base origin and configurable yellow target box work in both files

### What is broken or missing

| # | Issue | Impact |
|---|-------|--------|
| 1 | L2 differs: `sim_create` = 140mm, `sim_view` = 130mm | Creates discrepancy between creator and viewer |
| 2 | `fk()`, `deg2rad()`, `safe_float()` duplicated in both files | DRY violation; changes must be made in two places |
| 3 | `sim_view.py` uses module-level globals, not a class | Hard to extend or test |
| 4 | CSV path hardcoded in `sim_view.py` | Breaks if run from a different working directory |
| 5 | Link lengths hardcoded in both files | Cannot change geometry without editing source code |
| 6 | No inverse kinematics | Core missing feature |
| 7 | No `requirements.txt` | Cannot reproduce environment |
| 8 | No `tests/` | No confidence in correctness |
| 9 | No shared interface for multi-manipulator extensibility | Cannot add LLR/LOO without restructuring |

---

## Target Architecture

```
Manipulator/
├── core/
│   ├── kinematics.py      # fk(), ik(), deg2rad(), safe_float() — shared by all manipulators
│   └── config.py          # load/save YAML config (link lengths, joint limits, etc.)
├── RRR/
│   ├── config.yaml        # L1, L2, LB, joint limits for RRR
│   ├── sim_create.py      # FK GUI — uses core/
│   ├── sim_view.py        # Playback — uses core/
│   └── ik_solver.py       # IK (geometric closed-form) — planned
├── LLR/                   # future module
├── LOO/                   # future module (notation TBC)
├── tests/
│   ├── test_rrr_fk.py     # FK correctness for known angles
│   └── test_rrr_ik.py     # IK round-trip: FK(IK(target)) ≈ target
├── docs/
│   └── project.md         # this file
├── claude/
│   ├── claude_to_do.md
│   └── claude_log.md
├── requirements.txt
├── README.md
└── CLAUDE.md
```

---

## RRR Kinematics — Reference

### Forward Kinematics (2D planar)

Given joint angles θ1, θ2, θ3 (degrees) and base position (bx, by):

```
p0 = (bx, by)
p1 = p0 + L1 * (cos θ1, sin θ1)
p2 = p1 + L2 * (cos(θ1+θ2), sin(θ1+θ2))
pb = p2 + LB * (cos(θ1+θ2+θ3), sin(θ1+θ2+θ3))
```

Returns four points: base, joint 1, joint 2, end-effector (bucket tip).

### Inverse Kinematics (planned — geometric)

Given target end-effector position (px, py) and orientation φ (degrees):

```
# Wrist position (subtract end-effector link)
wx = px - LB * cos(φ)
wy = py - LB * sin(φ)

# Two-link IK for (wx, wy) using L1, L2
c2 = (wx² + wy² - L1² - L2²) / (2 * L1 * L2)
s2 = ±sqrt(1 - c2²)   # elbow-up (+) or elbow-down (-)
θ2 = atan2(s2, c2)
θ1 = atan2(wy, wx) - atan2(L2*s2, L1 + L2*c2)
θ3 = φ - θ1 - θ2
```

Both elbow-up and elbow-down solutions should be offered in the GUI.

---

## Pose CSV Format

```
time_s,th1_deg,th2_deg,th3_deg
0.000,0.000,0.000,0.000
1.500,30.000,-45.000,10.000
```

- `time_s` — must be strictly increasing; no duplicate timestamps
- Angles in degrees
- Playback interpolates linearly between rows

---

## Open Questions

1. What does **O** stand for in LOO? (spherical joint? offset? other?)
2. Should the GUI eventually move from matplotlib widgets to **Tkinter**? (user preference per tech stack)
3. Should IK show both elbow-up and elbow-down solutions simultaneously, or let user toggle?
4. Is 2D-only sufficient for all planned manipulator types, or is 3D needed for any?
