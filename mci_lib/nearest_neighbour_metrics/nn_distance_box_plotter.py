import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os



filters = {
    "Base": lambda file: file.str.contains("_T(0#0)_R0_", regex=False),
    "Removal": lambda file: file.str.contains("%", regex=False),
    "Perturbed": lambda file: file.str.contains("Per_S", regex=False),
    "Perturbed+Removal": lambda file: file.str.contains("Per_S", regex=False) & file.str.contains("%", regex=False),
    "Rotation": lambda file: ~file.str.contains("_T(0#0)_R0_", regex=False) & ~file.str.contains("R0.0", regex=False),
    "Translation": lambda file: ~file.str.contains("_T(0#0)_R0_", regex=False) & ~file.str.contains("T(0.0#0.0)", regex=False),
}

titles = {
    "Base": "Base Perlin Clouds",
    "Removal": "Perlin Clouds with Removal",
    "Perturbed": "Perlin Clouds with Perturbation",
    "Perturbed+Removal": "Perlin Clouds with Removal and Perturbation",
    "Rotation": "Perlin Clouds with Rotation",
    "Translation": "Perlin Clouds with Translation"
}

def apply_file_filter(data,case):
    return data[filters[case](data["File"])]

def nn_distance_violin_plot_by_case(nn_distances_summarized_csv_file,title="Base Perlin Cloud",case ="Base",output_folder="."):
    data = pd.read_csv(nn_distances_summarized_csv_file,delimiter=',')

    title = titles[case]
    
    violin_data = apply_file_filter(data,case)



    if case == "Base":
        violin_data_1nn = violin_data[(violin_data['Column'] == 't1_min_dist_arr')]
        violin_data_2nn = violin_data[(violin_data['Column'] == 't1_min_dist_arr_2nn')]
    else:
        violin_data_1nn = violin_data[(violin_data['Column'] == 't2_min_dist_arr')]
        violin_data_2nn = violin_data[(violin_data['Column'] == 't2_min_dist_arr_2nn')]

    with pd.option_context("display.max_rows", None, "display.max_colwidth", None):
        print("1NN")
        print(violin_data_1nn["File"])
        print(len(violin_data_1nn["File"]))

    with pd.option_context("display.max_rows", None, "display.max_colwidth", None):
        print("2NN")
        print(violin_data_2nn["File"])
        print(len(violin_data_2nn["File"]))

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 3, 1)
    sns.violinplot(y='Raw Mode (int)', data=violin_data_1nn,cut=0)
    plt.title(f'Mode of 1NN \n between points of the \n {title}')
    plt.ylabel('Mode')
    
    plt.subplot(2, 3, 2)
    sns.violinplot(y='95th Percentile', data=violin_data_1nn, cut=0)
    plt.title(f'95th Percentile of 1NN \n between points of the \n {title}')
    plt.ylabel('95th Percentile')
    
    
    plt.subplot(2, 3, 3)
    sns.violinplot(y='5th Percentile', data=violin_data_1nn, cut=0)
    plt.title(f'5th Percentile of 1NN \n between points of the \n {title}')
    plt.ylabel('5th Percentile')

    plt.subplot(2, 3, 4)
    sns.violinplot(y='Raw Mode (int)', data=violin_data_2nn,cut=0)
    plt.title(f'Mode of 2NN \n between points of the \n {title}')
    plt.ylabel('Mode')

    plt.subplot(2, 3, 5)
    sns.violinplot(y='95th Percentile', data=violin_data_2nn, cut=0)
    plt.title(f'95th Percentile of 2NN \n between points of the \n {title}')
    plt.ylabel('95th Percentile')


    plt.subplot(2, 3, 6)
    sns.violinplot(y='5th Percentile', data=violin_data_2nn, cut=0)
    plt.title(f'5th Percentile of 2NN \n between points of the \n {title}')
    plt.ylabel('5th Percentile')

    plt.tight_layout(pad=3.0)
    plt.savefig(os.path.join(output_folder,f'nndist_plot_{title}_v2.png'))
    plt.show()



