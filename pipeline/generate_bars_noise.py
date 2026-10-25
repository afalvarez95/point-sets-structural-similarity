import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from config import MEASURMENTS_CSV_FILENAME
from heatmap_classes import PAPER_FONTSIZE, class_of, set_class_ticks

#Bars of the impulsive noise tests: one lane per measurement and, for each point cloud, one bar per number of noise points,
#each bar the mean of the seed variations of that number of points. Classes of point clouds on the horizontal axis.
#It also saves the means in <output>/noise_bars_mean.csv.

MEASUREMENTS = ["mci", "wasserstein", "avg_haussdorf_distance_value", "p95_haussdorf_distance_value", "haussdorf_distance_value"]
#Short labels of the lanes, so they fit with the paper font size
LANE_LABELS = {"mci": "MCI", "wasserstein": "Sliced\nWasserstein", "avg_haussdorf_distance_value": "AHD",
               "p95_haussdorf_distance_value": "HD95", "haussdorf_distance_value": "Hausdorff"}
CLASSES = ["S4", "S8", "S16", "B4816", "C416-Coarse", "C416-Fine"]


def collect(root_folder):
    rows = [pd.read_csv(csv).iloc[0] for csv in sorted(Path(root_folder).glob(f"*/{MEASURMENTS_CSV_FILENAME}"))]
    return pd.DataFrame(rows).rename(columns={"seed": "cloud"})


def main():
    parser = argparse.ArgumentParser(description="Bars of the impulsive noise tests, mean of the seed variations.")
    parser.add_argument("root_folder", help="Root folder containing the measurement folders")
    parser.add_argument("output_folder", help="Folder to store the plot")
    parser.add_argument("--title", default="Clean vs impulsive noise", help="Title of the plot")
    args = parser.parse_args()

    df = collect(args.root_folder)
    variations = df.groupby(["cloud", "noise_points"])["noise_seed_offset"].nunique()
    means = df.groupby(["cloud", "noise_points"])[MEASUREMENTS].mean().reset_index()
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    means.to_csv(output_folder / "noise_bars_mean.csv", index=False)
    print(f"{df['cloud'].nunique()} clouds, noise points {sorted(df['noise_points'].unique())}, "
          f"{variations.min()}-{variations.max()} seed variations per bar")

    counts = sorted(means["noise_points"].unique())
    clouds = sorted(means["cloud"].unique(), key=lambda c: (CLASSES.index(class_of(c)), c))
    colors = {c: plt.get_cmap("tab10")(i) for i, c in enumerate(counts)}
    width = 0.8 / len(counts)
    fig, axes = plt.subplots(len(MEASUREMENTS), 1, figsize=(18, 3.6 * len(MEASUREMENTS)), sharex=True)
    for ax, column in zip(axes, MEASUREMENTS):
        for k, count in enumerate(counts):
            values = means[means["noise_points"] == count].set_index("cloud").loc[clouds, column]
            ax.bar([i - 0.4 + width * (k + 0.5) for i in range(len(clouds))], values, width=width, color=colors[count], label=f"{count} points")
        #Horizontal class labels, so they take less height than the bars
        set_class_ticks(ax, clouds, "x", rotation=0, fontsize=PAPER_FONTSIZE["label"] + 2)
        ax.set_ylabel(LANE_LABELS[column], fontsize=PAPER_FONTSIZE["label"])
        ax.tick_params(axis="y", labelsize=PAPER_FONTSIZE["ticks"] - 2)
    axes[-1].set_xlim(-0.6, len(clouds) - 0.4)
    axes[-1].set_xlabel("Perlin cloud class", fontsize=PAPER_FONTSIZE["label"])
    fig.suptitle(f"{args.title} (mean of {variations.max()} seeds)", fontsize=PAPER_FONTSIZE["title"] + 6)
    fig.legend(*axes[0].get_legend_handles_labels(), ncol=len(counts), loc="upper center", bbox_to_anchor=(0.5, 0.962),
               fontsize=PAPER_FONTSIZE["label"] + 4, frameon=False, handlelength=2.5, columnspacing=2.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    output = output_folder / "noise_bars.png"
    fig.savefig(output, dpi=300)
    plt.close(fig)
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
