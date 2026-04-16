# Manipulator — Robot Kinematics GUI Toolkit

A Python-based interactive GUI toolkit for visualising and computing **forward and inverse kinematics** of robot manipulators. Built for learning, experimentation, and motion planning — starting with the planar **RRR** (3-revolute-joint) configuration and designed to expand to other manipulator types.

---

## What It Does

- **Forward Kinematics** — set joint angles via sliders or text inputs and see the manipulator update in real time on a 2D canvas.
- **Pose Sequencing** — record poses with timestamps and export them to CSV for playback.
- **Playback & Animation** — load a pose CSV and scrub or animate through the motion sequence with speed control.
- **Configurable Workspace** — move the base origin and define a target zone (yellow box) directly from the GUI.

---

## Manipulator Types

| Type | Status |
|------|--------|
| RRR (3-revolute, planar 2D) | In progress |
| LLR, LOO, and others | Planned |

---

## Project Structure

```
Manipulator/
├── RRR/
│   ├── sim_create.py     # FK pose creator — interactive joint control + CSV export
│   ├── sim_view.py       # Pose playback — animate a saved CSV sequence
│   └── data/
│       └── arm_poses_5.csv   # Sample pose data
├── docs/
│   └── project.md        # Full project brief and design document
├── README.md
└── CLAUDE.md
```

---

## Getting Started

```bash
# 1. Clone the repo
git clone <repo-url>
cd Manipulator

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the FK pose creator
python RRR/sim_create.py

# 5. Run the playback viewer (point it at your exported CSV)
python RRR/sim_view.py
```

---

## Author

**KL Mithunvel** — [klm@smtw.in](mailto:klm@smtw.in)