import argparse
import sys
from pathlib import Path
 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
 
from config import MEASURMENTS_CSV_FILENAME,NO_VALUE
from heatmap_matrix import save_matrix
 
 
def split_name(name,type_):
    row_id = name.split('_')[0]
    #rotation
    if type_ == "rotation":
        rest = name.split('_')[-1]
        if "R0" in name or "R0.0" in name:
            value = NO_VALUE
        else:
            value = rest.split('R')[-1]+"º"
    #translation
    else:
        rest = name.split('_')[-2]
        if "T(0,0)" in name or "T(0.0,0.0)" in name:
            value = NO_VALUE
        else:
            value = rest.split("T(")[1].split(",")[0]
    return row_id, value
 
 
def column_sort_key(value):
    if not "-"  in value:
        if "º" in value:
            return (0,float(value[0:-2]),"")
        return (0,float(value),"")
    else:
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
 
 
def collect(base_folder, measurement,type_):
    records = {}
    for folder in sorted(p for p in base_folder.iterdir() if p.is_dir()):
        if(type_ == "rotation"):
            if "R0.0" in str(folder):
                continue
            elif type_ == "translation":
                name = folder.name

                t_value = 0.0
                t_start = name.find("T(")
                if t_start != -1:
                    t_end = name.find(",", t_start)
                    t_value = float(name[t_start + 2:t_end])

                r_value = 0.0
                r_start = name.find("_R")
                if r_start != -1:
                    r_end = name.find("_", r_start + 2)
                    if r_end == -1:
                        r_end = len(name)
                    r_value = float(name[r_start + 2:r_end])

                if t_value == 0 and r_value != 0:
                    continue

        parts = split_name(folder.name,type_)
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
            if type_ == "translation":
                print(f"Skipping {folder.name}: ID={parts[0]}, VALUE={parts[1]} because non-zero radiuses are skipped in this heatmap.")
            else:
                print(f"Skipping {folder.name}: ID={parts[0]}, VALUE={parts[1]} already taken"
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
 
 
def plot(rows, cols, matrix, measurement, title, reverse, type_,output_folder):

    cmap_name = "RdYlGn_r" if reverse else "RdYlGn"
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_bad("lightgray")
 
    fig, ax = plt.subplots(
        figsize=(max(6, 0.8 * len(cols) + 4), max(4, 0.4 * len(rows) + 2))
    )
    im = ax.imshow(np.ma.masked_invalid(matrix), cmap=cmap, aspect="auto")
 
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows)
    if(type_ == "rotation"):
        ax.set_xlabel(r"Degrees of rotation from center")
    else:
        ax.set_xlabel(r"Horizontal translation")
    
    ax.set_ylabel("Perlin Point Cloud Name")
    ax.set_title(title or measurement)

    measurement_label = measurement
 

    fig.colorbar(im, ax=ax, label=measurement_label)
    fig.tight_layout(pad=5.0)

    output_dir : Path = Path(__file__).resolve().parent.parent / output_folder
    output_dir.mkdir(parents=True, exist_ok= True)
    output_heatmap = output_dir / f"{title}.png"
    fig.savefig(output_heatmap)
    print(f"Saved {output_heatmap}")
    save_matrix(rows, cols, matrix, output_heatmap, measurement, title, reverse, ax.get_xlabel(), "Perlin Point Cloud Name")
    plt.show()
 
 
def main():
    parser = argparse.ArgumentParser(description="Heatmap of a measurement across folders.")
    parser.add_argument("root_folder",help="Root folder containing the measurement folders")
    parser.add_argument("column",help="Column name containing the measurement")
    parser.add_argument("title",help="Title of the heatmap")
    parser.add_argument("type_",help="Type")
    parser.add_argument("output_folder",help="Folder to store the heatmap")
    parser.add_argument("--reverse",action="store_true",help="Reverse the colormap: green at 0, red at max")

    
    args = parser.parse_args()
    records = collect(Path(args.root_folder), args.column, args.type_)
    rows, cols, matrix = build_matrix(records)
    plot(rows, cols, matrix, args.column, args.title, args.reverse, args.type_, args.output_folder)
 
if __name__ == "__main__":
    main()
 
