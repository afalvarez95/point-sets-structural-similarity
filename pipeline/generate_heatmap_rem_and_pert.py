import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import MEASURMENTS_CSV_FILENAME
from heatmap_matrix import save_matrix
from heatmap_classes import PAPER_FIGSIZE, style_class_heatmap


NO_VALUE = "none"
BASELINE = "baseline"
NO_REM = "0" 



def split_name(name):
    if "_" not in name:
        return None
    id_and_rem, transformation = name.split("_", 1)
    epsilons = name[name.rfind("_") + 1:] or NO_VALUE
    has_removal = id_and_rem[-1] == "%"
    if has_removal and "-" in id_and_rem:
        row_id, rem = id_and_rem.rsplit("-", 1)
        return row_id, rem[3:-1], epsilons
    if transformation[0] == "T":
        return id_and_rem, None, BASELINE
    return id_and_rem, NO_REM, epsilons


def column_sort_key(value):
    if(value == BASELINE):
        return (0.0, 0.0, "")
    elif value == NO_VALUE:
        return (0.01, 0.01, "")
    elif("B" in value or "S" in value or "C" in value):
        ending = value[1:]
        if value[0] == "S":
            if value[1] == "4":
                return 0, ending,""
            elif value[1] == "8":
                return 0.1, ending,""
            else:
                return 0.2, ending,""
        elif value[0] == "B":
            return 1, ending,""
        else:
            return 2, ending,""
    else:
        return 1, float(value), ""


def collect(base_folder, measurement):
    records = {}
    for folder in sorted(p for p in base_folder.iterdir() if p.is_dir()):
        parts = split_name(folder.name)
        if parts is None:
            print(f"Skipping {folder.name}: no '_' in name", file=sys.stderr)
            continue
        if parts in records:
            print(f"Skipping {folder.name}: same condition as {records[parts][0]}", file=sys.stderr)
            continue

        csv_path = folder / MEASURMENTS_CSV_FILENAME
        if not csv_path.is_file():
            print(f"Skipping {folder.name}: no {MEASURMENTS_CSV_FILENAME}", file=sys.stderr)
            continue

        df = pd.read_csv(csv_path)
        if measurement not in df.columns:
            print(f"Skipping {folder.name}: no column '{measurement}'", file=sys.stderr)
            continue
        if df.empty:
            print(f"Skipping {folder.name}: {MEASURMENTS_CSV_FILENAME} is empty", file=sys.stderr)
            continue

        v = pd.to_numeric(df[measurement].iloc[0], errors="coerce")
        records[parts] = (folder.name, v)
    return {key: v for key, (_, v) in records.items()}


def build_matrix(records, rem):
    """Rows are IDs that have a certain removal, while columns are baseline and epsilon values."""
    ids = {row_id for row_id, r, _ in records if r == rem}
    cells = {(row_id, eps): v for (row_id, r, eps), v in records.items()
             if row_id in ids and r in (rem, None)}
    rows = sorted(ids, key=column_sort_key)
    cols = sorted({eps for _, eps in cells} | {BASELINE}, key=column_sort_key)
    matrix = np.full((len(rows), len(cols)), np.nan)
    for (row_id, eps), v in cells.items():
        matrix[rows.index(row_id), cols.index(eps)] = v
    return rows, cols, matrix


def plot(rows, cols, matrix, measurement, title, reverse, vrange, output):
    cmap = plt.get_cmap("RdYlGn_r" if reverse else "RdYlGn").copy()
    cmap.set_bad("lightgray")

    fig, ax = plt.subplots(figsize=PAPER_FIGSIZE)
    im = ax.imshow(np.ma.masked_invalid(matrix), cmap=cmap, aspect="auto", vmin=vrange[0], vmax=vrange[1])
    ax.axvline(0.5, color="black", linewidth=2)

    #One label per class of Perlin cloud on the rows, paper font sizes
    style_class_heatmap(fig, ax, im, rows, cols, title, "ε", measurement)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight", pad_inches=0.3)
    print(f"Saved {output}")
    save_matrix(rows, cols, matrix, output, measurement, title, reverse, "ε", "Perlin Point Cloud Name", vrange=vrange)


def main():
    parser = argparse.ArgumentParser(description="One heatmap per removed case across folders.")
    parser.add_argument("root_folder", type=Path, help="Root folder containing the measurement folders")
    parser.add_argument("column", help="Column name containing the measurement")
    parser.add_argument("title", help="Title of the heatmap, but defaults to column if not set")
    parser.add_argument("out_folder", type=Path, default=None, help="Where to save the PNGs. Default is heatmaps_<title>)")
    parser.add_argument("-r", "--reverse", action="store_true", help="Invert colormap (high = red)")
    args = parser.parse_args()

    if not args.root_folder.is_dir():
        sys.exit(f"Not a folder: {args.root_folder}")

    records = collect(args.root_folder, args.column)
    rems = sorted({r for _, r, _ in records if r is not None}, key=column_sort_key)
    if not rems:
        sys.exit("Folder has not removed Perlin Clouds.")

    values = np.array(list(records.values()), dtype=float)
    vrange = (np.nanmin(values), np.nanmax(values))  #Keeping same color scale on every heatmap
    out_folder = args.out_folder or Path(re.sub(r'[\\/:*?"<>|]', "", args.title).strip())
    if out_folder is not None:
        out_folder = out_folder / f"heatmaps_{args.title}"
    out_folder.mkdir(parents=True, exist_ok=True)

    for rem in rems:
        rows, cols, matrix = build_matrix(records, rem)
        label = "no removals" if rem == NO_REM else f"rem {rem}%"
        plot(rows, cols, matrix, args.column, f"{args.title} - {label}",
             args.reverse, vrange,
             out_folder / f"{label}.png")
    plt.show()


if __name__ == "__main__":
    main()