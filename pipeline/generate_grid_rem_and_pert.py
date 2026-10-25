import argparse
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import MEASURMENTS_CSV_FILENAME
from heatmap_classes import PAPER_FONTSIZE, class_of

#Grids of the perturbation + removal tests: one cell per case, epsilon of the perturbation on the vertical axis
#(0 at the bottom) and % of removal on the horizontal axis, with the 48 point clouds of the case inside the cell.
#- <measurement> violins.png: a violin with the distribution of the 48 clouds, each point colored by its class.
#- <measurement> bars.png: one bar per class (mean of its clouds), with the points of the class on top.
#All the cells of a measurement share the same vertical scale.

from heatmap_classes import MEASUREMENT_LABELS as MEASUREMENTS
CLASSES = ["S4", "S8", "S16", "B4816", "C416-Coarse", "C416-Fine"]
CLASS_COLORS = dict(zip(CLASSES, sns.color_palette("tab10", len(CLASSES))))
#Font sizes of the grids, bigger than PAPER_FONTSIZE because the figure holds 25 cells
GRID_FONTSIZE = {"title": 34, "label": 30, "case": 26, "values": 20, "legend": 26}

#<cloud>[-rem<removal>%]_Per_S_<seed>_E_<epsilon> or <cloud>[-rem<removal>%]_T(0,0)_R0_ (no perturbation)
NAME_PATTERN = re.compile(r"^(?P<cloud>.+?)(?:-rem(?P<rem>\d+)%)?_(?:Per_S_\d+_E_(?P<eps>[\d.]+)|T\(0,0\)_R0_)$")


def collect(root_folder):
    rows = []
    for folder in sorted(p for p in Path(root_folder).iterdir() if p.is_dir()):
        match = NAME_PATTERN.match(folder.name)
        csv_path = folder / MEASURMENTS_CSV_FILENAME
        if match is None or not csv_path.is_file():
            print(f"Skipping {folder.name}")
            continue
        row = pd.read_csv(csv_path).iloc[0]
        rows.append({"cloud": match["cloud"], "class": class_of(match["cloud"]), "removal": int(match["rem"] or 0),
                     "epsilon": float(match["eps"] or 0), **{m: float(row[m]) for m in MEASUREMENTS}})
    return pd.DataFrame(rows)


def epsilon_label(epsilon):
    return "0" if epsilon == 0 else f"{epsilon:g}"


def plot_grid(df, measurement, kind, title, output):
    removals = sorted(df["removal"].unique())
    #Epsilon 0 at the bottom: the first row of the grid is the largest epsilon
    epsilons = sorted(df["epsilon"].unique(), reverse=True)
    top = df[measurement].max() * 1.08 or 1

    fig, axes = plt.subplots(len(epsilons), len(removals), figsize=(4 * len(removals) + 2, 3.3 * len(epsilons) + 2),
                             sharex=True, sharey=True)
    rng = np.random.default_rng(0)
    for i, epsilon in enumerate(epsilons):
        for j, removal in enumerate(removals):
            ax = axes[i, j]
            cell = df[(df["epsilon"] == epsilon) & (df["removal"] == removal)]
            if kind == "violins":
                #One violin of the 48 clouds, the points spread horizontally inside it and colored by class
                with warnings.catch_warnings():
                    #A single violin makes seaborn set equal x limits for a moment, they are set just below
                    warnings.filterwarnings("ignore", message="Attempting to set identical low and high xlims")
                    sns.violinplot(y=cell[measurement], ax=ax, color="lightgray", cut=0, inner=None, linewidth=1)
                jitter = rng.uniform(-0.18, 0.18, len(cell))
                ax.scatter(jitter, cell[measurement], c=[CLASS_COLORS[c] for c in cell["class"]], s=34, edgecolors="black", linewidths=0.4, zorder=3)
                ax.set_xlim(-0.5, 0.5)
            else:
                #One bar per class with the mean of its clouds, the points of the class on top of its bar
                for k, c in enumerate(CLASSES):
                    values = cell[cell["class"] == c][measurement]
                    ax.bar(k, values.mean(), width=0.75, color=CLASS_COLORS[c], alpha=0.75)
                    ax.scatter(k + rng.uniform(-0.2, 0.2, len(values)), values, color=CLASS_COLORS[c], s=26, edgecolors="black", linewidths=0.4, zorder=3)
                ax.set_xlim(-0.6, len(CLASSES) - 0.4)
            ax.set_ylim(0, top)
            ax.set_xticks([])
            ax.set_ylabel("")
            ax.tick_params(axis="y", labelsize=GRID_FONTSIZE["values"])
            if i == 0:
                ax.set_title(f"{removal}%", fontsize=GRID_FONTSIZE["case"])
            if j == 0:
                ax.set_ylabel(f"ε = {epsilon_label(epsilon)}", fontsize=GRID_FONTSIZE["case"])

    fig.supxlabel("% of removal", fontsize=GRID_FONTSIZE["label"])
    #The overall label has its own margin on the left, so it does not overlap the ε of each row
    fig.supylabel("ε of perturbation", fontsize=GRID_FONTSIZE["label"], x=0.008)
    fig.suptitle(title, fontsize=GRID_FONTSIZE["title"])
    handles = [plt.Rectangle((0, 0), 1, 1, color=CLASS_COLORS[c]) for c in CLASSES]
    fig.legend(handles, CLASSES, ncol=len(CLASSES), loc="upper center", bbox_to_anchor=(0.5, 0.952), fontsize=GRID_FONTSIZE["legend"],
               frameon=False, handlelength=1.6, columnspacing=1.6)
    fig.tight_layout(rect=(0.03, 0, 1, 0.92))
    fig.savefig(output, dpi=300)
    plt.close(fig)
    print(f"Saved {output}")


def main():
    parser = argparse.ArgumentParser(description="Violin and bar grids of the perturbation + removal tests.")
    parser.add_argument("root_folder", help="Root folder containing the measurement folders")
    parser.add_argument("output_folder", help="Folder to store the grids")
    parser.add_argument("--title", default="Perturbed and Removed Perlin Point Sets", help="Start of the title of each grid")
    args = parser.parse_args()

    df = collect(args.root_folder)
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"{len(df)} point clouds, {df['removal'].nunique()} removals x {df['epsilon'].nunique()} epsilons")
    for measurement, label in MEASUREMENTS.items():
        for kind in ["violins", "bars"]:
            plot_grid(df, measurement, kind, f"{args.title} - {label} per case", output_folder / f"{label} {kind}.png")


if __name__ == "__main__":
    main()
