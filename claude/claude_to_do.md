# Claude To-Do

Tracks all pending and in-progress work. Updated every session.

Legend: 🔴 Bug / rule violation | 🟡 In progress | 🟢 Not started | ✅ Done

---

## CRITICAL

- 🔴 Fix L2 inconsistency — `sim_create.py` uses L2=140mm, `sim_view.py` uses L2=130mm

## HIGH

- 🔴 Extract duplicated `fk()`, `deg2rad()`, `safe_float()` into `core/kinematics.py`
- 🔴 Move all link lengths and joint limits out of source files into `RRR/config.yaml`
- 🟢 Refactor `sim_view.py` from module-level globals to a class (match `ArmGUI` pattern)

## MEDIUM

- 🟢 Replace hardcoded CSV path in `sim_view.py` with CLI argument or file dialog
- 🟢 Create `requirements.txt` (matplotlib, numpy)
- 🟢 Create `tests/` with FK correctness tests for known angle inputs

## NOT STARTED

- 🟢 Implement standalone `RRR/ik_solver.py` (pure solver, no GUI)
- 🟢 Show both elbow-up and elbow-down IK solutions (confirm with user which is preferred)
- 🟢 Workspace reachability visualisation (plot reachable region on canvas)
- 🟢 Design shared manipulator interface (`core/base.py`) for multi-type extensibility
- 🟢 LLR manipulator module
- 🟢 LOO manipulator module (clarify joint notation with user first)
- 🟢 Migrate GUI from matplotlib widgets to Tkinter (per tech stack preference)

## DONE

- ✅ Write `docs/project.md` — full project brief
- ✅ Update `CLAUDE.md` to project-specific format
- ✅ Write proper `README.md` with welcome, structure, and getting started