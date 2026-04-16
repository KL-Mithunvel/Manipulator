"""
core/kinematics.py

Shared kinematics utilities for all manipulator modules.
Functions take link lengths as explicit arguments — no hardcoded constants here.
"""

import math


def deg2rad(d: float) -> float:
    return d * math.pi / 180.0


def rad2deg(r: float) -> float:
    return r * 180.0 / math.pi


def safe_float(s: str, fallback: float) -> float:
    try:
        return float(str(s).strip())
    except Exception:
        return fallback


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def fk(
    th1_deg: float,
    th2_deg: float,
    th3_deg: float,
    base_xy: tuple[float, float],
    L1: float,
    L2: float,
    LB: float,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    """
    Forward kinematics for a planar RRR arm.

    Joint angles are measured in degrees, cumulative (absolute frame):
        p1 direction: th1
        p2 direction: th1 + th2
        pb direction: th1 + th2 + th3

    Returns (p0, p1, p2, pb) — base, joint1, joint2, end-effector — all in mm.
    """
    bx, by = base_xy
    th1 = deg2rad(th1_deg)
    th2 = deg2rad(th2_deg)
    th3 = deg2rad(th3_deg)

    x0, y0 = bx, by
    x1 = x0 + L1 * math.cos(th1)
    y1 = y0 + L1 * math.sin(th1)
    x2 = x1 + L2 * math.cos(th1 + th2)
    y2 = y1 + L2 * math.sin(th1 + th2)
    xb = x2 + LB * math.cos(th1 + th2 + th3)
    yb = y2 + LB * math.sin(th1 + th2 + th3)

    return (x0, y0), (x1, y1), (x2, y2), (xb, yb)


def ik(
    px: float,
    py: float,
    phi_deg: float,
    base_xy: tuple[float, float],
    L1: float,
    L2: float,
    LB: float,
) -> tuple[tuple[float, float, float] | None, tuple[float, float, float] | None]:
    """
    Geometric inverse kinematics for a planar RRR arm.

    Given:
        (px, py)  — target end-effector (bucket tip) position in mm
        phi_deg   — desired end-effector orientation (th1+th2+th3) in degrees
        base_xy   — base origin in mm
        L1, L2, LB — link lengths in mm

    Returns:
        (elbow_up, elbow_down)
        Each is (th1_deg, th2_deg, th3_deg) or None if that configuration
        is geometrically unreachable.

    Both solutions reach the same (px, py, phi) but with opposite elbow bend.
    """
    bx, by = base_xy
    phi = deg2rad(phi_deg)

    # Step back along bucket link to find wrist (joint 2) position
    wx = px - LB * math.cos(phi)
    wy = py - LB * math.sin(phi)

    # Wrist position relative to base
    dx = wx - bx
    dy = wy - by

    # Law of cosines: cos(th2)
    d_sq = dx * dx + dy * dy
    c2 = (d_sq - L1 * L1 - L2 * L2) / (2.0 * L1 * L2)

    # Outside reachable ring: both solutions impossible
    if abs(c2) > 1.0:
        return None, None

    s2_up = math.sqrt(1.0 - c2 * c2)   # elbow up: th2 > 0
    s2_down = -s2_up                    # elbow down: th2 < 0

    results = []
    for s2 in (s2_up, s2_down):
        th2 = math.atan2(s2, c2)
        th1 = math.atan2(dy, dx) - math.atan2(L2 * s2, L1 + L2 * c2)
        th3 = phi - th1 - th2
        results.append((rad2deg(th1), rad2deg(th2), rad2deg(th3)))

    return results[0], results[1]
