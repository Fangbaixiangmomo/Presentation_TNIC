from manim import *
import numpy as np

# -------- configurable parameters ----------
N_FIRMS         = 12           # number of nodes
THETA           = 0.15         # global threshold
RADIUS          = 3            # circle radius for node layout
SEED            = 9            # for reproducibility
SIM_MIN, SIM_MAX = 0.10, 0.99   # raw similarity range
# -------------------------------------------

def similarity_matrix(n, low=SIM_MIN, high=SIM_MAX, seed=SEED):
    """Create a random (generally asymmetric) similarity matrix."""
    rng = np.random.default_rng(seed)
    M = rng.uniform(low, high, size=(n, n))
    np.fill_diagonal(M, 0.0)
    return M

class TNICScene(Scene):
    def construct(self):
        # Generate similarity data and nodes
        S = similarity_matrix(N_FIRMS)
        nodes = self._create_nodes()
        self.add(*nodes)

        # --- p1: highlight firm 0 and its hub spokes ---
        p1_idx = 0
        p1_dot = nodes[p1_idx]
        highlight1 = Circle(radius=0.35, color=YELLOW, stroke_width=4).move_to(p1_dot.get_center())
        self.play(Create(highlight1))
        self.wait()

        # Draw p1 spokes
        spokes1 = []  # list of (j, edge)
        for j in range(N_FIRMS):
            if j == p1_idx:
                continue
            start = p1_dot[0].get_center()
            end   = nodes[j][0].get_center()
            edge  = Line(start, end)
            s_ij  = S[p1_idx, j]
            alpha = np.clip((s_ij - SIM_MIN) / (SIM_MAX - SIM_MIN), 0, 1)
            edge.set_stroke(BLUE, width=3, opacity=alpha)
            spokes1.append((j, edge))
        self.play(LaggedStart(*[FadeIn(e) for _, e in spokes1], lag_ratio=0.1))
        self.wait()

        # Compute median for p1
        row1 = S[p1_idx]
        m1   = np.median(row1[row1 > 0])
        z1   = row1 - m1
        # annotate
        self.play(Write(MathTex(rf"m_{{{p1_idx}}}={m1:.3f}").scale(0.6).next_to(p1_dot, UP)))
        self.wait()

        # Threshold p1 spokes
        survive1 = [(j, e) for j, e in spokes1 if z1[j] >= THETA]
        remove1  = [(j, e) for j, e in spokes1 if z1[j] <  THETA]
        if remove1:
            self.play(*[FadeOut(e) for _, e in remove1])
            self.wait()
        # turn survive1 red
        self.play(*[e.animate.set_stroke(RED, width=4) for _, e in survive1])
        self.wait()

        # --- p2: pick one surviving neighbor ---
        p2_idx = survive1[0][0]
        # dim p1 red spokes
        self.play(*[e.animate.set_stroke(RED, width=2, opacity=0.5) for _, e in survive1])
        self.wait()

        # highlight p2
        p2_dot = nodes[p2_idx]
        highlight2 = Circle(radius=0.35, color=YELLOW, stroke_width=4).move_to(p2_dot.get_center())
        self.play(Transform(highlight1, highlight2))
        self.wait()

        # Draw p2 spokes
        spokes2 = []
        for j in range(N_FIRMS):
            if j == p2_idx:
                continue
            start = p2_dot[0].get_center()
            end   = nodes[j][0].get_center()
            edge  = Line(start, end)
            s_ij  = S[p2_idx, j]
            alpha = np.clip((s_ij - SIM_MIN) / (SIM_MAX - SIM_MIN), 0, 1)
            edge.set_stroke(BLUE, width=3, opacity=alpha)
            spokes2.append((j, edge))
        self.play(LaggedStart(*[FadeIn(e) for _, e in spokes2], lag_ratio=0.1))
        self.wait()

        # Compute median for p2 and centre
        row2 = S[p2_idx]
        m2   = np.median(row2[row2 > 0])
        z2   = row2 - m2
        self.play(Write(MathTex(rf"m_{{{p2_idx}}}={m2:.3f}").scale(0.6).next_to(p2_dot, UP)))
        self.wait()

        # Threshold p2 spokes, excluding back to p1
        survive2 = [(j, e) for j, e in spokes2 if z2[j] >= THETA and j != p1_idx]
        remove2  = [(j, e) for j, e in spokes2 if not (z2[j] >= THETA and j != p1_idx)]
        if remove2:
            self.play(*[FadeOut(e) for _, e in remove2])
            self.wait()
        # turn p2 survival green
        self.play(*[e.animate.set_stroke(GREEN, width=4) for _, e in survive2])
        self.wait()

    def _create_nodes(self):
        nodes = VGroup()
        for k in range(N_FIRMS):
            angle = 2 * np.pi * k / N_FIRMS
            pos   = np.array([np.cos(angle), np.sin(angle), 0]) * RADIUS
            dot   = Dot(point=pos, radius=0.12, color=WHITE)
            label = Text(str(k), font_size=24).next_to(dot, DOWN, buff=0.1)
            nodes.add(VGroup(dot, label))
        return nodes
