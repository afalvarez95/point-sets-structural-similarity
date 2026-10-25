import argparse
import sys
from pathlib import Path
 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import MEASURMENTS_CSV_FILENAME,NO_VALUE
from heatmap_matrix import save_matrix
from heatmap_classes import PAPER_FIGSIZE, style_class_heatmap
 
 
def split_name(name):
    if "rem" in name:
        row_id = name.split("-rem")[0]
        value = name.split("-rem")[-1].split("%")[0]
    else:
        row_id = name.split("_")[0]
        value = NO_VALUE
    return row_id, value
 
 
def column_sort_key(value):
    """'None first, then numeric values in order, then text."""
    if value == NO_VALUE:
        return (0, 0.0, "")
    elif("B" in value or "S" in value or "C" in value):
        print(value)
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

        if parts in records:
            print(f"Skipping {folder.name}: ID={parts[0]}, VALUE={parts[1]} already taken "
                  f"by {records[parts][0]}", file=sys.stderr)
            continue
        records[parts] = (folder.name, v)

    return {key: v for key, (_, v) in records.items()}
 
 
def build_matrix(records):
    rows = sorted({row_id for row_id, _ in records}, key=column_sort_key)
    cols = sorted({value for _, value in records}, key=column_sort_key)
    matrix = np.full((len(rows), len(cols)), np.nan)
    for (base, value), v in records.items():
        matrix[rows.index(base), cols.index(value)] = v
    return rows, cols, matrix
 
 
def plot(rows, cols, matrix, measurement, title, reverse,output_folder):
    cmap_name = "RdYlGn_r" if reverse else "RdYlGn"
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_bad("lightgray")
 
    fig, ax = plt.subplots(figsize=PAPER_FIGSIZE)
    im = ax.imshow(np.ma.masked_invalid(matrix), cmap=cmap, aspect="auto")

    #One label per class of Perlin cloud on the rows, paper font sizes
    style_class_heatmap(fig, ax, im, rows, cols, title or measurement, r"% of removal", measurement)
    fig.tight_layout()

    output_dir : Path = Path(__file__).resolve().parent.parent / output_folder
    output_dir.mkdir(parents=True, exist_ok= True)
    output_heatmap = output_dir / f"{title}.png"
    fig.savefig(output_heatmap, dpi=300)
    print(f"Saved {output_heatmap}")
    save_matrix(rows, cols, matrix, output_heatmap, measurement, title, reverse, r"% of removal", "Perlin Point Cloud Name")
    plt.show()
 
 
def main():
    parser = argparse.ArgumentParser(description="Heatmap of a measurement across folders.")
    parser.add_argument("root_folder",help="Root folder containing the measurement folders")
    parser.add_argument("column",help="Column name containing the measurement")
    parser.add_argument("title",help="Title of the heatmap")
    parser.add_argument("output_folder",help="Folder to store the heatmap")
    parser.add_argument("--reverse",action="store_true",help="Reverse the colormap: green at 0, red at max")

    args = parser.parse_args()
    records = collect(Path(args.root_folder), args.column)
    rows, cols, matrix = build_matrix(records)
    plot(rows, cols, matrix, args.column, args.title, args.reverse,args.output_folder)
 
 
if __name__ == "__main__":
    main()
 
