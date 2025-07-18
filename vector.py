from manim import *
import numpy as np

# Slow down all default animations
config.default_animation_run_time = 4.0  # seconds per default animation

class MultiHotSimilarity(ThreeDScene):
    def construct(self):
        # --- 1a: Display business descriptions ---
        desc1 = Text(
            "1) We present custom shop stratocasters\nsigned by John Mayer",
            t2c={"signed": BLUE, "John Mayer": GREEN},
        ).scale(0.6).to_edge(UP)
        desc2 = Text(
            "2) Our tea boxes are signed by Prof. Ruochen Wu,\n   certified master in tea appreciation",
            t2c={"tea": YELLOW, "signed": BLUE},
        ).scale(0.6).next_to(desc1, DOWN, buff=0.5)
        # Use a longer write time explicitly, and pause after
        self.play(Write(desc1), Write(desc2), run_time=4.0)
        self.wait(3)  # longer break

        # --- 1b: Vocabulary and multi-hot encoding ---
        vocab = ["signed", "tea", "John Mayer"]
        vocab_text = Text(
            "Vocabulary: " + ", ".join(vocab)
        ).scale(0.6).next_to(desc2, DOWN, buff=0.5)
        Pi = np.array([1, 0, 1])
        Pj = np.array([1, 1, 0])
        Pi_tex = Matrix([Pi]).scale(0.6).next_to(vocab_text, DOWN, buff=0.5)
        Pj_tex = Matrix([Pj]).scale(0.6).next_to(Pi_tex, DOWN, buff=0.3)
        label_Pi = MathTex("P_i =").scale(0.6).next_to(Pi_tex, LEFT)
        label_Pj = MathTex("P_j =").scale(0.6).next_to(Pj_tex, LEFT)
        self.play(
            Write(vocab_text),
            Write(label_Pi),
            Create(Pi_tex),
            Write(label_Pj),
            Create(Pj_tex),
            run_time=4.0
        )
        self.wait(3)

        # --- 1c: Normalize vectors ---
        Vi = Pi / np.linalg.norm(Pi)
        Vj = Pj / np.linalg.norm(Pj)
        Vi_tex = MathTex(r"V_i=\frac{P_i}{\|P_i\|}").scale(0.6)
        Vj_tex = MathTex(r"V_j=\frac{P_j}{\|P_j\|}").scale(0.6)
        Vi_tex.next_to(Pj_tex, DOWN, buff=0.5)
        Vj_tex.next_to(Vi_tex, DOWN, buff=0.3)
        self.play(Write(Vi_tex), Write(Vj_tex), run_time=4.0)
        self.wait(3)

        # Clear everything with a graceful fade
        self.play(
            FadeOut(
                desc1, desc2, vocab_text,
                label_Pi, Pi_tex, label_Pj, Pj_tex,
                Vi_tex, Vj_tex
            ),
            run_time=3.0
        )
        self.wait(2)

        # --- 1d: 3D axes and two new vectors ---
        axes3d = ThreeDAxes(
            x_range=[-6, 6, 1], y_range=[-6, 6, 1], z_range=[-6, 6, 1],
        )
        self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES)
        self.play(Create(axes3d), run_time=4.0)
        self.wait(2)

        origin_3d = axes3d.c2p(0, 0, 0)
        # Example vectors
        v3 = np.array([0, 4, 4])
        v4 = np.array([4, 0, 4])
        end3 = axes3d.c2p(*v3)
        end4 = axes3d.c2p(*v4)
        arrow3 = Arrow3D(start=origin_3d, end=end3, color=BLUE)
        arrow4 = Arrow3D(start=origin_3d, end=end4, color=GREEN)
        # Slow ambient rotation
        self.begin_ambient_camera_rotation(rate=0.2, about="theta")
        self.play(Create(arrow3), Create(arrow4), run_time=4.0)
        self.wait(6)  # linger on the rotating 3D view
        self.stop_ambient_camera_rotation()

        # Angle label
        theta_mid = (end3 + end4) / 2
        theta_label3d = MathTex(r"\theta").scale(0.7).move_to(theta_mid)
        self.add_fixed_orientation_mobjects(theta_label3d)
        self.play(Write(theta_label3d), run_time=3.0)
        self.wait(3)

        # Rotate vector and show change slowly
        self.play(
            Rotate(
                arrow4,
                angle=45 * DEGREES,
                axis=OUT,
                about_point=origin_3d
            ),
            run_time=4.0
        )
        self.wait(3)

        # --- 1f: Similarity score ---
        sim = float(np.dot(Vi, Vj))
        sim_tex = MathTex(r"s_{ij}=V_i \cdot V_j=", f"{sim:.2f}") \
            .scale(0.6) \
            .to_corner(DR, buff=1.0)
        self.add_fixed_orientation_mobjects(sim_tex)
        self.play(Write(sim_tex), run_time=3.0)
        self.wait(3)
