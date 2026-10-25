import argparse
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd
from mci_lib.point_set_generation.point_set_generation import DualPerlinCloud, PerlinFunc, PerlinType
from config import GNPF__DATASET_CSV_FILE, GNPF__OUTPUT_FOLDER, NOISE__COUNTS, NOISE__SEED_OFFSETS

#Step 2 of the impulsive noise tests: for each base cloud of perlin_base_dataset.csv, builds the Perlin field once and writes
#one dual cloud per number of noise points and seed offset: <cloud>_n<count>s<offset>.csv,
#Type 1 = the clean cloud (the same blobs as generate_perlin_files.py), Type 2 = the clean cloud plus the noise points.

DATASET_CSV_FILE = GNPF__DATASET_CSV_FILE
OUTPUT_FOLDER = GNPF__OUTPUT_FOLDER


def semicolon_list(string, cast):
    #Same format as generate_perlin_files.py: [a;b;c], or nan when empty
    if string in ("nan", "None"):
        return None
    return [cast(x) for x in string[1:-1].split(";")]


def generate(row, output_folder, counts, seed_offsets):
    #The settings come from the main process, so every worker uses the same config
    name = row["name"]
    perlin_func = PerlinFunc(PerlinType[row["perlin_type"]], semicolon_list(row["seed_array"], int), semicolon_list(row["octave_array"], int),
                             custom_weights=semicolon_list(row["perlin_weights"], float))
    sampling_seed = int(row["numpy_choice_rng_seed"])
    cloud = DualPerlinCloud(1000, 1000, perlin_func, ["Type 1", "Type 2"], None,
                            float(row["t1_point_density"]), float(row["t2_rigid_loss"]), point_sampling_seed=sampling_seed)
    cloud.generate_perlin_base_points()
    cloud.generate_threshold()
    cloud.generate_original_perlin_points()
    blobs = cloud.points_data.get_original_points()

    for offset in seed_offsets:
        noise_by_count = cloud.generate_impulsive_noise_points(sampling_seed + offset, counts)
        for count in counts:
            cloud.csv_name = os.path.join(output_folder, f"{name}_n{count}s{offset}.csv")
            cloud.points_data.set_transformed_points(np.vstack([blobs, noise_by_count[count]]))
            cloud.generate_csv()
    return name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processes", type=int, default=8, help="Clouds generated in parallel (about 1 minute each)")
    parser.add_argument("--only", nargs="*", help="Names of the clouds to generate, all of them by default")
    args = parser.parse_args()

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    rows = pd.read_csv(DATASET_CSV_FILE).astype(str).to_dict("records")
    if args.only:
        rows = [row for row in rows if row["name"] in args.only]
    with Pool(args.processes) as pool:
        done = pool.starmap(generate, [(row, str(OUTPUT_FOLDER), NOISE__COUNTS, NOISE__SEED_OFFSETS) for row in rows])
    print(f"{len(done)} clouds x {len(NOISE__COUNTS)} counts x {len(NOISE__SEED_OFFSETS)} seed offsets in {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()
