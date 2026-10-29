"""Compact, descriptive view of the perturbation/removal results.

Reads the _matrix.csv files of the per+rem heatmaps (generate_heatmap_rem_and_pert.py), so it runs after them.
Rows are removal levels, columns are measurements, the horizontal axis is the perturbation epsilon.
Lines are means of eight clouds per class; bands are observed minima/maxima.
Saves combined_compact.png (450 dpi) and combined_compact.svg in the output folder.
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


#Removal levels of the rows, only for this plot
REMOVAL_LEVELS = (0, 20, 60)
EPSILON = np.array([0, 5, 10, 20, 40])
CLASSES = (
    ("S4", "#1f77b4"),
    ("S8", "#ff7f0e"),
    ("S16", "#2ca02c"),
    ("B4816", "#d62728"),
    ("C416-Coarse", "#9467bd"),
    ("C416-Fine", "#8c564b"),
)
#Measurement label of the heatmap folders and title of the column; the y limits of each column come from the data
METRICS = (
    ("MCI", "MCI"),
    ("HD95", "HD95"),
    ("AHD", "AHD"),
    ("Sliced Wasserstein", "Sliced Wasserstein"),
)


def read_values(source, title, metric, removal):
    filename = "no removals_matrix.csv" if removal == 0 else f"rem {removal}%_matrix.csv"
    path = Path(source) / f"heatmaps_{title} {metric}" / filename
    values = pd.read_csv(path, index_col=0)
    if removal:
        # 'baseline' is identity, not the zero-perturbation removed cloud.
        values = values.drop(columns="baseline").rename(columns={"none": "0"})
    else:
        values = values.rename(columns={"baseline": "0"})
    values.columns = [int(float(column)) for column in values.columns]
    return values.loc[:, EPSILON]


def main():
    parser = argparse.ArgumentParser(description="Compact plot of the perturbation + removal results (removal 0, 20 and 60%).")
    parser.add_argument("heatmap_folder", help="Folder with the heatmaps_<title> <measurement> folders of the per+rem heatmaps")
    parser.add_argument("output_folder", help="Folder to store the plot")
    parser.add_argument("--title", default="Perturbed and Removed Perlin Point Sets", help="Title used in the names of the heatmap folders")
    args = parser.parse_args()

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7,
        "axes.titlesize": 8.5,
        "axes.labelsize": 7.5,
        "xtick.labelsize": 6.8,
        "ytick.labelsize": 6.8,
        "axes.linewidth": 0.6,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })
    figure, axes = plt.subplots(3, 4, figsize=(7.2, 4.9), sharex=True, sharey="col")
    figure.subplots_adjust(left=0.078, right=0.985, bottom=0.105, top=0.86,
                           wspace=0.25, hspace=0.22)
    #Highest band of each column, for its shared y limits
    column_max = np.zeros(len(METRICS))
    for row, removal in enumerate(REMOVAL_LEVELS):
        for column, (metric, title) in enumerate(METRICS):
            axis = axes[row, column]
            values = read_values(args.heatmap_folder, args.title, metric, removal)
            class_names = values.index.to_series().map(lambda name: name.rsplit("-", 2)[0])
            for name, color in CLASSES:
                group = values.loc[class_names == name]
                if len(group) != 8:
                    raise ValueError(f"Expected 8 clouds in {name}; received {len(group)}")
                axis.fill_between(EPSILON, group.min().to_numpy(), group.max().to_numpy(),
                                  facecolor=color, alpha=0.09, linewidth=0, zorder=1)
                axis.plot(EPSILON, group.mean().to_numpy(), color=color,
                          linewidth=1.15, marker="o", markersize=2.1,
                          markeredgewidth=0, zorder=3)
                column_max[column] = max(column_max[column], group.max().max())
            axis.set_xlim(-1, 41)
            axis.set_xticks(EPSILON)
            axis.grid(axis="y", color="#e5e5e5", linewidth=0.5, zorder=0)
            axis.tick_params(length=2.5, width=0.6, pad=2)
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
            if row == 0:
                axis.set_title(title, pad=7, fontweight="bold")
            if row == 2:
                axis.set_xlabel(r"Perturbation $\varepsilon$", labelpad=3)
        axes[row, 0].set_ylabel(f"Removal {removal}%", labelpad=8)
    #The columns share their y axis, so setting the top row sets all the rows
    for column in range(len(METRICS)):
        axes[0, column].set_ylim(0, column_max[column] * 1.05)
        axes[0, column].yaxis.set_major_locator(MaxNLocator(nbins=4))

    handles = [Line2D([0], [0], color=color, linewidth=1.5, marker="o", markersize=2.5,
                      markeredgewidth=0, label=name) for name, color in CLASSES]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.53, 0.985),
                  ncol=6, frameon=False, fontsize=7.3, handlelength=1.4,
                  columnspacing=1.2, handletextpad=0.4)
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_folder / "combined_compact.png", dpi=450)
    figure.savefig(output_folder / "combined_compact.svg")
    plt.close(figure)
    print(output_folder / "combined_compact.png")
    print(output_folder / "combined_compact.svg")


if __name__ == "__main__":
    main()
