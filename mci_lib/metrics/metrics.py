'''
Code with the metrics.
'''
import ot
import pandas as pd
import numpy as np
from functools import partial
from scipy.spatial.distance import directed_hausdorff, cdist


def calculate_wasserstein(file,n_estimations=20):
    '''
    Given a dual Perlin cloud, calculates the Sliced Wasserstein Distance to it and returns the min wasserstein value, the maximum and the mean of all
    the estimations perform from the sliced approach (default is 20 attempts).
    '''
    df = pd.read_csv(file) 

    original_points_df = df[df['Type'] == 'Type 1']
    transformed_points_df = df[df['Type'] == 'Type 2']

    coordinates_original_points = original_points_df[['x', 'y']].to_numpy(dtype="float32")
    coordinates_transformed_points = transformed_points_df[['x', 'y']].to_numpy(dtype="float32")

    n_type1 = len(coordinates_original_points)
    n_type2 = len(coordinates_transformed_points)

    values_type1 = np.array([1 / n_type1] * n_type1)
    values_type2 = np.array([1 / n_type2] * n_type2)

    max_was = -np.inf
    min_was = np.inf
    was_list = []
    for s in range(n_estimations):
        wasserstein = ot.sliced_wasserstein_distance(coordinates_original_points,coordinates_transformed_points,values_type1,values_type2,n_projections=50,p=2,seed=s)
        if(wasserstein < min_was):
            min_was = wasserstein
        if(wasserstein > max_was):
            max_was = wasserstein
        was_list.append(wasserstein)
    return min_was,max_was,np.mean(was_list)


def calculate_haussdorf_distances(file):
    '''
    Given a dual Perlin cloud csv file, calculates the:
    - Average Haussdorf Distance
    - 95th Percentile Haussdorf Distance
    '''

    df = pd.read_csv(file) 

    original_points_df = df[df['Type'] == 'Type 1']
    transformed_points_df = df[df['Type'] == 'Type 2']

    coordinates_original_points = original_points_df[['x', 'y']].to_numpy(dtype="float32")
    coordinates_transformed_points = transformed_points_df[['x', 'y']].to_numpy(dtype="float32")

    distance_matrix = cdist(coordinates_original_points,coordinates_transformed_points, metric='euclidean')

    min_dist_O_to_T = np.min(distance_matrix, axis=1)
    min_dist_T_to_O = np.min(distance_matrix, axis=0)
    average_haussdorf_distance = (np.mean(min_dist_O_to_T) + np.mean(min_dist_T_to_O))/2

    p95_O_to_T = np.percentile(min_dist_O_to_T,95)
    p95_T_to_O = np.percentile(min_dist_O_to_T,95)
    haussdorf_95th_percentile_distance = max(p95_O_to_T, p95_T_to_O)

    return average_haussdorf_distance,haussdorf_95th_percentile_distance

