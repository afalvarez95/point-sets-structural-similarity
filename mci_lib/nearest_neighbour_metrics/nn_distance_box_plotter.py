import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os



def nn_distance_violin_plot(nn_distances_summarized_csv_file):
    data = pd.read_csv(nn_distances_summarized_csv_file,delimiter=',')
    type_A_data = data[data['Column'] == 't1_min_dist_arr']
    type_B_data = data[data['Column'] == 't2_min_dist_arr']

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    sns.violinplot(y='Raw Mode (int)', data=type_A_data,cut=0)
    plt.title('Mode of nearest neighbour distance between points of the original Perlin Cloud')
    plt.ylabel('Mode')

    plt.subplot(2, 2, 2)
    sns.violinplot(y='95th Percentile', data=type_A_data, cut=0)
    plt.title('95th Percentile of nearest neighbour distance between points of the original Perlin Cloud')
    plt.ylabel('95th Percentile')


    plt.subplot(2, 2, 3)
    sns.violinplot(y='Raw Mode (int)', data=type_B_data,cut=0)
    plt.title('Mode of nearest neighbour distance between points of the transformed Perlin Cloud')
    plt.ylabel('e')

    plt.subplot(2, 2, 4)
    sns.violinplot(y='95th Percentile', data=type_B_data,cut=0)
    plt.title('95th Percentile of nearest neighbour distance between points of the transformed Perlin Cloud')
    plt.ylabel('95th Percentile')


    plt.tight_layout()
    plt.show()