"""
RRR Inverse Kinematics — exam scratch
--------------------------------------
Sliders control the target position (px, py) and end-effector angle (phi).
IK solves for joint angles. Both elbow-up and elbow-down solutions are shown.

IK equations (geometric):
    1. Find wrist position by stepping back along end-effector link:
           wx = px - L3*cos(phi)
           wy = py - L3*sin(phi)

    2. Two-link IK for (wx, wy) using L1 and L2 (law of cosines):
           c2 = (wx² + wy² - L1² - L2²) / (2·L1·L2)
           s2 = ±sqrt(1 - c2²)          ← + elbow-up, − elbow-down
           t2 = atan2(s2, c2)
           t1 = atan2(wy, wx) - atan2(L2·s2, L1 + L2·c2)
           t3 = phi - t1 - t2
"""

import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# ── Link lengths (mm) ────────────────────────────────────────────────────────
L1 = 140.0
L2 = 140.0
L3 = 55.0

REACH = L1 + L2 + L3   # max reach = 335 mm


# ── Forward kinematics (for drawing) ─────────────────────────────────────────
def fk(t1_deg, t2_deg, t3_deg):
    t1 = math.radians(t1_deg)
    t2 = math.radians(t2_deg)
    t3 = math.radians(t3_deg)
    x0, y0 = 0.0, 0.0
    x1 = x0 + L1 * math.cos(t1)
    y1 = y0 + L1 * math.sin(t1)
    x2 = x1 + L2 * math.cos(t1 + t2)
    y2 = y1 + L2 * math.sin(t1 + t2)
    xb = x2 + L3 * math.cos(t1 + t2 + t3)
    yb = y2 + L3 * math.sin(t1 + t2 + t3)
    return (x0, y0), (x1, y1), (x2, y2), (xb, yb)


# ── Inverse kinematics ────────────────────────────────────────────────────────
def ik(px, py, phi_deg):
    """
    Returns (elbow_up, elbow_down).
    Each is (t1_deg, t2_deg, t3_deg) or None if unreachable.
    """
    phi = math.radians(phi_deg)

    # Wrist position
    wx = px - L3 * math.cos(phi)
    wy = py - L3 * math.sin(phi)

    # Law of cosines
    c2 = (wx**2 + wy**2 - L1**2 - L2**2) / (2 * L1 * L2)
    if abs(c2) > 1.0:
        return None, None   # outside reachable workspace

    s2_up   =  math.sqrt(1 - c2**2)
    s2_down = -s2_up

    solutions = []
    for s2 in (s2_up, s2_down):
        t2 = math.atan2(s2, c2)
        t1 = math.atan2(wy, wx) - math.atan2(L2 * s2, L1 + L2 * c2)
        t3 = phi - t1 - t2
        solutions.append((math.degrees(t1), math.degrees(t2), math.degrees(t3)))

    return solutions[0], solutions[1]


# ── State ─────────────────────────────────────────────────────────────────────
elbow_up = [True]   # mutable so the button callback can modify it


# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 7))
plt.subplots_adjust(bottom=0.32, right=0.78)
fig.canvas.manager.set_window_title("RRR Inverse Kinematics")

R = REACH * 1.1
ax.set_xlim(-R, R)
ax.set_ylim(-R, R)
ax.set_aspect("equal")
ax.grid(True)
ax.set_title("RRR — Inverse Kinematics")

# Active solution (solid)
arm_line,   = ax.plot([], [], "o-", lw=3, color="steelblue", zorder=3)
end_line,   = ax.plot([], [], "o-", lw=3, color="tomato",    zorder=3)

# Alternate solution (dashed grey)
arm_alt,    = ax.plot([], [], "o--", lw=1.5, color="grey", alpha=0.45, zorder=2)
end_alt,    = ax.plot([], [], "o--", lw=1.5, color="grey", alpha=0.45, zorder=2)

# Target marker
target_pt,  = ax.plot([], [], "rx", ms=13, markeredgewidth=2.5, zorder=5)

info = ax.text(0.02, 0.98, "", transform=ax.transAxes,
               va="top", ha="left", fontsize=9)


# ── Sliders ───────────────────────────────────────────────────────────────────
ax_px  = plt.axes([0.12, 0.22, 0.60, 0.04])
ax_py  = plt.axes([0.12, 0.15, 0.60, 0.04])
ax_phi = plt.axes([0.12, 0.08, 0.60, 0.04])

s_px  = Slider(ax_px,  "px (mm)", -REACH, REACH, valinit=200.0)
s_py  = Slider(ax_py,  "py (mm)", -REACH, REACH, valinit=0.0)
s_phi = Slider(ax_phi, "φ (deg)", -180.0, 180.0, valinit=0.0)

# Elbow toggle button
ax_btn = plt.axes([0.80, 0.50, 0.17, 0.06])
btn_elbow = Button(ax_btn, "Elbow: UP")


# ── Draw helper ───────────────────────────────────────────────────────────────
def draw_arm(line, eline, sol):
    if sol is None:
        line.set_data([], [])
        eline.set_data([], [])
        return
    p0, p1, p2, pb = fk(*sol)
    line.set_data( [p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]])
    eline.set_data([p2[0], pb[0]],         [p2[1], pb[1]])


# ── Update ────────────────────────────────────────────────────────────────────
def update(_):
    px, py, phi = s_px.val, s_py.val, s_phi.val
    sol_up, sol_down = ik(px, py, phi)

    active = sol_up if elbow_up[0] else sol_down
    alt    = sol_down if elbow_up[0] else sol_up

    target_pt.set_data([px], [py])
    draw_arm(arm_line, end_line, active)
    draw_arm(arm_alt,  end_alt,  alt)

    if active is None:
        info.set_text(
            f"px={px:.1f}  py={py:.1f}  φ={phi:.1f}°\n"
            "NO SOLUTION — target unreachable"
        )
    else:
        t1, t2, t3 = active
        elbow_label = "UP" if elbow_up[0] else "DOWN"
        info.set_text(
            f"px={px:.1f}  py={py:.1f}  φ={phi:.1f}°\n"
            f"θ1={t1:.1f}°   θ2={t2:.1f}°   θ3={t3:.1f}°\n"
            f"Elbow: {elbow_label}"
        )

    fig.canvas.draw_idle()


def toggle_elbow(_):
    elbow_up[0] = not elbow_up[0]
    btn_elbow.label.set_text("Elbow: UP" if elbow_up[0] else "Elbow: DOWN")
    update(None)


s_px.on_changed(update)
s_py.on_changed(update)
s_phi.on_changed(update)
btn_elbow.on_clicked(toggle_elbow)
update(None)

plt.show()
