"""
RRR Forward Kinematics — exam scratch
--------------------------------------
Sliders control joint angles. Plot updates live.

FK equations (planar 2D):
    p0 = base
    p1 = p0 + L1 * [cos(t1),          sin(t1)]
    p2 = p1 + L2 * [cos(t1+t2),       sin(t1+t2)]
    pb = p2 + L3 * [cos(t1+t2+t3),    sin(t1+t2+t3)]
"""

import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ── Link lengths (mm) ────────────────────────────────────────────────────────
L1 = 140.0
L2 = 140.0
L3 = 55.0   # end-effector (bucket) link


# ── Forward kinematics ───────────────────────────────────────────────────────
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


# ── Figure ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 7))
plt.subplots_adjust(bottom=0.30)
fig.canvas.manager.set_window_title("RRR Forward Kinematics")

R = (L1 + L2 + L3) * 1.1
ax.set_xlim(-R, R)
ax.set_ylim(-R, R)
ax.set_aspect("equal")
ax.grid(True)
ax.set_title("RRR — Forward Kinematics")

arm_line,   = ax.plot([], [], "o-", lw=3, color="steelblue")
end_line,   = ax.plot([], [], "o-", lw=3, color="tomato")
info        = ax.text(0.02, 0.98, "", transform=ax.transAxes,
                      va="top", ha="left", fontsize=9)


# ── Sliders ───────────────────────────────────────────────────────────────────
ax_t1 = plt.axes([0.15, 0.20, 0.70, 0.04])
ax_t2 = plt.axes([0.15, 0.13, 0.70, 0.04])
ax_t3 = plt.axes([0.15, 0.06, 0.70, 0.04])

s_t1 = Slider(ax_t1, "θ1 (deg)", -180, 180, valinit=45)
s_t2 = Slider(ax_t2, "θ2 (deg)", -180, 180, valinit=-30)
s_t3 = Slider(ax_t3, "θ3 (deg)", -180, 180, valinit=0)


# ── Update ────────────────────────────────────────────────────────────────────
def update(_):
    t1, t2, t3 = s_t1.val, s_t2.val, s_t3.val
    p0, p1, p2, pb = fk(t1, t2, t3)

    arm_line.set_data([p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]])
    end_line.set_data([p2[0], pb[0]],         [p2[1], pb[1]])

    info.set_text(
        f"θ1={t1:.1f}°   θ2={t2:.1f}°   θ3={t3:.1f}°\n"
        f"End-effector: ({pb[0]:.1f}, {pb[1]:.1f}) mm"
    )
    fig.canvas.draw_idle()


s_t1.on_changed(update)
s_t2.on_changed(update)
s_t3.on_changed(update)
update(None)

plt.show()
