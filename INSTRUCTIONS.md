# MCI Pipeline

Pipeline to generate Perlin point sets, analyse their nearest-neighbour distances, compute the MCI and plot the results as heatmaps.

Every step is controlled from one file, [`pipeline/config.py`](pipeline/config.py), so a test can be reproduced by keeping the same config values.

## Setup

From the project folder, run once:

```bash
pip install -r requirements.txt
pip install -e .
```

The second command installs `mci_lib` so the MCI commands can find it from any folder. `requirements.txt` pins the versions used to produce the results (Python 3.12.10).

The MCI videos are written with [ffmpeg](https://ffmpeg.org/download.html), which is not a pip package: install it and add its `bin` folder to the PATH.

## Folder layout

| Folder | Content | In git |
|---|---|---|
| `pipeline/` | Pipeline scripts and `config.py` | Yes |
| `mci_lib/` | MCI, metrics and point set generation library | Yes |
| `perlin_base_csv_dataset/` | Small CSVs that describe how to generate the point sets | Yes |
| `input_datasets/<dataset>/` | Ready-made point sets used by partial tests | Yes |
| `runs/` | Everything the pipeline generates, one folder per run | No |
| `notebook/` | Notebook to compute the MCI of your own point clouds, see [notebook/README.md](notebook/README.md) | Yes (its `outputs/` no) |
Each run writes into `runs/<DATEIDENTIFIER>_<mode>_<dataset>/`, using the short names of `PIPELINE_OPTIONS_SHORT_NAMES` and `DATASET_OPTIONS_SHORT_NAMES` in `config.py`, for example `runs/261021_MCI_HMAPS_CS/` or `runs/261021_REBUILT_STEPS_PER_REM/`.

| Mode | Short name | | Dataset | Short name |
|---|---|---|---|---|
| `MCI_AND_HEATMAPS` | `MCI_HMAPS` | | `CROSS` | `CS` |
| `REBUILT_EACH_WITH_STEP` | `REBUILT_STEPS` | | `PERTURBATION` | `PER` |
| `USE_CUSTOM_FILENAMES` | `CUSTOM` | | `REMOVAL` | `REM` |
| | | | `TRANSLATION` | `TRA` |
| | | | `ROTATION` | `ROT` |
| | | | `PERT_AND_REMOVAL` | `PER_REM` |
| | | | `IMPULSIVE_NOISE` | `IN` |

Runs never overwrite each other, and it does not matter from which folder a script is launched.

## Configuring a test

Open `pipeline/config.py` and set the values at the top:

| Setting | What it does |
|---|---|
| `PIPELINE_OPTIONS` | Type of test (see below) |
| `SELECTED_DATASET_OPTION` | Dataset: `CROSS`, `PERTURBATION`, `REMOVAL`, `TRANSLATION`, `ROTATION`, `PERT_AND_REMOVAL`, `IMPULSIVE_NOISE` |
| `DATEIDENTIFIER` | Name of the run, keep it the same to work on the same run folder |
| `NND__SKIP_GENERATION` | `True` to only re-plot nearest-neighbour distances that already exist |
| `NND__SHOW_PLOTS` | `True` to save (and show) the nearest-neighbour violin plot |
| `MCIHELP__N_BATCHES` | Number of batches the MCI is split into |
| `MCIHELP__MIN_RADIUS`, `MCIHELP__MAX_RADIUS`, `MCIHELP__RADIUS_STEP` | Radius range of the MCI (use the recommendation of step 4) |
| `NOISE__COUNTS` | `IMPULSIVE_NOISE` only: numbers of noise points per cloud (`[25, 50, 75, 100]`) |
| `NOISE__SEED_OFFSETS` | `IMPULSIVE_NOISE` only: one noise variation per offset, the seed of its generator is `numpy_choice_rng_seed` of the cloud + offset (`[1, 2, 3, 4]`; 0 is the seed of the blobs and is not used). Other offsets give other reproducible variations |

### Types of test

| `PIPELINE_OPTIONS` | Test | Point sets come from | Steps to run |
|---|---|---|---|
| `MCI_AND_HEATMAPS` | Partial | `input_datasets/<dataset>/` | 3 to 6 |
| `REBUILT_EACH_WITH_STEP` | Full | Generated from `perlin_base_csv_dataset/` | 1 to 6 |
| `USE_CUSTOM_FILENAMES` | Custom | Whatever is set in the `USE_CUSTOM_FILENAMES` section of `config.py` | Any |

In custom tests, the recommended values of the selected dataset are loaded first and only the values written in the `USE_CUSTOM_FILENAMES` section are replaced.

### Datasets

| `SELECTED_DATASET_OPTION` | Partial test input folder | MCI set type | Heatmap |
|---|---|---|---|
| `CROSS` | `input_datasets/cross` | `Cross_Set` | `cross` |
| `PERTURBATION` | `input_datasets/perturbation` | `Perturbation` | `perturbations` |
| `REMOVAL` | `input_datasets/removal` | `Rigid_Transformation` | `removals` |
| `TRANSLATION` | `input_datasets/rigid` | `Rigid_Transformation` | `rigid` |
| `ROTATION` | `input_datasets/rigid` | `Rigid_Transformation` | `rigid` |
| `PERT_AND_REMOVAL` | `input_datasets/pert_and_removal` | `Perturbation` | `per+rem` |
| `IMPULSIVE_NOISE` | `input_datasets/impulsive_noise` | `Impulsive_Noise` | `noise` (bars, no heatmap) |

`input_datasets/base` holds the base point sets the perturbed ones were generated from.

## Steps

Run every command from the project folder.

### Step 1: Generate the base point sets (full tests only)

```bash
python pipeline/generate_perlin_files.py -b 24 -i 0
```

Generates the point sets described in `perlin_base_dataset.csv` (or `perlin_base_dataset_with_removal.csv` for `REMOVAL` and `PERT_AND_REMOVAL`). The rows are processed in batches: `-b` is the batch size and `-i` the batch index, so run `-i 0`, `-i 1`, ... until every row is done (48 rows = 2 batches of 24, 240 rows = 10 batches of 24).

To skip this step with point sets you already have, copy them into the run folder (`perlin_base_point_clouds/`, or `perlin_base_point_clouds_rem/` for removal). Their names must end in `_T(0,0)_R0_.csv`.

### Step 2: Cross or transform the point sets (full tests only)

For `CROSS`:

```bash
python pipeline/generate_cross_perlin_files.py
```

For `PERTURBATION`, `TRANSLATION`, `ROTATION` and `PERT_AND_REMOVAL`:

```bash
python pipeline/generate_transformation_perlin_files.py
```

- Perturbations use the `epsilon` and `main_seed` of each row of `perturbation_transforms.csv`, so the same files are produced on every run.
- Translation and rotation are both applied from `rigid_transforms.csv` in the same step; the heatmaps split them afterwards.
- `REMOVAL` has no step 2, the removal is done in step 1.

For `IMPULSIVE_NOISE` (step 1 is not needed):

```bash
python pipeline/generate_noise_perlin_files.py
```

For each cloud of `perlin_base_dataset.csv` it builds the Perlin field (about 1 minute per cloud, 8 in parallel with `--processes`) and writes one dual cloud per number of noise points and seed offset, `perlin_point_clouds_noise/<cloud>_n<count>s<offset>.csv`: `Type 1` is the clean cloud (the same blobs as step 1) and `Type 2` the same cloud plus the noise points, placed on the white pixels of the field (above the median). For each seed offset the largest count is drawn once and each count takes its first points, so 25 ⊂ 50 ⊂ 75 ⊂ 100. With the default settings: 48 clouds × 4 counts × 4 offsets = 768 dual clouds.

### Step 3: Previews

```bash
python pipeline/generate_previews.py
```

Saves one PNG per point set in `<point set folder>_previews/` inside the run folder.

### Step 4: Nearest-neighbour distances

```bash
python pipeline/generate_nearest_neighbour_distances_files.py
```

Writes the distances and a summary in `dataset_nn_distance_metrics_perlin_<case>_<date>/` inside the run folder, and prints the recommended radius range, for example:

```
Recommended radius range is: minimum radius=8, maximum radius=24
```

Copy those values into `MCIHELP__MIN_RADIUS` and `MCIHELP__MAX_RADIUS`. With `NND__SHOW_PLOTS = True` the violin plot is also saved in that folder.

### Step 5: MCI

```bash
python pipeline/mci_commands_helper.py
```

Prints one command per batch:

```
Batch 0
python ".../mci_lib/processes/mci_process.py" ".../input_datasets/cross" 10 0 8 24 4 "Cross_Set" ".../runs/261021_MCI_HMAPS_CS/MCI"

Batch 1
...
```

Copy each command and run it, each in its own terminal to run the batches in parallel. The arguments are: point set folder, number of batches, batch index, minimum radius, maximum radius, radius step, set type and output folder. The MCI results (a `measurements.csv` per point set) are written into the output folder.

### Step 6: Heatmaps

```bash
python pipeline/heatmap_runner.py
```

Reads the MCI results and saves the heatmaps in `heatmap/<case>/` inside the run folder. Next to each heatmap `<title>.png` it also saves `<title>_matrix.csv`, the matrix with its row and column labels to explore it (pandas, Excel), and `<title>_matrix.png`, the same heatmap with the value written in each cell. Each heatmap is also opened in a window; close it to continue with the next one.

For the perturbation + removal tests it also saves, in `heatmap/per+rem/grids/`, two grids per measurement with the ε of the perturbation on the vertical axis (0 at the bottom) and the % of removal on the horizontal axis, one cell per case: `<measurement> violins.png`, a violin with the 48 point clouds of the case, each point colored by its class (S4, S8, S16, B4816, C416-Coarse, C416-Fine), and `<measurement> bars.png`, one bar per class with the mean of its clouds and its points on top. All the cells of a grid share the same vertical scale. They can also be made alone with `python pipeline/generate_grid_rem_and_pert.py <MCI folder> <output folder>`.

After the grids it saves the compact plot in `heatmap/per+rem/compact/` as `combined_compact.png` (450 dpi) and `combined_compact.svg` (text kept as text, to edit it). It has one row for each removal level of 0, 20 and 60% and one column for each of MCI, HD95, AHD and Sliced Wasserstein, with the ε of the perturbation on the horizontal axis. Each line is the mean of the 8 clouds of a class, and the band around it goes from their minimum to their maximum. The rows of a column share a vertical scale computed from the data, starting at 0. It is made from the `_matrix.csv` files of the per+rem heatmaps, so it can also be made alone after them with `python pipeline/generate_compact_rem_and_pert.py <run folder>/heatmap/per+rem <output folder>`.

For the impulsive noise tests there are no heatmaps: it saves `heatmap/noise/noise_bars.png`, one lane per measurement (MCI, sliced Wasserstein, AHD, HD95, Hausdorff) with, for each point cloud, one bar per number of noise points, each bar the mean of the seed variations, and the means in `noise_bars_mean.csv`. It can also be made alone with `python pipeline/generate_bars_noise.py <MCI folder> <output folder>`.

## Notes

- Windows limits paths to 260 characters. The MCI writes each point set in `MCI/<name>/<name>/<name>_TMST<timestamp>.mp4`, so long point set names reach the limit quickly. Keep the project in a short path directly under the drive (for example `C:\MCI Folder 20261019`), and keep `DATEIDENTIFIER` short (`261021`). When the limit is hit, the batch stops at that point set and every later point set of the batch is skipped.
- `pipeline/plot_nndistances.py`, which plots the nearest-neighbour distances of every case together, still uses fixed folder names and has not been adapted to the run folders yet.
