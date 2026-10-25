from pathlib import Path
import math
import os
import ot
from mci_lib.metrics.metrics import calculate_haussdorf_distances, calculate_wasserstein
import pandas as pd
import numpy as np
import time
from mci_lib.mci.core import RigidTransform, MCITestFamily, BatchMCITester, PerturbationTransform
import sys
from pathlib import Path
from enum import Enum
import traceback




class DatasetType(Enum):
    PERTURBATION = "Perturbation"
    RIGID_TRANSFORMATION = "Rigid_Transformation"
    BOTH = "Both"
    CROSS_SET = "Cross_Set"
    IMPULSIVE_NOISE = "Impulsive_Noise"

def list_csv_files(perlin_folder):

    return list(sorted(perlin_folder.glob("*.csv")))

def read_points_perlin_file(perlin_file):
    df = pd.read_csv(perlin_file)

    type1_df = df.query("Type == 'Type 1'")
    type2_df = df.query("Type == 'Type 2'")

    T1 = type1_df[['x', 'y']].to_numpy()
    T2 = type2_df[['x', 'y']].to_numpy()
    return T1,T2

def generate_perlin_metadata(perlin_file_name,avg_haussdorf_distance_value,p95_haussdorf_distance_value,haussdorf_distance_value,wass_value,dataset_type):
    
    def translation_string_to_module(translation_str):
        start = translation_str.find('(')
        end = translation_str.find(')', start)
        vector_str = translation_str[start+1:end]
        x,y = vector_str.split(',')
        return math.sqrt(float(x)**2 + float(y)**2)
    
    metadata = {}


    dataset_type = DatasetType(dataset_type)
    match dataset_type:
        case DatasetType.PERTURBATION:
            if(perlin_file_name[-1] == '_'):
                typename,_,_,_ = perlin_file_name.split('_')
                main_seed,epsilon=None,0
            else:
                print(perlin_file_name)
                typename,_,_,main_seed,_,epsilon = perlin_file_name.split('_')
            metadata['seed'] = typename
            metadata['perturbation_seed'] = main_seed
            metadata['epsilon'] = epsilon
            metadata['avg_haussdorf_distance_value'] = avg_haussdorf_distance_value
            metadata['p95_haussdorf_distance_value'] = p95_haussdorf_distance_value
            metadata['haussdorf_distance_value'] = haussdorf_distance_value
            metadata['wasserstein'] = wass_value
        case DatasetType.RIGID_TRANSFORMATION:
            if(perlin_file_name[-1] == '_'):
                #typename,id_,tr,rot,_ = perlin_file_name.split('_')
                typename,tr,rot,_ = perlin_file_name.split('_')
            else:
                typename,tr,rot = perlin_file_name.split('_')
            metadata['seed'] = typename
            metadata['translation'] = tr
            metadata['rotation'] = rot+'_center'
            metadata['avg_haussdorf_distance_value'] = avg_haussdorf_distance_value
            metadata['p95_haussdorf_distance_value'] = p95_haussdorf_distance_value
            metadata['haussdorf_distance_value'] = haussdorf_distance_value
            metadata['wasserstein'] = wass_value
        case DatasetType.BOTH:
            if(perlin_file_name[-1] == '_'):
                typename,id_,_,_,main_seed,_,epsilon,tr,rot,_ = perlin_file_name.split('_')
            else:
                typename,id_,_,_,main_seed,_,epsilon,tr,rot = perlin_file_name.split('_')
            metadata['seed'] = typename+'_'+id_
            metadata['translation'] = tr
            metadata['rotation'] = rot+'_center'
            metadata['perturbation_seed'] = main_seed
            metadata['epsilon'] = epsilon
            metadata['avg_haussdorf_distance_value'] = avg_haussdorf_distance_value
            metadata['p95_haussdorf_distance_value'] = p95_haussdorf_distance_value
            metadata['haussdorf_distance_value'] = haussdorf_distance_value
            metadata['wasserstein'] = wass_value
        case DatasetType.CROSS_SET:
            if 'x' in perlin_file_name:
                id_,tr,rot,_ = perlin_file_name.split('_')
                metadata['seed'] = id_
            else:
                typename,id_,tr,rot,_ = perlin_file_name.split('_')
                metadata['seed'] = typename+'_'+id_

            metadata['translation'] = tr
            metadata['rotation'] = rot+'_center'
            metadata['avg_haussdorf_distance_value'] = avg_haussdorf_distance_value
            metadata['p95_haussdorf_distance_value'] = p95_haussdorf_distance_value
            metadata['haussdorf_distance_value'] = haussdorf_distance_value
            metadata['wasserstein'] = wass_value
        case DatasetType.IMPULSIVE_NOISE:
            #<cloud>_n<count>s<offset>: number of noise points and offset of the seed of the noise
            typename,noise = perlin_file_name.split('_')
            noise_points,seed_offset = noise[1:].split('s')
            metadata['seed'] = typename
            metadata['noise_points'] = int(noise_points)
            metadata['noise_seed_offset'] = int(seed_offset)
            metadata['avg_haussdorf_distance_value'] = avg_haussdorf_distance_value
            metadata['p95_haussdorf_distance_value'] = p95_haussdorf_distance_value
            metadata['haussdorf_distance_value'] = haussdorf_distance_value
            metadata['wasserstein'] = wass_value
    return metadata





