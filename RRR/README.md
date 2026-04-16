# RRR Manipulator — 3-Joint Planar Arm (Excavator / Digger)

This module implements the simulation, kinematics, and motion planning for a **3-revolute-joint (RRR) planar robotic arm** modelled after a compact excavator-style digger. The third joint carries a **bucket end-effector** used for digging — the arm's job is to systematically cover and excavate a defined rectangular target zone.

---

## What This Arm Does

The arm has three revolute joints in a 2D plane:

```
Base (fixed)
  └── Link 1 (L1) ── Joint 1 (θ1)
        └── Link 2 (L2) ── Joint 2 (θ2)
              └── Bucket link (LB) ── Joint 3 (θ3) ── [BUCKET]
```

- **θ1** — shoulder: rotates the whole arm from the base
- **θ2** — elbow: bends the second link relative to the first
- **θ3** — wrist/bucket: controls the bucket angle (digging attack angle)

The **yellow rectangle** shown on the canvas represents the **target dig zone** — the area the bucket must systematically cover during operation.

---

## Hardware — Servo & Motor Mapping

> **This section must be filled in before IK or Arduino code can be written.**
> Measure and record each servo's details from the physical build.

| Joint | Role | Servo Model | Mount Orientation | Zero Position | Range of Motion | Direction of +ve angle |
|-------|------|-------------|-------------------|---------------|-----------------|------------------------|
| θ1 | Shoulder (base rotation) | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| θ2 | Elbow | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| θ3 | Bucket / wrist | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**For each servo, record:**
- **Model** (e.g. MG996R, SG90, DS3225) — determines torque, PWM range, and pulse width mapping
- **PWM range** (e.g. 500µs–2500µs) — needed to convert angle → Arduino `servo.writeMicroseconds()`
- **Mount orientation** — which way is the servo horn pointing at its physical zero? Is servo zero = arm straight up, horizontal, or something else?
- **Mechanical zero vs software zero** — what physical angle corresponds to θ=0° in the simulation?
- **Positive direction** — does increasing PWM rotate the joint clockwise or counter-clockwise in the simulation frame?
- **Hard limits** — any physical stop or range restriction beyond the servo's rated travel

---

## Link Dimensions

> Confirm these against the physical arm. They are currently hardcoded — will move to `config.yaml`.

| Parameter | Current value | Physical measurement |
|-----------|--------------|----------------------|
| L1 (shoulder → elbow) | 140 mm | _confirm_ |
| L2 (elbow → wrist) | 140 mm | _confirm_ (sim_view.py incorrectly has 130mm — fix pending) |
| LB (wrist → bucket tip) | 55 mm | _confirm_ |

---

## Forward Kinematics (Implemented)

Given (θ1, θ2, θ3) in degrees and base position (bx, by):

```
p0 = (bx, by)                                              ← base
p1 = p0 + L1 · (cos θ1,        sin θ1)                    ← elbow
p2 = p1 + L2 · (cos(θ1+θ2),   sin(θ1+θ2))                ← wrist
pb = p2 + LB · (cos(θ1+θ2+θ3), sin(θ1+θ2+θ3))            ← bucket tip
```

**Files:**
- `sim_create.py` — interactive FK GUI (sliders, live canvas, pose save, CSV export)
- `sim_view.py` — animated playback of a saved pose CSV

---

## Inverse Kinematics (Planned)

**Goal:** given a target bucket-tip position (px, py) and bucket attack angle φ, solve for (θ1, θ2, θ3).

### Geometric solution

```
# Step 1: find wrist position by stepping back along the bucket link
wx = px - LB · cos(φ)
wy = py - LB · sin(φ)

# Step 2: two-link IK for (wx, wy) using L1 and L2
c2 = (wx² + wy² − L1² − L2²) / (2 · L1 · L2)
s2 = ±√(1 − c2²)        ← + = elbow up,  − = elbow down
θ2 = atan2(s2, c2)
θ1 = atan2(wy, wx) − atan2(L2·s2, L1 + L2·c2)
θ3 = φ − θ1 − θ2
```

**Both elbow-up and elbow-down solutions must be computed.** The GUI will let the user select which configuration to use, or automatically pick the one that keeps all joints within their limits.

**Implementation file (planned):** `RRR/ik_solver.py`

---

## Dig Zone Coverage (Planned)

The yellow box on the canvas is not just a visual reference — it is the **dig target zone**. The arm needs a motion plan that systematically covers the entire box with the bucket.

### Coverage strategy (to be designed)

The likely approach is a **raster/column sweep**:

```
For each column x in box (left → right, step = bucket_width):
    Move bucket to top of column   → IK solve → pose
    Drag bucket down to bottom     → IK solve → pose
    Lift and move to next column   → IK solve → pose
```

**What needs to be built:**

1. **Coverage path generator** — given box (x0, y0, w, h) and a step size, output a list of (px, py, φ) waypoints that cover the box.
2. **IK batch solve** — run IK on each waypoint, flag any point outside the reachable workspace.
3. **Reachability check** — before committing to a dig plan, visualise which parts of the box the arm can actually reach given its link lengths and joint limits.
4. **Pose sequence export** — convert the solved waypoints to a timestamped CSV compatible with `sim_view.py` for animation preview.

### Animation preview flow

```
Coverage path generator
        |
        v
   IK batch solve
        |
        v
  Pose CSV (time_s, th1, th2, th3)
        |
        v
   sim_view.py  →  animated preview
```

---

## Arduino Conversion (Future)

Once FK, IK, and coverage path generation are working and verified in simulation, the motion plan will be converted to Arduino servo commands.

**What this requires (to be detailed once servo specs are known):**

- Angle → PWM pulse width mapping per servo (using measured min/max µs values)
- Handling mechanical zero offset per joint
- Timing: how fast to move between poses (servo speed, ramp profile)
- Serial or hardcoded sequence — TBD based on whether the Arduino receives commands from a host or runs a stored program

**Target file (planned):** `RRR/arduino_export.py` — takes a pose CSV and outputs Arduino `.ino` sketch or `servo.writeMicroseconds()` call sequence.

---

## Files in This Module

| File | Status | Description |
|------|--------|-------------|
| `sim_create.py` | Working | FK GUI — interactive pose creation and CSV export |
| `sim_view.py` | Working (needs refactor) | Animated playback of pose CSV |
| `ik_solver.py` | Planned | Geometric IK solver for RRR |
| `coverage.py` | Planned | Dig zone path planner (raster sweep) |
| `arduino_export.py` | Future | Convert pose CSV to Arduino servo commands |
| `config.yaml` | Planned | Link lengths, joint limits, servo mappings |
| `data/arm_poses_5.csv` | Sample | Minimal 2-row sample pose data |

---

## Known Issues

See `CLAUDE.md` → Known Technical Debt for the full list. Key items:

- L2 inconsistency between `sim_create.py` (140mm) and `sim_view.py` (130mm) — **fix before any IK work**
- `fk()` duplicated in both files — extract to `core/kinematics.py`
- `sim_view.py` uses module-level globals — refactor to class before extending

---

## Immediate Next Steps

1. **Fill in the servo table above** — model, PWM range, mount orientation, mechanical zero, direction
2. **Confirm physical link lengths** against the table above
3. Fix L2 inconsistency and extract shared code to `core/`
4. Implement `ik_solver.py`
5. Build coverage path generator
6. Animate a full dig sequence in `sim_view.py`