import pandas as pd
import numpy as np
import math
import glob
import os
from pathlib import Path


def calculate_nearest_neighbour_distance_distribution_from_folder(csv_folder,output_folder: str | Path):
    '''
    Calculates the nearest neighbour distance distribution using a folder which contains
    all the pair of Perlin clouds csv files.
    '''
    output_folder = Path(output_folder)

    output_folder.mkdir(exist_ok=True)  
    csv_files = glob.glob(f"{csv_folder}/*.csv")
    number_csv_files = len(csv_files)
    file_count = 0
    for current_csv_file in csv_files:
        calculate_nearest_neighbour_distance_distribution_from_file(current_csv_file,output_folder)
        file_count+=1
        print("Files done: ",file_count,"/",number_csv_files)
        

def calculate_nearest_neighbour_distance_distribution_from_file(current_csv_file,output_folder):
    filename = os.path.basename(current_csv_file)

    df = pd.read_csv(current_csv_file)
    df_filtered = df[['x', 'y', 'Type']]
    df_filtered = df_filtered[df_filtered['Type'].isin(['Type 1', 'Type 2'])]
    df_filtered.reset_index(drop=True, inplace=True)

    coords = df_filtered[['x', 'y']].to_numpy()
    cases = df_filtered['Type'].to_numpy()

    t1_min_dist_arr = np.full(len(df_filtered), np.inf)
    t2_min_dist_arr = np.full(len(df_filtered), np.inf)
    cross_min_dist_arr = np.full(len(df_filtered), np.inf)

    for i in range(len(df_filtered)):
        x, y, case_type = coords[i][0], coords[i][1], cases[i]
        
        if i < len(df_filtered) - 1:
            future_coords = coords[i + 1:]
            future_cases = cases[i + 1:]

            distances = np.linalg.norm(future_coords - np.array([x, y]), axis=1)

            if(case_type == 'Type 1'):
                t1_mask = (future_cases == 'Type 1')
                t1_min_dist_arr[i] = np.min(distances[t1_mask], initial=np.inf)

            if(case_type == 'Type 2'):
                t2_mask = (future_cases == 'Type 2')
                t2_min_dist_arr[i] = np.min(distances[t2_mask], initial=np.inf)

            cross_mask = (future_cases != case_type)
            cross_min_dist_arr[i] = np.min(distances[cross_mask], initial=np.inf)
    result_csv = pd.DataFrame({
        'number_id': range(1, len(t1_min_dist_arr) + 1),
        't1_min_dist_arr': t1_min_dist_arr,
        't2_min_dist_arr': t2_min_dist_arr,
        'cross_min_dist_arr': cross_min_dist_arr
    })
    
    result_csv.to_csv(os.path.join(output_folder,filename), index=False)

