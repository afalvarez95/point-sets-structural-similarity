import pandas as pd
import numpy as np
from scipy import stats
import os
import math

def summarize_nn_distances_from_file(df, total_stats,filename):
    df = df.replace(np.inf, np.nan)
    stats_list = []

    for column in ['t1_min_dist_arr', 't2_min_dist_arr', 'cross_min_dist_arr','t1_min_dist_arr_2nn', 't2_min_dist_arr_2nn', 'cross_min_dist_arr_2nn']:
        
        mode_bins = pd.cut(df[column], bins=np.arange(0, 1415, 5))
        mode = mode_bins.value_counts().idxmax()
        
        if(len(df[column].mode()) > 1):
            raw_mode = df[column].mode()[0]
            raw_mode_int = df[column].replace([np.inf, -np.inf], np.nan).dropna().round().astype(int).mode()[0]
        elif(len(df[column].mode()) == 1):
            raw_mode = df[column].mode()[0]
            raw_mode_int = df[column].replace([np.inf, -np.inf], np.nan).dropna().round().astype(int).mode()[0]
        else:
            raw_mode = 'NA'
            raw_mode_int = 'NA'

        median = df[column].median()
        mean = df[column].mean()
        std_dev = df[column].std()
        quantile_95 = df[column].quantile(0.95)
        quantile_05 = df[column].quantile(0.05)
        stats_list.append({
            'File': filename.replace(',',"#"),
            'Column': column,
            'Mode interval': mode,
            'Raw Mode (float)': raw_mode,
            'Raw Mode (int)': raw_mode_int,
            'Median': median,
            'Mean': mean,
            'Std Dev': std_dev,
            '5th Percentile': quantile_05,
            '95th Percentile': quantile_95
        })

    stats_df = pd.DataFrame(stats_list)

    total_stats = pd.concat([total_stats, stats_df], ignore_index=True)

    return total_stats


#summarize_nn_distances_from_folder(perlin_distances_folder, perlin_distances_summarized_folder)
def summarize_nn_distances_from_folder(input_directory,output_directory,stats_filename='statistics_all_files.csv'):
    '''
    Summarizes nearest neighbour distances from a folder.
    '''
    os.makedirs(output_directory, exist_ok=True)

    all_results = pd.DataFrame()
    counter = 0
    for file in os.listdir(input_directory):
        if file.endswith('.csv'):
            print(f"Summarizing: {file}")
            filepath = os.path.join(input_directory, file)
            df = pd.read_csv(filepath)
            all_results = summarize_nn_distances_from_file(df,all_results,file)
            counter+=1
            print("Files done: ", counter)
    result_df = all_results
    output_filepath = os.path.join(output_directory, stats_filename)
    result_df.to_csv(output_filepath, index=False)


def offer_radius_ranges_recommendation(input_directory,stats_file_name='statistics_all_files.csv'):
    statistics_file = os.path.join(input_directory, stats_file_name)
    df_stats = pd.read_csv(statistics_file)
    t1_name_1nn,t2_name_1nn = 't1_min_dist_arr','t2_min_dist_arr'
    t1_and_t2_names_1nn = [t1_name_1nn,t2_name_1nn]
    t1_or_t2_df_1nn = df_stats.loc[df_stats['Column'].isin(t1_and_t2_names_1nn)]


    t1_name_2nn,t2_name_2nn = 't1_min_dist_arr_2nn','t2_min_dist_arr_2nn'
    t1_and_t2_names_2nn = [t1_name_2nn,t2_name_2nn]
    t1_or_t2_df_2nn = df_stats.loc[df_stats['Column'].isin(t1_and_t2_names_2nn)]

    max_5th_percentile_2nn_t1_or_t2 = t1_or_t2_df_2nn['5th Percentile'].max()

    max_95th_percentile_2nn_t1_or_t2 = t1_or_t2_df_2nn['95th Percentile'].max()

    min_radius = math.ceil(max_5th_percentile_2nn_t1_or_t2 / 4) * 4
    max_radius = math.ceil(max_95th_percentile_2nn_t1_or_t2 / 4) * 4

    print(f"Recommended radius range is: minimum radius={min_radius}, maximum radius={max_radius}")
