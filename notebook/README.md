# MCI notebook for your own point clouds

[`mci_custom_clouds.ipynb`](mci_custom_clouds.ipynb) computes the MCI of a pair of point sets (a *dual cloud*) that you provide, and shows the results: the MCI value, the $J_\delta$ per radius, its plot and the video of the closings.

It uses the same code as the pipeline (`mci_lib`), so a dual cloud gives the same MCI here and in the pipeline.

## Setup

From the project folder, once:

```bash
pip install -r requirements.txt
```

Then open the notebook from this `notebook/` folder (JupyterLab, Jupyter Notebook or VS Code). It finds the project folder by itself, so `mci_lib` does not need to be installed.

## How to use it

1. Run the **Setup** and **Helpers** cells.
2. Load your dual cloud with one of the three options (each one has a working example of the project already filled in):

| Option | Input | Helper |
|---|---|---|
| 1 | One `.csv` with the columns `x`, `y`, `Type` (`Type 1` = first point set, `Type 2` = second point set), the format of every point set file of the pipeline | `load_dual_cloud_csv(path, label_1="Type 1", label_2="Type 2")` |
| 2 | Two NumPy arrays of shape (N, 2) with the `x`, `y` coordinates | none, use the arrays directly |
| 3 | Two files, one per point set: a `.csv` with the columns `x`, `y` (with a `Type` column, `label` chooses the rows) or a `.npy` with an (N, 2) array | `load_point_set(path, label=None)` |

3. Check the point sets with `preview(A, B, name)`.
4. Optionally run `recommend_radius_range(A, B)`: it prints the radius range recommended from the nearest neighbour distances, the same recommendation as step 4 of the pipeline.
5. Run `run_mci(A, B, name, min_radius, max_radius, radius_step)`. It computes the MCI and shows:
   - the MCI value,
   - the table of $J_\delta$ per radius,
   - the plot `<name>_jd_per_r_plot.png`,
   - the video `<name>.mp4`.

`show_results(name)` shows a dual cloud already computed again, without recomputing it.

## Output

Each dual cloud is saved in `notebook/outputs/<name>/` (not tracked in git):

```
outputs/<name>/
├── measurements.csv               (name, number of points, mci, jd_r)
└── <name>/
    ├── <name>.mp4                 (video of the closings, one frame per radius)
    ├── <name>_jd_per_r_plot.png   (J_delta per radius, AUC in red)
    └── frames/frame_<i>.png
```

Running `run_mci` again with the same name replaces that folder.

## Examples of the notebook

| Option | Example | Radius | MCI |
|---|---|---|---|
| 1 | `input_datasets/perturbation/B4816-1-A_Per_S_700003_E_40.0.csv` | 8–32, step 4 | 0.6434 (same as the pipeline) |
| 2 | 500 random points, the second set moved with a normal noise of σ = 5 | 16–64, step 8 | 0.3673 |
| 3 | `input_datasets/base/S4-1-A…` and `S4-1-B…` | 8–24, step 4 | 0.5484 (same as the cross heatmap) |

## Notes

- The coordinates are used as they are (no scaling), so the radii are in the same units as your points.
- The MCI is 0 when both point sets are the same, and grows up to 1 as they differ.
- `name` is used as a folder and file name: use only letters, numbers, `-` and `_`, and keep it short (Windows limits paths to 260 characters).
- The videos are embedded in the notebook when they are shown, so a saved notebook with outputs can get large. Clear the outputs before sharing it.
