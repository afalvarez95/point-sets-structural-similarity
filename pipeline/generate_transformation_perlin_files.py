import os
from mci_lib.point_set_generation.point_set_generation import RigidTransformation,DualPerlinCloud,PerturbationTransformation
import pandas as pd
import shutil
#This file is the second step to generate the files which are the perlin clouds after a series of rigid transformation.
#These are performed with the rigid_transforms.csv file.


DEFAULT_BASE_POINT_CLOUD_FOLDER = 'perlin_base_point_clouds'

DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = 'perlin_transformed_point_clouds'
option = "Translation_Rotation"

python_local_path = os.path.dirname(os.path.dirname(__file__))
perlin_dataset_folder_path = os.path.join(python_local_path,DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER)

os.makedirs(DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER, exist_ok=True)


for file in os.listdir(DEFAULT_BASE_POINT_CLOUD_FOLDER):
    ruta_origen = os.path.join(DEFAULT_BASE_POINT_CLOUD_FOLDER, file)
    
    if os.path.isfile(ruta_origen):
        shutil.copy(ruta_origen, DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER)
        print(f'Copied base perlin file: {file}')

if(option == "Translation_Rotation"):
    transforms_path = os.path.join(python_local_path,'perlin_base_csv_dataset','rigid_transforms.csv')
else:
    transforms_path = os.path.join(python_local_path,'perlin_base_csv_dataset','perturbation_transforms.csv')


df_transforms_path = pd.read_csv(transforms_path).astype(str)




for filename in os.listdir(perlin_dataset_folder_path):
    if filename.endswith('_T(0,0)_R0_.csv'):
        file_path = os.path.join(perlin_dataset_folder_path, filename)
        print(f'Transforming points of: {file_path}, using option: {option}' )

        for _, row_tra in df_transforms_path.iterrows():
            if(option == "Translation_Rotation"):
                translation_x = float(row_tra['translation_x'])
                translation_y = float(row_tra['translation_y'])
                rotation = float(row_tra['rotation_angle'])
                rigid_transform_name = "T("+str(translation_x)+","+str(translation_y)+")_R"+str(rotation)+'.csv'
                file_for_csv = file_path.replace('_T(0,0)_R0_.csv','')
                csv_name_ = "_".join([file_for_csv,rigid_transform_name])
                rigid_transform = RigidTransformation([translation_x,translation_y],rotation)
                dpc = DualPerlinCloud(width_im=1000,height_im=1000,csv_name=csv_name_,transformation=rigid_transform,point_labels=['Type 1','Type 2'])
            else:
                epsilon = float(row_tra['epsilon'])
                main_seed = int(row_tra['main_seed'])
                perturbation_transform_name = f"Per_S_{main_seed}_E_{epsilon}.csv"
                file_for_csv = file_path.replace('_T(0,0)_R0_.csv','')
                csv_name_ = "_".join([file_for_csv,perturbation_transform_name])
                perturbation_transform = PerturbationTransformation(epsilon=epsilon,main_seed=main_seed)
                dpc = DualPerlinCloud(width_im=1000,height_im=1000,csv_name=csv_name_,transformation=perturbation_transform,point_labels=['Type 1','Type 2'])

            dpc.load_perlin_cloud_from_file(file_path)
            dpc.perform_transformation_from_points()
            dpc.generate_csv()
