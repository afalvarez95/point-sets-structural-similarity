
import argparse
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from config import MEASURMENTS_CSV_FILENAME
from heatmap_matrix import save_matrix
from heatmap_classes import PAPER_FONTSIZE, set_class_ticks, set_paper_title, measurement_label

def read_measurement(csv_path, column):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader, None)

    if row is None:
        raise ValueError(f"No data row in {csv_path}")

    if column not in row:
        raise ValueError(
            f"Column '{column}' not found in {csv_path}"
        )
    return float(row[column])



def order_names(label_name):
    ending = label_name[1:]
    if label_name[0] == "S":
        if label_name[1] == "4":
            return 0, ending
        elif label_name[1] == "8":
            return 0.1, ending
        else:
            return 0.2, ending
    elif label_name[0] == "B":
        return 1, ending
    else:
       return 2, ending

def generate_short_name(label_name):
    if label_name[0] == "S":
        return label_name
    elif label_name[0] == "B":
        return label_name
    else:
       return label_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root_folder",help="Root folder containing the measurement folders")
    parser.add_argument("column",help="Column name containing the measurement")
    parser.add_argument("title",help="Title of the heatmap")
    parser.add_argument("output_folder",help="Folder to store the heatmap")
    parser.add_argument("--reverse",action="store_true",help="Reverse the colormap: green at 0, red at max")


    args = parser.parse_args()

    measurements = {}
    names = set()

    for folder in os.listdir(args.root_folder):
        folder_path = os.path.join(args.root_folder, folder)

        if not os.path.isdir(folder_path):
            continue

        csv_path = os.path.join(folder_path, MEASURMENTS_CSV_FILENAME)

        if not os.path.isfile(csv_path):
            continue

        value = read_measurement(csv_path, args.column)

        if "x" in folder:
            cross_name = folder.split("_")[0]
            name1, name2 = cross_name.split("x", 1)
            name1 = generate_short_name(name1)
            name2 = generate_short_name(name2)

            names.add(name1)
            names.add(name2)


            measurements[(name1, name2)] = value
            measurements[(name2, name1)] = value

        else:
            single_name = folder.split("_")[0]+folder.split("_")[1]
            single_name = generate_short_name(single_name)

            names.add(single_name)
            measurements[(single_name, single_name)] = value

    names = sorted(names, key= lambda name: order_names(name))
    n = len(names)

    name_to_index = {
        name: i for i, name in enumerate(names)
    }

    matrix = np.full((n, n), np.nan)

    for (name1, name2), value in measurements.items():
        i = name_to_index[name1]
        j = name_to_index[name2]

        matrix[i, j] = value

    cmap = "RdYlGn_r" if args.reverse else "RdYlGn"


    fig, ax = plt.subplots(
        figsize=(9, 8),
        constrained_layout=True
    )



    im = ax.imshow(
        matrix,
        cmap=cmap,
        vmin=0,
        vmax=np.nanmax(matrix)
    )

    #One label per class of Perlin cloud instead of one per point cloud
    set_class_ticks(ax, names, "x")
    set_class_ticks(ax, names, "y")

    ax.set_xlabel("Perlin cloud class", fontsize=PAPER_FONTSIZE["label"])
    ax.set_ylabel("Perlin cloud class", fontsize=PAPER_FONTSIZE["label"])

    set_paper_title(ax, args.title)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(measurement_label(args.column), fontsize=PAPER_FONTSIZE["colorbar"])
    cbar.ax.tick_params(labelsize=PAPER_FONTSIZE["ticks"])

    output_dir : Path = Path(__file__).resolve().parent.parent / args.output_folder
    output_dir.mkdir(parents=True, exist_ok= True)
    output_heatmap = output_dir / f"{args.title}.png"
    fig.savefig(output_heatmap, dpi=300)
    save_matrix(names, names, matrix, output_heatmap, args.column, args.title, args.reverse,
                "Perlin Point Cloud Name", "Perlin Point Cloud Name", vrange=(0, np.nanmax(matrix)))
    plt.show()


if __name__ == "__main__":
    main()
