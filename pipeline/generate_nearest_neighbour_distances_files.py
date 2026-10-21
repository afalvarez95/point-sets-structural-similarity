from mci_lib.nearest_neighbour_metrics.nn_distance import calculate_nearest_neighbour_distance_distribution_from_folder
from mci_lib.nearest_neighbour_metrics.nn_distance_summarizer import summarize_nn_distances_from_folder, offer_radius_ranges_recommendation
from mci_lib.nearest_neighbour_metrics.nn_distance_box_plotter import nn_distance_violin_plot_by_case

from config import (NND__ANALYSIS_DATE,
                    
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__BASE,
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__REMOVAL,
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PERTURBED,
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PER_REM,
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__ROTATION,
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__TRANSLATION,

NND__CURRENT_CASE_IDX,
NND__SKIP_GENERATION,
NND__SHOW_PLOTS,
WORK_DIR)

import os

titles = {
    "Base": "Base Perlin Clouds",
    "Removal": "Perlin Clouds with Removal",
    "Perturbed": "Perlin Clouds with Perturbation",
    "Perturbed+Removal": "Perlin Clouds with Removal and Perturbation",
    "Rotation": "Perlin Clouds with Rotation",
    "Translation": "Perlin Clouds with Translation"
}


DATE = NND__ANALYSIS_DATE

TRANSFORMED_POINT_CLOUD_FOLDER_NAMES = {
    "Base": NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__BASE,
    "Removal": NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__REMOVAL,
    "Perturbed": NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PERTURBED,
    "Perturbed+Removal": NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PER_REM,
    "Rotation": NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__ROTATION,
    "Translation": NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__TRANSLATION
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

SKIP_GENERATION = NND__SKIP_GENERATION

SHOW_PLOT = NND__SHOW_PLOTS

case = list(TRANSFORMED_POINT_CLOUD_FOLDER_NAMES)[NND__CURRENT_CASE_IDX]
# case = list(TRANSFORMED_POINT_CLOUD_FOLDER_NAMES)[3]

TRANSFORMED_POINT_CLOUD_FOLDER_NAME = TRANSFORMED_POINT_CLOUD_FOLDER_NAMES[case]

NN_DISTANCES_FOLDER_NAME = NN_DISTANCES_FOLDER_NAMES[case]

NN_DISTANCES_SUMMARIZED_FOLDER_NAME = NN_DISTANCES_FOLDER_NAMES[case]

SUMMARIZED_STATS_FILE_NAME = SUMMARIZED_STATS_FILE_NAMES[case]



python_local_path = str(WORK_DIR)
os.makedirs(python_local_path, exist_ok=True)
transformed_point_cloud_folder = str(TRANSFORMED_POINT_CLOUD_FOLDER_NAME)
nn_distances_folder = os.path.join(python_local_path,NN_DISTANCES_FOLDER_NAME)
nn_distances_summarized_name = os.path.join(python_local_path,NN_DISTANCES_SUMMARIZED_FOLDER_NAME)

if(not SKIP_GENERATION):
    calculate_nearest_neighbour_distance_distribution_from_folder(transformed_point_cloud_folder,nn_distances_folder)
    summarize_nn_distances_from_folder(nn_distances_folder,nn_distances_summarized_name,SUMMARIZED_STATS_FILE_NAME)

if(SHOW_PLOT):
    nn_distance_violin_plot_by_case(f"{nn_distances_summarized_name}/{SUMMARIZED_STATS_FILE_NAME}",case=case,output_folder=nn_distances_summarized_name)

offer_radius_ranges_recommendation(nn_distances_summarized_name,SUMMARIZED_STATS_FILE_NAME)