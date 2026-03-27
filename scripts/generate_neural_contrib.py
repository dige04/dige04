#!/usr/bin/env python3
"""
Generate a neural network activation animation SVG from GitHub contribution data.

The animation shows neural network layers activating with signals
that converge into the contribution grid, illuminating cell borders
with a spreading glow effect.

Animation loop (8s):
  0-2s  : NN nodes pulse, connections glow layer by layer
  2-5s  : Light sweeps across grid edges (left -> right)
  5-7s  : Full contribution graph revealed
  7-8s  : Fade out, loop
"""

import json
import math
import os
import random
import urllib.request

# -- Configuration ------------------------------------------------------------

GITHUB_USER = os.environ.get("GITHUB_USER", "dige04")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# -- Grid parameters -----------------------------------------------------------

CELL_SIZE = 16
CELL_GAP = 4
CELL_STRIDE = CELL_SIZE + CELL_GAP
CELL_RADIUS = 3
COLS = 52  # weeks
ROWS = 7   # days

# -- Layout --------------------------------------------------------------------

NN_MARGIN_LEFT = 35
NN_WIDTH = 180
GAP_NN_GRID = 50
GRID_X = NN_MARGIN_LEFT + NN_WIDTH + GAP_NN_GRID
GRID_Y = 50
GRID_W = COLS * CELL_STRIDE
GRID_H = ROWS * CELL_STRIDE
SVG_W = GRID_X + GRID_W + 30
SVG_H = GRID_Y + GRID_H + 55

# -- Neural network layers ----------------------------------------------------

NN_LAYERS = [
    {"count": 3, "x_frac": 0.0},    # Input
    {"count": 5, "x_frac": 0.45},   # Hidden
    {"count": 7, "x_frac": 1.0},    # Output (maps to 7 grid rows)
]
NODE_R = 7

# -- Colors (tokyonight-inspired) ---------------------------------------------

BG = "#1a1b27"
GRID_EMPTY = "#1e2030"
NODE_DIM = "#2a2e42"
LIGHTNING = "#7dcfff"
NODE_GLOW = "#bb9af7"
SUBTITLE = "#565f89"
EDGE_COLOR = "#7dcfff"

CONTRIB_COLORS = {
    0: "#1e2030",
    1: "#1a3a5c",
    2: "#2560a0",
    3: "#4a90e2",
    4: "#7aa2f7",
}

# -- Animation timing ----------------------------------------------------------

CYCLE = 8  # seconds


# ==============================================================================
# Data fetching
# ==============================================================================


