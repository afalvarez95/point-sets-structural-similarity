# MCI notebook for your own point clouds

[`mci_custom_clouds.ipynb`](mci_custom_clouds.ipynb) computes the MCI of a pair of point sets (a *dual cloud*) that you provide, and shows the results: the MCI value, the other measurements of the pipeline (AHD, HD95, Hausdorff and Sliced Wasserstein), the $J_\delta$ per radius, its plot and the frames of the closings (optionally also their video, see [Video of the closings](#video-of-the-closings)).

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
   - a table with the MCI and the other measurements: AHD (average Hausdorff), HD95 (95th percentile Hausdorff), Hausdorff and Sliced Wasserstein (mean of 20 estimates of 50 projections). They are computed by `other_measurements(A, B)`, the same code as `mci_process.py`,
   - the plot `<name>_jd_per_r_plot.png`,
   - the video `<name>.mp4`, only when `SAVE_VIDEO = True` (otherwise it says where the frames are).

`show_results(name)` shows a dual cloud already computed again, without recomputing it.

`compare_results([name_1, name_2, ...])` shows one table with the MCI, AHD, HD95, Hausdorff and Sliced Wasserstein of dual clouds already computed, and saves it in `outputs/comparison_metrics.csv` (`file_name` changes the name).

## Video of the closings

By default (`SAVE_VIDEO = False` in the **Setup** cell) the notebook saves only the frames of the closings, one PNG per radius in `outputs/<name>/<name>/frames/`, and does not render the video. This way it runs without ffmpeg, and the MCI and the other results are exactly the same.

To also render the video `<name>.mp4`:

1. Install ffmpeg and check that it is on the `PATH` (a new terminal should print its version):

   ```bash
   ffmpeg -version
   ```

   On Windows, download a build from https://ffmpeg.org/download.html, unzip it (for example to `C:\FFmpeg`) and add its `bin` folder (`C:\FFmpeg\bin`) to the `PATH` environment variable. Then restart Jupyter or VS Code so it sees the new `PATH`.
2. In the **Setup** cell, set `SAVE_VIDEO = True` and run the **Setup** and **Helpers** cells again.
3. Run `run_mci(...)` again for each dual cloud that needs its video (or switch `SAVE_VIDEO` back to `False` for the ones that do not).

If ffmpeg is still not found, matplotlib can be pointed to it directly in the **Setup** cell:

```python
plt.rcParams["animation.ffmpeg_path"] = r"C:\FFmpeg\bin\ffmpeg.exe"
```

## Output

Each dual cloud is saved in `notebook/outputs/<name>/` (not tracked in git):

```
outputs/<name>/
├── measurements.csv               (name, number of points, AHD, HD95, Hausdorff, Sliced Wasserstein, jd_r, mci; same column names as the pipeline)
└── <name>/
    ├── <name>.mp4                 (video of the closings, one frame per radius, only with SAVE_VIDEO = True)
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
- With `SAVE_VIDEO = True` the videos are embedded in the notebook when they are shown, so a saved notebook with outputs can get large. Clear the outputs before sharing it.
