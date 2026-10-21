from pathlib import Path
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Saves the matrix of a heatmap next to it, so it can be explored:
#<heatmap>_matrix.csv with the values, and <heatmap>_matrix.png with the value written on each cell.


def save_matrix(rows, cols, matrix, output_heatmap, measurement, title, reverse, xlabel, ylabel, vrange=None):
    output_heatmap = Path(output_heatmap)
    stem = output_heatmap.with_suffix("").name

    output_csv = output_heatmap.with_name(f"{stem}_matrix.csv")
    pd.DataFrame(matrix, index=rows, columns=cols).to_csv(output_csv, index_label=ylabel)
    print(f"Saved {output_csv}")

    cmap = plt.get_cmap("RdYlGn_r" if reverse else "RdYlGn").copy()
    cmap.set_bad("lightgray")
    masked = np.ma.masked_invalid(matrix)
    vmin, vmax = vrange if vrange is not None else (np.nanmin(matrix), np.nanmax(matrix))

    #Cells big enough to fit a value with 2 decimals, smaller font for wide matrices like the cross one.
    n_rows, n_cols = matrix.shape
    fontsize = 8 if n_cols <= 12 else 5
    cell = 0.9 if max(n_rows, n_cols) <= 12 else 0.42
    fig, ax = plt.subplots(figsize=(max(6, cell * n_cols + 4), max(4, cell * 0.55 * n_rows + 2)))
    im = ax.imshow(masked, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)

    for i in range(n_rows):
        for j in range(n_cols):
            value = matrix[i, j]
            if np.isnan(value):
                continue
            #White text on the dark ends of the colormap, black on the light middle.
            normalized = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
            color = "white" if normalized < 0.15 or normalized > 0.85 else "black"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=fontsize, color=color)

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(cols, rotation=90 if n_cols > 12 else 0)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(rows)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    #Long titles are wrapped so they fit in narrow matrices.
    ax.set_title(textwrap.fill(title or measurement, width=int(fig.get_figwidth() * 8)))
    fig.colorbar(im, ax=ax, label=measurement)
    fig.tight_layout()

    output_png = output_heatmap.with_name(f"{stem}_matrix.png")
    fig.savefig(output_png, dpi=150)
    plt.close(fig)
    print(f"Saved {output_png}")
