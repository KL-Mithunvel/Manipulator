"""
RRR/ik_create.py

Inverse kinematics pose creator for the planar RRR arm.

Controls:
    px, py sliders / textboxes  — target end-effector (bucket tip) position
    φ slider / textbox          — desired end-effector orientation (th1+th2+th3)
    t slider / textbox          — time stamp for this pose
    Elbow UP / DOWN button      — toggle between the two IK solutions
    Base X / Base Y + Set Base  — move the arm base origin
    Yellow box controls         — reposition the dig target zone
    Save Pose                   — record current solved pose at time t
    Clear                       — wipe all saved poses
    Export CSV                  — write poses to arm_poses_export.csv (sim_view compatible)

Canvas:
    Solid coloured arm      — active IK solution
    Dashed grey arm         — alternate IK solution (shown when it exists)
    Red X marker            — target (px, py) point
    Yellow rectangle        — configurable dig target zone
    Info text               — live readout of solved angles and status
"""

import sys
import os
import csv
from dataclasses import dataclass

# Allow `from core.kinematics import ...` when run from the RRR/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.kinematics import fk, ik, safe_float, clamp

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from matplotlib.patches import Rectangle

# ── USER PARAMETERS ──────────────────────────────────────────────────────────
L1 = 140.0   # mm  shoulder → elbow
L2 = 140.0   # mm  elbow → wrist
LB = 55.0    # mm  wrist → bucket tip

TIME_MIN = 0.0
TIME_MAX = 60.0

BASE_X0 = 0.0   # mm
BASE_Y0 = 0.0   # mm

BOX_X0 = 120.0  # mm
BOX_Y0 = -60.0  # mm
BOX_W  = 80.0   # mm
BOX_H  = 60.0   # mm

# Target slider ranges (cover the full workspace with margin)
_REACH = L1 + L2 + LB          # 335 mm
PX_MIN, PX_MAX   = -_REACH, _REACH
PY_MIN, PY_MAX   = -_REACH, _REACH
PHI_MIN, PHI_MAX = -180.0, 180.0


# ── DATA ─────────────────────────────────────────────────────────────────────
@dataclass
class Pose:
    time_s: float
    th1: float
    th2: float
    th3: float


