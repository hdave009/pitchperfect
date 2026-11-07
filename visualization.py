import matplotlib

matplotlib.use("Agg")  # Prevents macOS GUI thread crashes with Pygame!
import matplotlib.pyplot as plt
import io
import pygame


def create_trend_chart_surface(history, width=520, height=180):
    """
    Generates a clean line chart indexed by game number
    and converts it into a Pygame surface.
    """
    if not history:
        return None

    game_numbers = [f"G{i+1}" for i in range(len(history))]
    accuracies = [h[0] for h in history]

    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor("#232328")
    ax.set_facecolor("#2d2d34")

    ax.plot(
        game_numbers, accuracies, color="#50c878", marker="o", linewidth=2, markersize=6
    )
    ax.set_title("Performance Trend (Accuracy %)", color="white", fontsize=10, pad=8)
    ax.tick_params(colors="white", labelsize=8)
    ax.set_ylim(-5, 105)

    ax.grid(True, color="#404048", linestyle="--", alpha=0.5)
    for spine in ax.spines.values():
        spine.set_color("#50505c")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    buf.seek(0)
    plt.close(fig)

    chart_surface = pygame.image.load(buf, "png").convert()
    return chart_surface