def nn_distance_violin_plot_new(nn_distances_summarized_csv_file,title="Base Perlin Cloud"):
    data = pd.read_csv(nn_distances_summarized_csv_file,delimiter=',')
    both_types_1nn = data[(data['Column'] == 't1_min_dist_arr') | (data['Column'] == 't2_min_dist_arr')]
    both_types_2nn = data[(data['Column'] == 't1_min_dist_arr_2nn') | (data['Column'] == 't2_min_dist_arr_2nn')]

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 3, 1)
    sns.violinplot(y='Raw Mode (int)', data=both_types_1nn,cut=0)
    plt.title(f'Mode of 1NN \n between points of the \n {title}')
    plt.ylabel('Mode')

    plt.subplot(2, 3, 2)
    sns.violinplot(y='95th Percentile', data=both_types_1nn, cut=0)
    plt.title(f'95th Percentile of 1NN \n between points of the \n {title}')
    plt.ylabel('95th Percentile')


    plt.subplot(2, 3, 3)
    sns.violinplot(y='5th Percentile', data=both_types_1nn, cut=0)
    plt.title(f'5th Percentile of 1NN \n between points of the \n {title}')
    plt.ylabel('5th Percentile')


    plt.subplot(2, 3, 4)
    sns.violinplot(y='Raw Mode (int)', data=both_types_2nn,cut=0)
    plt.title(f'Mode of 2NN \n between points of the \n {title}')
    plt.ylabel('Mode')

    plt.subplot(2, 3, 5)
    sns.violinplot(y='95th Percentile', data=both_types_2nn, cut=0)
    plt.title(f'95th Percentile of 2NN \n between points of the \n {title}')
    plt.ylabel('95th Percentile')


    plt.subplot(2, 3, 6)
    sns.violinplot(y='5th Percentile', data=both_types_2nn, cut=0)
    plt.title(f'5th Percentile of 2NN \n between points of the \n {title}')
    plt.ylabel('5th Percentile')

    plt.tight_layout()
    plt.savefig(f'nndist_plot_{title}.png')
    plt.show()

def nn_distance_violin_plot_old(nn_distances_summarized_csv_file):
    data = pd.read_csv(nn_distances_summarized_csv_file,delimiter=',')
    type_A_data = data[data['Column'] == 't1_min_dist_arr']
    type_B_data = data[data['Column'] == 't2_min_dist_arr']

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 3, 1)
    sns.violinplot(y='Raw Mode (int)', data=type_A_data,cut=0)
    plt.title('Mode of nearest neighbour distance \n between points of the original Perlin Cloud')
    plt.ylabel('Mode')

    plt.subplot(2, 3, 2)
    sns.violinplot(y='95th Percentile', data=type_A_data, cut=0)
    plt.title('95th Percentile of nearest neighbour distance \n between points of the original Perlin Cloud')
    plt.ylabel('95th Percentile')


    plt.subplot(2, 3, 3)
    sns.violinplot(y='5th Percentile', data=type_A_data, cut=0)
    plt.title('5th Percentile of nearest neighbour distance \n between points of the original Perlin Cloud')
    plt.ylabel('5th Percentile')


    plt.subplot(2, 3, 4)
    sns.violinplot(y='Raw Mode (int)', data=type_B_data,cut=0)
    plt.title('Mode of nearest neighbour distance \n between points of the transformed Perlin Cloud')
    plt.ylabel('e')

    plt.subplot(2, 3, 5)
    sns.violinplot(y='95th Percentile', data=type_B_data,cut=0)
    plt.title('95th Percentile of nearest neighbour distance \n between points of the transformed Perlin Cloud')
    plt.ylabel('95th Percentile')

    plt.subplot(2, 3, 6)
    sns.violinplot(y='5th Percentile', data=type_B_data, cut=0)
    plt.title('5th Percentile of nearest neighbour distance \n between points of the transformed Perlin Cloud')
    plt.ylabel('5th Percentile')


    plt.tight_layout()
    plt.show()