# ── GUI ───────────────────────────────────────────────────────────────────────
class IKArmGUI:
    def __init__(self):
        self.poses: list[Pose] = []
        self._lock = False
        self._elbow_up = True   # True → elbow-up solution active

        self.base_x = float(BASE_X0)
        self.base_y = float(BASE_Y0)

        self.box_x0 = float(BOX_X0)
        self.box_y0 = float(BOX_Y0)
        self.box_w  = float(BOX_W)
        self.box_h  = float(BOX_H)

        self.fig = plt.figure(figsize=(13, 7))
        self.fig.canvas.manager.set_window_title("RRR IK Creator")

        # ── PLOT (LEFT) ──────────────────────────────────────────────────────
        self.ax = self.fig.add_axes([0.05, 0.22, 0.62, 0.74])
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.grid(True)

        r = _REACH * 1.15
        self.ax.set_xlim(-r, r)
        self.ax.set_ylim(-r, r)

        # Active solution — solid
        (self.line_links,)  = self.ax.plot([], [], "o-", linewidth=3, zorder=3)
        (self.line_bucket,) = self.ax.plot([], [], "o-", linewidth=3, zorder=3)
        (self.base_marker,) = self.ax.plot([], [], "o", ms=10, zorder=4)

        # Alternate solution — dashed grey
        (self.line_links_alt,)  = self.ax.plot([], [], "o--", lw=1.5,
                                                color="grey", alpha=0.45, zorder=2)
        (self.line_bucket_alt,) = self.ax.plot([], [], "o--", lw=1.5,
                                                color="grey", alpha=0.45, zorder=2)

        # Target point
        (self.target_marker,) = self.ax.plot([], [], "rx", ms=13,
                                             markeredgewidth=2.5, zorder=5)

        self.info_txt = self.ax.text(
            0.02, 0.98, "", transform=self.ax.transAxes, va="top", ha="left",
            fontsize=9,
        )

        # Yellow dig-zone box
        self.target_box = Rectangle(
            (self.box_x0, self.box_y0), self.box_w, self.box_h,
            facecolor="yellow", edgecolor="goldenrod", alpha=0.35, lw=2,
        )
        self.ax.add_patch(self.target_box)

        # ── RIGHT PANEL ──────────────────────────────────────────────────────
        rx    = 0.72
        rw    = 0.26
        row_h = 0.045

        def row(y):
            return [rx, y, rw, row_h]

        # Target sliders
        self.s_px  = Slider(self.fig.add_axes(row(0.88)), "px (mm)",
                            PX_MIN, PX_MAX, valinit=200.0)
        self.s_py  = Slider(self.fig.add_axes(row(0.82)), "py (mm)",
                            PY_MIN, PY_MAX, valinit=0.0)
        self.s_phi = Slider(self.fig.add_axes(row(0.76)), "φ (deg)",
                            PHI_MIN, PHI_MAX, valinit=0.0)
        self.s_t   = Slider(self.fig.add_axes(row(0.70)), "t (s)",
                            TIME_MIN, TIME_MAX, valinit=0.0)

        for s in (self.s_px, self.s_py, self.s_phi, self.s_t):
            s.on_changed(self.update)

        # Two-column textbox layout (same proportions as sim_create)
        col1_x = rx
        col2_x = rx + rw * 0.52
        col_w  = rw * 0.48
        tb_h   = 0.045

        def tb(colx, y):
            return [colx, y, col_w, tb_h]

        # Left column: target inputs + time
        self.tb_px  = TextBox(self.fig.add_axes(tb(col1_x, 0.63)), "px",  initial="200.0")
        self.tb_py  = TextBox(self.fig.add_axes(tb(col1_x, 0.57)), "py",  initial="0.0")
        self.tb_phi = TextBox(self.fig.add_axes(tb(col1_x, 0.51)), "φ",   initial="0.0")
        self.tb_t   = TextBox(self.fig.add_axes(tb(col1_x, 0.45)), "t",   initial="0.0")

        # Right column: base position
        self.tb_base_x = TextBox(self.fig.add_axes(tb(col2_x, 0.63)), "Base X",
                                 initial=str(BASE_X0))
        self.tb_base_y = TextBox(self.fig.add_axes(tb(col2_x, 0.57)), "Base Y",
                                 initial=str(BASE_Y0))

        for tbx in (self.tb_px, self.tb_py, self.tb_phi, self.tb_t):
            tbx.on_submit(lambda _: self._apply_textboxes())

        self.b_set_base = Button(
            self.fig.add_axes([col2_x, 0.51, col_w, tb_h]), "Set Base"
        )
        self.b_set_base.on_clicked(self.set_base)

        # Yellow box controls
        self.tb_box_x0 = TextBox(self.fig.add_axes(tb(col1_x, 0.39)), "Box X0",
                                 initial=str(BOX_X0))
        self.tb_box_y0 = TextBox(self.fig.add_axes(tb(col2_x, 0.39)), "Box Y0",
                                 initial=str(BOX_Y0))
        self.tb_box_w  = TextBox(self.fig.add_axes(tb(col1_x, 0.33)), "Box W",
                                 initial=str(BOX_W))
        self.tb_box_h  = TextBox(self.fig.add_axes(tb(col2_x, 0.33)), "Box H",
                                 initial=str(BOX_H))

        self.b_set_box = Button(self.fig.add_axes([rx, 0.27, rw, 0.05]), "Set Yellow Box")
        self.b_set_box.on_clicked(self.set_yellow_box)

        # Elbow toggle
        self.b_elbow = Button(self.fig.add_axes([rx, 0.20, rw, 0.055]), "Elbow: UP")
        self.b_elbow.on_clicked(self.toggle_elbow)

        # Pose buttons
        b_w = (rw - 0.02) / 2
        self.b_save  = Button(self.fig.add_axes([rx,              0.12, b_w, 0.06]),
                              "Save Pose")
        self.b_clear = Button(self.fig.add_axes([rx + b_w + 0.02, 0.12, b_w, 0.06]),
                              "Clear")
        self.b_export = Button(self.fig.add_axes([rx, 0.04, rw, 0.06]), "Export CSV")

        self.b_save.on_clicked(self.save_pose)
        self.b_clear.on_clicked(self.clear_poses)
        self.b_export.on_clicked(self.export_csv)

        # ── POSE LIST (BOTTOM LEFT) ───────────────────────────────────────────
        self.pose_box  = self.fig.add_axes([0.05, 0.03, 0.62, 0.16])
        self.pose_box.axis("off")
        self.pose_text = self.pose_box.text(0, 1, "", va="top", family="monospace")

        self.update(None)

    # ── HELPERS ──────────────────────────────────────────────────────────────

    def _solve(self):
        """Return (active, alt, sol_up, sol_down).  Each solution is
        (th1_deg, th2_deg, th3_deg) or None."""
        sol_up, sol_down = ik(
            self.s_px.val, self.s_py.val, self.s_phi.val,
            base_xy=(self.base_x, self.base_y),
            L1=L1, L2=L2, LB=LB,
        )
        if self._elbow_up:
            return sol_up, sol_down, sol_up, sol_down
        else:
            return sol_down, sol_up, sol_up, sol_down

    def _apply_textboxes(self):
        if self._lock:
            return
        self._lock = True
        try:
            self.s_px.set_val(
                clamp(safe_float(self.tb_px.text,  self.s_px.val),  PX_MIN,  PX_MAX))
            self.s_py.set_val(
                clamp(safe_float(self.tb_py.text,  self.s_py.val),  PY_MIN,  PY_MAX))
            self.s_phi.set_val(
                clamp(safe_float(self.tb_phi.text, self.s_phi.val), PHI_MIN, PHI_MAX))
            self.s_t.set_val(
                clamp(safe_float(self.tb_t.text,   self.s_t.val),   TIME_MIN, TIME_MAX))
        finally:
            self._lock = False

    def _sync_textboxes(self):
        if self._lock:
            return
        self._lock = True
        try:
            self.tb_px.set_val(f"{self.s_px.val:.2f}")
            self.tb_py.set_val(f"{self.s_py.val:.2f}")
            self.tb_phi.set_val(f"{self.s_phi.val:.2f}")
            self.tb_t.set_val(f"{self.s_t.val:.3f}")
        finally:
            self._lock = False

    # ── BUTTON CALLBACKS ─────────────────────────────────────────────────────

    def set_base(self, _):
        self.base_x = safe_float(self.tb_base_x.text, self.base_x)
        self.base_y = safe_float(self.tb_base_y.text, self.base_y)
        self.update(None)

    def set_yellow_box(self, _):
        self.box_x0 = safe_float(self.tb_box_x0.text, self.box_x0)
        self.box_y0 = safe_float(self.tb_box_y0.text, self.box_y0)
        self.box_w  = max(0.0, safe_float(self.tb_box_w.text, self.box_w))
        self.box_h  = max(0.0, safe_float(self.tb_box_h.text, self.box_h))
        self.target_box.set_xy((self.box_x0, self.box_y0))
        self.target_box.set_width(self.box_w)
        self.target_box.set_height(self.box_h)
        self.update(None)

    def toggle_elbow(self, _):
        self._elbow_up = not self._elbow_up
        self.b_elbow.label.set_text("Elbow: UP" if self._elbow_up else "Elbow: DOWN")
        self.update(None)

    def save_pose(self, _):
        active, _, _, _ = self._solve()
        if active is None:
            return   # no solution — silently ignore
        th1, th2, th3 = active
        self.poses.append(Pose(
            time_s=float(self.s_t.val),
            th1=th1, th2=th2, th3=th3,
        ))
        self.update(None)

    def clear_poses(self, _):
        self.poses.clear()
        self.update(None)

    def export_csv(self, _):
        if not self.poses:
            return
        poses = sorted(self.poses, key=lambda p: p.time_s)
        with open("arm_poses_export.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time_s", "th1_deg", "th2_deg", "th3_deg"])
            for p in poses:
                w.writerow([
                    f"{p.time_s:.3f}",
                    f"{p.th1:.3f}",
                    f"{p.th2:.3f}",
                    f"{p.th3:.3f}",
                ])
        print("Exported: arm_poses_export.csv")

    # ── MAIN UPDATE ──────────────────────────────────────────────────────────

    def update(self, _):
        self._sync_textboxes()

        px  = self.s_px.val
        py  = self.s_py.val
        phi = self.s_phi.val
        t   = self.s_t.val

        # Always draw the target marker
        self.target_marker.set_data([px], [py])

        active, alt, _up, _down = self._solve()

        if active is None:
            # Both solutions unreachable — clear arm lines
            for ln in (self.line_links, self.line_bucket,
                       self.line_links_alt, self.line_bucket_alt):
                ln.set_data([], [])
            self.base_marker.set_data([], [])
            self.info_txt.set_text(
                f"px={px:.1f}  py={py:.1f}  φ={phi:.1f}°\n"
                f"t = {t:.3f} s\n"
                f"Base = ({self.base_x:.1f}, {self.base_y:.1f}) mm\n"
                f"Saved poses: {len(self.poses)}\n"
                "⚠ NO SOLUTION — target unreachable"
            )
            self._update_pose_list()
            self.fig.canvas.draw_idle()
            return

        # ── Draw active solution (solid) ────────────────────────────────────
        th1, th2, th3 = active
        p0, p1, p2, pb = fk(th1, th2, th3,
                             base_xy=(self.base_x, self.base_y),
                             L1=L1, L2=L2, LB=LB)
        self.line_links.set_data( [p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]])
        self.line_bucket.set_data([p2[0], pb[0]],         [p2[1], pb[1]])
        self.base_marker.set_data([p0[0]], [p0[1]])

        # ── Draw alternate solution (dashed grey) ───────────────────────────
        if alt is not None:
            at1, at2, at3 = alt
            q0, q1, q2, qb = fk(at1, at2, at3,
                                 base_xy=(self.base_x, self.base_y),
                                 L1=L1, L2=L2, LB=LB)
            self.line_links_alt.set_data( [q0[0], q1[0], q2[0]], [q0[1], q1[1], q2[1]])
            self.line_bucket_alt.set_data([q2[0], qb[0]],         [q2[1], qb[1]])
        else:
            self.line_links_alt.set_data([], [])
            self.line_bucket_alt.set_data([], [])

        elbow_label = "UP" if self._elbow_up else "DOWN"
        alt_note    = "" if alt is not None else "  (only one solution)"
        self.info_txt.set_text(
            f"px={px:.1f}  py={py:.1f}  φ={phi:.1f}°\n"
            f"θ1={th1:.1f}°  θ2={th2:.1f}°  θ3={th3:.1f}°\n"
            f"Elbow: {elbow_label}{alt_note}   t = {t:.3f} s\n"
            f"Base = ({self.base_x:.1f}, {self.base_y:.1f}) mm\n"
            f"Saved poses: {len(self.poses)}"
        )

        self._update_pose_list()
        self.fig.canvas.draw_idle()

    def _update_pose_list(self):
        if not self.poses:
            self.pose_text.set_text(
                "Saved Poses: (none)\n"
                "Meaning of time:\n"
                "- t is the exact time when this pose must be reached.\n"
                "- Playback will interpolate between poses."
            )
            return
        poses = sorted(self.poses, key=lambda p: p.time_s)[-10:]
        lines = [" time(s) |  θ1   θ2   θ3"]
        for p in poses:
            lines.append(f"{p.time_s:7.2f} | {p.th1:5.1f} {p.th2:5.1f} {p.th3:5.1f}")
        self.pose_text.set_text("\n".join(lines))


if __name__ == "__main__":
    IKArmGUI()
    plt.show()
