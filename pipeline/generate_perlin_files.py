import pandas as pd
from mci_lib.point_set_generation.point_set_generation import *
import os
import argparse
from config import PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER, PFG__DEFAULT_DATASET_CSV_FILE

DEFAULT_BASE_POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER

DEFAULT_DATASET_CSV_FILE = PFG__DEFAULT_DATASET_CSV_FILE

def semicolon_list_converter_to_int_list(string: str):
    print(string)
    if string == 'nan':
        return None
    if len(string.split(';')) == 1:
        return [int(string[1:-1])]
    else:
        return [int(x) for x in string[1:-1].split(';')]
    
def semicolon_list_converter_to_float_list(string: str):
    print(string)
    if string == 'nan':
        return None
    if len(string.split(';')) == 1:
        return [float(string[1:-1])]
    else:
        return [float(x) for x in string[1:-1].split(';')]    


#This file is the first step to generate the perlin base images: aka, the images without any rigid transformation.
#These are generated with the perlin_base_dataset.csv file.
perlin_base_dataset_path = DEFAULT_DATASET_CSV_FILE

df_perlin = pd.read_csv(perlin_base_dataset_path).astype(str)


output_folder = str(DEFAULT_BASE_POINT_CLOUD_FOLDER)
os.makedirs(output_folder, exist_ok=True)

unaltered_rigid_transform = RigidTransformation([0,0],0)



width, height = 1000,1000

parser = argparse.ArgumentParser()

parser.add_argument("-b","--batch-size",type=int,default=24)
parser.add_argument("-i","--index",type=int,default=0)

args = parser.parse_args()

start = args.index * args.batch_size
df_batch_perlin = df_perlin.iloc[start:start + args.batch_size]

for _, row_perlin in df_batch_perlin.iterrows():
    name = row_perlin['name']
    perlin_type = PerlinType[row_perlin['perlin_type']]
    perlin_weights = semicolon_list_converter_to_float_list(row_perlin['perlin_weights'])
    seed_array = semicolon_list_converter_to_int_list(row_perlin['seed_array'])
    octave_array = semicolon_list_converter_to_int_list(row_perlin['octave_array'])
    t1_point_density = float(row_perlin['t1_point_density'])
    t2_rigid_loss = float(row_perlin['t2_rigid_loss'])
    numpy_choice_rng_seed = int(row_perlin['numpy_choice_rng_seed'])

    print(perlin_type,seed_array,octave_array,perlin_weights)

    perlin_func = PerlinFunc(perlin_type,seed_array,octave_array,custom_weights=perlin_weights)

    csv_name = str(output_folder+"\\"+"_".join([name,"T(0,0)_R0",'.csv']))

    unaltered_dual_perlin_cloud = DualPerlinCloud(
        width,
        height,
        perlin_func,
        ['Type 1','Type 2'],
        unaltered_rigid_transform,
        t1_point_density,
        t2_rigid_loss,
        csv_name = csv_name,
        point_sampling_seed=numpy_choice_rng_seed
    )
    print(width,height,
        perlin_func,
        ['Type 1','Type 2'],
        unaltered_rigid_transform,
        t1_point_density,
        t2_rigid_loss,
        output_folder+"_".join([name,"T(0,0)_R0"]),
        numpy_choice_rng_seed
        )

    unaltered_dual_perlin_cloud.process_pipeline()

