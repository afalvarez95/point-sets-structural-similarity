from mci_lib.nearest_neighbour_metrics.nn_distance_box_plotter import nn_distance_violin_plot_by_case

import os



SHOW_PLOT = True



DATE = "20261016"

TRANSFORMED_POINT_CLOUD_FOLDER_NAMES = {
    "Base": 'perlin_base_point_clouds_20261006',
    "Removal": 'perlin_base_point_clouds_20261010_rem',
    "Perturbed": "perlin_perturbed_point_clouds_20261010",
    "Perturbed+Removal": "perlin_perturbed_point_clouds_20261010_rem",
    "Rotation": "perlin_point_clouds_20261013_rigid",
    "Translation": "perlin_point_clouds_20261013_rigid"
}

NN_DISTANCES_FOLDER_NAMES = {
    "Base": f'dataset_nn_distance_metrics_perlin_base_{DATE}',
    "Removal": f'dataset_nn_distance_metrics_perlin_rem_{DATE}',
    "Perturbed": f'dataset_nn_distance_metrics_perlin_pert_{DATE}',
    "Perturbed+Removal": f'dataset_nn_distance_metrics_perlin_pert_rem_{DATE}',
    "Rotation": f'dataset_nn_distance_metrics_perlin_rigid_{DATE}',
    "Translation": f'dataset_nn_distance_metrics_perlin_rigid_{DATE}',
}

SUMMARIZED_STATS_FILE_NAMES = {
    "Base": f'nndist_stats_perlin_base_{DATE}',
    "Removal": f'nndist_stats_perlin_rem_{DATE}',
    "Perturbed": f'nndist_stats_perlin_pert_{DATE}',
    "Perturbed+Removal": f'nndist_stats_perlin_pert_rem_{DATE}',
    "Rotation": f'nndist_stats_perlin_rigid_{DATE}',
    "Translation": f'nndist_stats_perlin_rigid_{DATE}',
}

cases = SUMMARIZED_STATS_FILE_NAMES.keys()




for case in cases:
    python_local_path = os.path.dirname(os.path.dirname(__file__))
    SUMMARIZED_STATS_FILE_NAME = SUMMARIZED_STATS_FILE_NAMES[case]
    NN_DISTANCES_SUMMARIZED_FOLDER_NAME= NN_DISTANCES_FOLDER_NAMES[case]
    nn_distances_summarized_name = os.path.join(python_local_path,NN_DISTANCES_SUMMARIZED_FOLDER_NAME)

    nn_distance_violin_plot_by_case(f"{nn_distances_summarized_name}/{SUMMARIZED_STATS_FILE_NAME}",case=case,title=None)
