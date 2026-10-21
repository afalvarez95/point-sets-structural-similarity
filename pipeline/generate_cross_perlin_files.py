import pandas as pd
from mci_lib.point_set_generation.point_set_generation import *
import os
import itertools
from pathlib import Path
from config import GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER,GCPF__OUTPUT_FOLDER

DEFAULT_BASE_POINT_CLOUD_FOLDER = GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER

OUTPUT_FOLDER  = GCPF__OUTPUT_FOLDER


if DEFAULT_BASE_POINT_CLOUD_FOLDER is None or OUTPUT_FOLDER is None:
    raise SystemExit("Cross generation is not applicable: GCPF__ folders are None in config.py.")

input_folder = Path(DEFAULT_BASE_POINT_CLOUD_FOLDER)
output_folder = Path(OUTPUT_FOLDER)
output_folder.mkdir(parents=True, exist_ok=True)

csv_files = list(input_folder.glob("*.csv"))

for perlin1_file, perlin2_file in list(itertools.combinations_with_replacement(csv_files, 2)):
    perlin1_filename = perlin1_file.name
    perlin2_filename = perlin2_file.name
    short_name_1 = perlin1_filename.split('_')[0]
    short_name_2 = perlin2_filename.split('_')[0]
    csv_path = Path(output_folder,f"{short_name_1}x{short_name_2}_T(0,0)_R0_.csv")
    dualperlincloud = DualPerlinCloud(width_im=1000,height_im=1000,point_labels=['Type 1','Type 2'],csv_name=csv_path)
    dualperlincloud.load_cross_perlin_cloud_from_two_files(perlin1_file,perlin2_file)
    dualperlincloud.generate_csv()