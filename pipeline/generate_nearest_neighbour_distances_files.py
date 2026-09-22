from mci_lib.nearest_neighbour_metrics.nn_distance import calculate_nearest_neighbour_distance_distribution_from_folder
from mci_lib.nearest_neighbour_metrics.nn_distance_summarizer import summarize_nn_distances_from_folder, offer_radius_ranges_recommendation
from mci_lib.nearest_neighbour_metrics.nn_distance_box_plotter import nn_distance_violin_plot

import os


SKIP_GENERATION = False

SHOW_PLOT = True

TRANSFORMED_POINT_CLOUD_FOLDER_NAME = 'perlin_transformed_point_clouds'

NN_DISTANCES_FOLDER_NAME = 'dataset_nn_distance_metrics'

NN_DISTANCES_SUMMARIZED_FOLDER_NAME = 'dataset_nn_summarized_distance_metrics'

SUMMARIZED_STATS_FILE_NAME = 'statistics_all_files.csv'

python_local_path = os.path.dirname(os.path.dirname(__file__))
transformed_point_cloud_folder = os.path.join(python_local_path,TRANSFORMED_POINT_CLOUD_FOLDER_NAME)
nn_distances_folder = os.path.join(python_local_path,NN_DISTANCES_FOLDER_NAME)
nn_distances_summarized_name = os.path.join(python_local_path,NN_DISTANCES_SUMMARIZED_FOLDER_NAME)

if(not SKIP_GENERATION):
    calculate_nearest_neighbour_distance_distribution_from_folder(transformed_point_cloud_folder,nn_distances_folder)
    summarize_nn_distances_from_folder(nn_distances_folder,nn_distances_summarized_name,SUMMARIZED_STATS_FILE_NAME)

if(SHOW_PLOT):
    nn_distance_violin_plot(f"{nn_distances_summarized_name}/{SUMMARIZED_STATS_FILE_NAME}")

offer_radius_ranges_recommendation(nn_distances_summarized_name,SUMMARIZED_STATS_FILE_NAME)