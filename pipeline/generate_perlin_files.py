import pandas as pd
from mci_lib.point_set_generation.point_set_generation import *
import os


DEFAULT_BASE_POINT_CLOUD_FOLDER = 'perlin_base_point_clouds_debug'

DEFAULT_DATASET_CSV_FILE  = 'perlin_base_dataset_20260920.csv'

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
python_local_path = os.path.dirname(os.path.dirname(__file__))
perlin_base_dataset_path = os.path.join(python_local_path,'perlin_base_csv_dataset',DEFAULT_DATASET_CSV_FILE)
rigid_transforms_path = os.path.join(python_local_path,'perlin_base_csv_dataset','rigid_transforms.csv')


df_perlin = pd.read_csv(perlin_base_dataset_path).astype(str)

df_rigid_transforms = pd.read_csv(rigid_transforms_path).astype(str)

output_folder = os.path.join(python_local_path,DEFAULT_BASE_POINT_CLOUD_FOLDER)

unaltered_rigid_transform = RigidTransformation([0,0],0)



width, height = 1000,1000


for _, row_perlin in df_perlin.iterrows():
    name = row_perlin['name']
    perlin_type = PerlinType[row_perlin['perlin_type']]
    perlin_weights = semicolon_list_converter_to_float_list(row_perlin['perlin_weights'])
    seed_array = semicolon_list_converter_to_int_list(row_perlin['seed_array'])
    octave_array = semicolon_list_converter_to_int_list(row_perlin['octave_array'])
    t1_point_density = float(row_perlin['t1_point_density'])
    t2_rigid_loss = float(row_perlin['t2_rigid_loss'])

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
        csv_name = csv_name
    )
    print(width,height,
        perlin_func,
        ['Type 1','Type 2'],
        unaltered_rigid_transform,
        t1_point_density,
        t2_rigid_loss,
        output_folder+"_".join([name,"T(0,0)_R0"]),
        0.2
        )

    unaltered_dual_perlin_cloud.process_pipeline()

