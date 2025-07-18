from manim import *
import numpy as np
import itertools
import random

# ---------- helper utilities ---------- #
def random_similarity_matrix(n, low=0.2, high=1.0):
    """Symmetric similarity matrix with 1's on the diagonal."""
    S = np.random.uniform(low, high, size=(n, n))
    S = (S + S.T) / 2
    np.fill_diagonal(S, 1)
    return S

def edge_style(weight):
    """Map similarity weight ∈ (0,1] to a color + stroke‑width."""
    # deepest colour (highest weight) = RED; lightest = LIGHT_GREY
    base = interpolate_color(LIGHT_GREY, RED_E, weight)
    width = 1 + 4 * weight          # 1–5 px
    return base, width

def avg_linkage_score(S, cluster_a, cluster_b):
    """Compute average similarity between two (index) sets."""
    idx_a = list(cluster_a)
    idx_b = list(cluster_b)
    return S[np.ix_(idx_a, idx_b)].mean()

# ---------- oriented‑ellipse version ---------- #
class AverageLinkageClustering(ThreeDScene):
    N_NODES   = 12
    MIN_CLUST = 5
    RNG_SEED  = 20250717

    # --- build a PCA‑aligned ellipse that fully contains the points ----
    def make_oriented_ellipse(self, node_ids, nodes, pad=0.30, min_axis=0.25):
        P   = np.array([nodes[i].get_center()[:2] for i in node_ids])
        cen = P.mean(axis=0)

        if len(P) == 1:
            # singleton → tiny circle
            w = h = 2*min_axis + pad
            angle = 0
        else:
            # 1) PCA on the points
            C = np.cov(P.T)
            vals, vecs = np.linalg.eigh(C)
            order = np.argsort(vals)[::-1]
            vecs = vecs[:, order]

            # 2) coordinates in PCA frame
            proj = (P - cen) @ vecs

            # 3) initial half‑extents along each PCA axis + pad
            dx0, dy0 = np.max(np.abs(proj), axis=0) + pad

            # 4) check each point’s “ellipse radius” and scale up if needed
            #    r_i = sqrt((x/dx0)^2 + (y/dy0)^2)
            radii = np.sqrt((proj[:,0]/dx0)**2 + (proj[:,1]/dy0)**2)
            scale = max(1.0, radii.max())

            # 5) final half‑axes
            dx, dy = dx0 * scale, dy0 * scale

            # 6) build the ellipse
            w = max(2*dx, 2*min_axis)
            h = max(2*dy, 2*min_axis)
            angle = np.arctan2(vecs[1, 0], vecs[0, 0])

        ell = Ellipse(width=w, height=h, stroke_color=BLUE_C, stroke_width=4)
        # rotate so its “width” axis aligns with the first eigenvector
        ell.rotate(angle, about_point=ORIGIN)
        # move from origin to the cluster’s centroid (in 3D)
        ell.move_to(np.append(cen, 0))
        ell.z_index = -1
        return ell


    def construct(self):
        rng = np.random.default_rng(self.RNG_SEED)
        S   = random_similarity_matrix(self.N_NODES)

        # ❶ nodes on a circle
        R = 3
        ang = np.linspace(0, TAU, self.N_NODES, endpoint=False)
        pos = [R*np.array([np.cos(a), np.sin(a), 0]) for a in ang]
        nodes  = VGroup(*[Dot(p, radius=0.09) for p in pos])
        labels = VGroup(*[
            Text(str(i), font_size=24).next_to(nodes[i], UP*0.25)
            for i in range(self.N_NODES)
        ])
        self.play(FadeIn(nodes, labels, lag_ratio=0.05), run_time=1.6)

        # ❷ backdrop similarity edges
        edges = VGroup()
        for i, j in itertools.combinations(range(self.N_NODES), 2):
            col, sw = edge_style(S[i, j])
            edges.add(Line(pos[i], pos[j], stroke_color=col, stroke_width=sw))
        self.play(Create(edges, lag_ratio=0.01), run_time=2)

        # ❸ state containers
        clusters = {i: [i] for i in range(self.N_NODES)}   # ordered lists
        order    = list(range(self.N_NODES))               # round‑the‑circle
        outline  = {i: self.make_oriented_ellipse([i], nodes)
                    for i in range(self.N_NODES)}          # start w/ dots
        self.play(*[Create(ell) for ell in outline.values()], run_time=1)

        # ❹ agglomeration loop
        while len(clusters) >= self.MIN_CLUST:
            # a) pick best adjacent pair
            best_pair, best_score = None, -np.inf
            for k in range(len(order)):
                a, b = order[k], order[(k+1) % len(order)]
                sc   = avg_linkage_score(S, clusters[a], clusters[b])
                if sc > best_score:
                    best_pair, best_score = (a, b), sc

            a, b = best_pair
            A, B = clusters[a], clusters[b]

            # b) DRAW centroid‑to‑centroid line **before** removing ellipses
            cenA = np.mean([nodes[i].get_center() for i in A], axis=0)
            cenB = np.mean([nodes[i].get_center() for i in B], axis=0)
            hl   = Line(cenA, cenB, stroke_color=YELLOW, stroke_width=8)
            self.play(Create(hl), run_time=0.25)

            # c) fade old ellipses
            self.play(
                FadeOut(outline.pop(a)),
                FadeOut(outline.pop(b)),
                run_time=0.4
            )

            # d) fade highlight
            self.play(FadeOut(hl), run_time=0.2)

            # e) merge bookkeeping
            new_id = max(clusters)+1
            merged = A + B
            clusters[new_id] = merged
            clusters.pop(a); clusters.pop(b)

            ai = order.index(a)
            order.pop(ai)
            bi = order.index(b) if b in order else (ai % len(order))
            order.pop(bi)
            order.insert(ai, new_id)

            # f) draw new oriented ellipse
            ell = self.make_oriented_ellipse(merged, nodes)
            outline[new_id] = ell
            self.play(Create(ell), run_time=0.9)
            self.wait(0.4)

        self.wait(2)