def generate_mcitests_perlin(perlin_folder,begin,end,radius_list,dataset_type):
    list_perlin = list_csv_files(perlin_folder)[begin:end]

    print(f"List that will be processed: {list_perlin}")
    mci_tests = []


    for file in list_perlin:
        T1,T2 = read_points_perlin_file(file)
        csv_name = file.stem
        average_haussdorf_dist, p95_haussdorf_distance, haussdorf_distance = calculate_haussdorf_distances(file)
        sliced_wasserstein_dist = calculate_wasserstein(file)[2]
        perlin_metadata = generate_perlin_metadata(csv_name,average_haussdorf_dist,p95_haussdorf_distance,haussdorf_distance,sliced_wasserstein_dist,dataset_type)

        mci_test = MCITestFamily(A_points=T1,
                          B_points=T2,
                          scale_factor=1,
                          are_randomly_generated=False,
                          radius_list= radius_list,
                          test_name=csv_name,
                          rigid_transforms=None,
                          metadata_override=perlin_metadata,
                          folder_name_override=csv_name)
        mci_tests.append(mci_test)
    print(mci_tests)
    return mci_tests




def mci_process(perlin_folder: str, n_batches: int, batch_index: int, min_radius: int, max_radius: int, radius_step: int ,dataset_type: DatasetType, output_folder_name: str):


    ok, failed = 0, []


    try:
        
        radius_list = list(range(min_radius, max_radius + radius_step, radius_step))

        perlin_folder = Path(perlin_folder)
        files = sorted(perlin_folder.glob("*.csv"))  
        
        size_batch, remainder_batch = divmod(len(files), n_batches)         
        first_file_index = batch_index * size_batch + min(batch_index, remainder_batch)

        extra_file = 1 if batch_index < remainder_batch else 0

        second_file_index = first_file_index + size_batch + extra_file

        chunk = files[first_file_index:second_file_index]
        if not chunk:
            print(f"Batch {batch_index} is empty")
        else:
            print(f"[Batch {batch_index}]: files {first_file_index}..{second_file_index} of {len(files)}. This process will process a total of {second_file_index-first_file_index} files")
            print(f"[Batch {batch_index}]: The first file will be: {chunk[0].name}, while the final file will be: {chunk[-1].name} btw")

        start_time = time.time()


        mci_tests = generate_mcitests_perlin(perlin_folder,first_file_index,second_file_index,radius_list,dataset_type)
        print(mci_tests)
        bmt = BatchMCITester(mci_tests,csv_filename='measurements').run_batch(show_output=False,output_folder_name=output_folder_name)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")
        ok+=1
    except Exception as e:
        failed.append((str(e)))
        failed.append(traceback.print_exc())
    

    return {"batch": batch_index, "range": (first_file_index, second_file_index), "ok": ok, "failed": failed} 


if __name__ == "__main__":
    perlin_folder = (Path(sys.argv[1]))
    n_batches, batch_index, min_radius, max_radius, radius_step = [int(sys.argv[i]) for i in range(2,7)]
    #Options for the type of dataset: if it's perturbation, rigid, or both.
    dataset_type = str(sys.argv[7])
    output_folder_name = str(sys.argv[8])
    mci_process(perlin_folder, n_batches, batch_index, min_radius, max_radius, radius_step, dataset_type,output_folder_name)