def fetch_contributions(user: str, token: str) -> dict:
    """Fetch contribution calendar via GitHub GraphQL API."""
    query = """
    query($user: String!) {
        user(login: $user) {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            contributionCount
                            date
                            weekday
                        }
                    }
                }
            }
        }
    }
    """
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps({"query": query, "variables": {"user": user}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except Exception as e:
        print(f"Warning: Could not fetch contributions ({e}). Using mock data.")
        return _mock_data()


def _mock_data() -> dict:
    random.seed(42)
    weeks = []
    for _ in range(52):
        days = []
        for d in range(7):
            c = random.choice([0, 0, 0, 0, 1, 1, 2, 3, 0, 0, 1, 4, 0])
            days.append({"contributionCount": c, "weekday": d})
        weeks.append({"contributionDays": days})
    return {"totalContributions": 247, "weeks": weeks}


def _level(count: int) -> int:
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 10:
        return 3
    return 4


# ==============================================================================
# SVG generation helpers
# ==============================================================================


def _node_positions() -> list[list[tuple[float, float]]]:
    """Return [[(x, y), ...], ...] for each NN layer."""
    positions = []
    for li, layer in enumerate(NN_LAYERS):
        n = layer["count"]
        x = NN_MARGIN_LEFT + layer["x_frac"] * NN_WIDTH
        if li == len(NN_LAYERS) - 1 and n == ROWS:
            positions.append([
                (x, GRID_Y + r * CELL_STRIDE + CELL_SIZE / 2) for r in range(ROWS)
            ])
        else:
            spacing = GRID_H / (n + 1)
            positions.append([(x, GRID_Y + spacing * (i + 1)) for i in range(n)])
    return positions


def _build_defs() -> str:
    return f"""<defs>
  <filter id="gN" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="gL" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feColorMatrix in="b" type="matrix"
      values="0 0 0 0 0.49
              0 0 0 0 0.81
              0 0 0 0 1
              0 0 0 1.8 0" result="cb"/>
    <feMerge><feMergeNode in="cb"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="gC" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="gE" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2" result="b"/>
    <feColorMatrix in="b" type="matrix"
      values="0 0 0 0 0.49
              0 0 0 0 0.81
              0 0 0 0 1
              0 0 0 2 0" result="cb"/>
    <feMerge><feMergeNode in="cb"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""


def _build_styles(grid: list[list[int]]) -> str:
    s = f"""<style>
@keyframes np{{
  0%,100%{{r:{NODE_R};opacity:.25}}
  50%{{r:{NODE_R+3};opacity:1}}
}}
@keyframes ng{{
  0%,100%{{opacity:0}}
  30%,70%{{opacity:.55}}
  50%{{opacity:1}}
}}
@keyframes ca{{
  0%,15%{{stroke:{NODE_DIM};opacity:.12}}
  35%,65%{{stroke:{LIGHTNING};opacity:.8}}
  85%,100%{{stroke:{NODE_DIM};opacity:.12}}
}}
@keyframes bf{{
  0%{{opacity:0}}
  15%{{opacity:.7}}
  85%{{opacity:.7}}
  100%{{opacity:0}}
}}
@keyframes gc{{
  0%,18%{{opacity:.08}}
  35%{{opacity:1;filter:url(#gC)}}
  55%,78%{{opacity:.85;filter:none}}
  92%,100%{{opacity:.08}}
}}
@keyframes ge{{
  0%,100%{{opacity:.18}}
  50%{{opacity:.28}}
}}
@keyframes eg{{
  0%,15%{{stroke-opacity:0}}
  30%{{stroke-opacity:.9;stroke:{EDGE_COLOR}}}
  50%{{stroke-opacity:.5;stroke:{EDGE_COLOR}}}
  70%,100%{{stroke-opacity:0}}
}}
"""

    for li, layer in enumerate(NN_LAYERS):
        d = li * 0.6
        s += f".nl{li}{{animation:np {CYCLE}s {d:.1f}s ease-in-out infinite}}\n"
        s += f".gl{li}{{animation:ng {CYCLE}s {d:.1f}s ease-in-out infinite}}\n"

    for li in range(len(NN_LAYERS) - 1):
        d = li * 0.6 + 0.3
        s += f".cl{li}{{animation:ca {CYCLE}s {d:.1f}s ease-in-out infinite}}\n"

    for r in range(ROWS):
        d = 1.5 + r * 0.1
        s += f".br{r}{{animation:bf {CYCLE}s {d:.1f}s ease-in-out infinite}}\n"

    for c in range(COLS):
        d = 2.0 + c * 0.055
        s += f".gc{c}{{animation:gc {CYCLE}s {d:.2f}s ease-in-out infinite}}\n"

    for c in range(COLS):
        d = 1.8 + c * 0.055
        s += f".eg{c}{{animation:eg {CYCLE}s {d:.2f}s ease-in-out infinite}}\n"

    s += "</style>"
    return s


# ==============================================================================
# SVG component builders
# ==============================================================================


def _build_nn_nodes(positions: list[list[tuple]]) -> str:
    parts = ["<!-- NN Nodes -->"]
    for li, layer in enumerate(positions):
        for x, y in layer:
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="{NODE_R+4}" '
                f'fill="{LIGHTNING}" opacity="0" class="gl{li}" filter="url(#gN)"/>'
            )
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="{NODE_R}" '
                f'fill="{NODE_DIM}" class="nl{li}"/>'
            )
    labels = ["IN", "H1", "OUT"]
    for li, layer in enumerate(positions):
        lx = NN_MARGIN_LEFT + NN_LAYERS[li]["x_frac"] * NN_WIDTH
        parts.append(
            f'<text x="{lx}" y="{GRID_Y + GRID_H + 22}" '
            f'font-family="\'Fira Code\',monospace" font-size="9" '
            f'fill="{SUBTITLE}" text-anchor="middle" opacity=".45">{labels[li]}</text>'
        )
    return "\n".join(parts)


def _build_nn_connections(positions: list[list[tuple]]) -> str:
    parts = ["<!-- NN Connections (fully connected) -->"]
    for li in range(len(positions) - 1):
        cur, nxt = positions[li], positions[li + 1]
        for i, (x1, y1) in enumerate(cur):
            for j, (x2, y2) in enumerate(nxt):
                mx = (x1 + x2) / 2
                parts.append(
                    f'<path d="M{x1:.0f},{y1:.0f} Q{mx:.0f},{(y1+y2)/2:.0f} {x2:.0f},{y2:.0f}" '
                    f'fill="none" stroke="{NODE_DIM}" stroke-width=".7" '
                    f'opacity=".12" class="cl{li}" filter="url(#gL)"/>'
                )
    return "\n".join(parts)


def _build_beams(positions: list[list[tuple]]) -> str:
    parts = ["<!-- Activation Beams -->"]
    output = positions[-1]
    for r in range(min(ROWS, len(output))):
        ox, oy = output[r]
        gy = GRID_Y + r * CELL_STRIDE + CELL_SIZE / 2
        parts.append(
            f'<line x1="{ox + NODE_R + 2:.0f}" y1="{oy:.0f}" '
            f'x2="{GRID_X:.0f}" y2="{gy:.0f}" '
            f'stroke="{LIGHTNING}" stroke-width="1.5" fill="none" '
            f'opacity="0" class="br{r}" filter="url(#gL)"/>'
        )
    return "\n".join(parts)


def _build_grid(grid: list[list[int]]) -> str:
    parts = ["<!-- Contribution Grid -->"]
    for c in range(min(len(grid), COLS)):
        for r in range(min(len(grid[c]), ROWS)):
            lv = grid[c][r]
            x = GRID_X + c * CELL_STRIDE
            y = GRID_Y + r * CELL_STRIDE
            color = CONTRIB_COLORS[lv]
            if lv > 0:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                    f'rx="{CELL_RADIUS}" fill="{color}" opacity=".08" class="gc{c}"/>'
                )
            else:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                    f'rx="{CELL_RADIUS}" fill="{GRID_EMPTY}" class="ge" '
                    f'style="animation:ge 6s ease-in-out infinite"/>'
                )
    return "\n".join(parts)


def _build_edge_glow(grid: list[list[int]]) -> str:
    parts = ["<!-- Edge Glow -->"]
    for c in range(min(len(grid), COLS)):
        for r in range(min(len(grid[c]), ROWS)):
            lv = grid[c][r]
            x = GRID_X + c * CELL_STRIDE
            y = GRID_Y + r * CELL_STRIDE
            if lv > 0:
                sw = 1.0 + lv * 0.3
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                    f'rx="{CELL_RADIUS}" fill="none" '
                    f'stroke="{EDGE_COLOR}" stroke-width="{sw:.1f}" stroke-opacity="0" '
                    f'class="eg{c}" filter="url(#gE)"/>'
                )
            else:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                    f'rx="{CELL_RADIUS}" fill="none" '
                    f'stroke="{EDGE_COLOR}" stroke-width="0.6" stroke-opacity="0" '
                    f'class="eg{c}"/>'
                )
    return "\n".join(parts)


# ==============================================================================
# Main SVG assembly
# ==============================================================================


def generate_svg(calendar: dict) -> str:
    grid: list[list[int]] = []
    for week in calendar["weeks"]:
        col = [_level(d["contributionCount"]) for d in week["contributionDays"]]
        grid.append(col)
    while len(grid) < COLS:
        grid.append([0] * ROWS)

    pos = _node_positions()

    return "\n".join([
        f'<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg">',
        _build_styles(grid),
        _build_defs(),
        f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG}" rx="12"/>',
        f'<text x="{SVG_W/2:.0f}" y="32" font-family="\'Fira Code\',monospace" '
        f'font-size="12" fill="{SUBTITLE}" text-anchor="middle" opacity=".55">'
        f'neural activation \u00b7 contribution graph</text>',
        _build_nn_connections(pos),
        _build_nn_nodes(pos),
        _build_beams(pos),
        _build_grid(grid),
        _build_edge_glow(grid),
        "</svg>",
    ])


# ==============================================================================
# Entry point
# ==============================================================================


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "dist")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Fetching contributions for {GITHUB_USER}...")
    cal = fetch_contributions(GITHUB_USER, GITHUB_TOKEN)
    total = cal.get("totalContributions", "?")
    print(f"Total contributions: {total}")

    print("Generating SVG...")
    svg = generate_svg(cal)

    path = os.path.join(out_dir, "github-neural-contrib.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Done: {path} ({len(svg):,} bytes)")

    dark_path = os.path.join(out_dir, "github-neural-contrib-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Done: {dark_path}")


if __name__ == "__main__":
    main()
