'''
Code with the perlin noise generator functions.
'''


from enum import Enum
from typing import List
from perlin_noise import PerlinNoise
import random
import math
import numpy as np
import csv
import matplotlib.pyplot as plt
import cv2
import pandas as pd
from pathlib import Path
from abc import ABC, abstractmethod

np.random.seed(30)



class PerlinType(Enum):
    '''
    Enum that models the types of Perlin Noise that can be generated.
    Single: Using a single seed and a octave value.
    Multiweight Balanced: Using N seeds and octaves, and each contribution is equally balanced in the final Perlin Noise.
    Multiweight Custom: Using N seeds and octaves, and each contribution is variably balanced in the final Perlin Noise.
    '''
    SINGLE = 1,
    MULTI_WEIGHT_BALANCED = 2,
    MULTI_WEIGHT_CUSTOM = 3


class AngleMetric(Enum):
    '''
    Enum that models Angles units: Degrees or Radians.
    '''
    DEGREE = 1,
    RADIAN = 2


class PerlinPostEliminationType(Enum):
    '''
    Enum that models the elimination policy of points, in this case, just removing points randomly.
    '''
    POINT = 1



class Transformation():
    '''
    Class that models a generic transformation of point.
    '''
    @abstractmethod
    def __init__(self,seed):
        self.numpy_rng = np.random.default_rng(seed=seed)
        pass
    @abstractmethod
    def __call__(self):
        pass

class RigidTransformation(Transformation):
    '''
    Class that models a rigid transformation.
    '''
    def __init__(self,translation_vector,rotation_angle,angle_metric=AngleMetric.DEGREE,rotation_pivot=(-500,-500),seed=30):
        super().__init__(seed)
        self.translation_vector = translation_vector
        self.angle_metric = angle_metric

        match self.angle_metric:
            case AngleMetric.DEGREE:
                self.rotation_angle = math.radians(rotation_angle)
            case AngleMetric.RADIAN:
                self.rotation_angle = rotation_angle

        self.rotation_matrix = np.array([[math.cos(self.rotation_angle), math.sin(self.rotation_angle)],
                             [-math.sin(self.rotation_angle),  math.cos(self.rotation_angle)]])
        self.rotation_pivot = rotation_pivot

    def __call__(self, points: np.ndarray, rigid_point_elimination_percentage: float):
        translated_points = points + self.translation_vector + self.rotation_pivot
        rotated_points = np.round(translated_points @ self.rotation_matrix.T,decimals=2).astype(float)
        rotated_points = rotated_points - self.rotation_pivot
        num_to_eliminate = int(len(rotated_points) * rigid_point_elimination_percentage)

        if num_to_eliminate > 0:
            elimination_indices = self.numpy_rng.choice(len(rotated_points), num_to_eliminate, replace=False)
            rotated_points = np.delete(rotated_points, elimination_indices, axis=0)

        return rotated_points
    

class PerturbationTransformation(Transformation):
    '''
    Class that models a perturbation transformation.
    '''
    def __init__(self,main_seed,epsilon):
        self.main_seed = int(main_seed)
        self.epsilon = float(epsilon)
        

    def __call__(self, points: np.ndarray, elimination_percentage: float=0,seed=30):
        super().__init__(seed)
        num_points = len(points)
        random_number_generator = np.random.default_rng(seed=self.main_seed)
        angles = random_number_generator.uniform(0, 2*np.pi, size=num_points)
        uniform_vectors = np.column_stack((np.cos(angles), np.sin(angles)))

        moved_points = points + self.epsilon*uniform_vectors

        num_to_eliminate = int(len(moved_points) * elimination_percentage)

        if num_to_eliminate > 0:
            elimination_indices = self.numpy_rng.choice(len(moved_points), num_to_eliminate, replace=False)
            moved_points = np.delete(moved_points, elimination_indices, axis=0)
        
        return moved_points


class RigidAndPerturbationTransformation(Transformation):
    '''
    Class that models both a perturbation transformation followed by a rigid transformation.
    '''
    def __init__(self,main_seed,epsilon,translation_vector,rotation_angle,angle_metric=AngleMetric.DEGREE,rotation_pivot=(-500,-500)):
        self.perturbation_transformation = PerturbationTransformation(main_seed,epsilon)
        self.rigid_transformation = RigidTransformation(translation_vector,rotation_angle,angle_metric,rotation_pivot)

    def __call__(self,points: np.ndarray, elimination_percentage: float=0):
        perturbed_points= self.perturbation_transformation(points, 0)
        rigid_transformed_and_perturbed_points = self.perturbation_transformation(perturbed_points,elimination_percentage)
        return rigid_transformed_and_perturbed_points

class PointData:
    '''
    Class that models Data Points.
    '''
    def __init__(self,name_f1,name_f2):
        self.points_f1 = None
        self.name_f1 = name_f1
        self.points_f2 = None
        self.name_f2 = name_f2
    
    def set_original_points(self,points_f1):
        self.points_f1 = points_f1.astype(float)
    def set_transformed_points(self,points_f2):
        self.points_f2 = points_f2.astype(float)
    def get_original_points(self):
        return self.points_f1
    def get_transformed_points(self):
        return self.points_f2
    def get_labels(self):
        return self.name_f1,self.name_f2

class PerlinFunc:
    '''
    Class that generates Perlin Noise depending of the Perlin Noise type that is requested.
    '''
    def __init__(self,perlin_type: PerlinType, seed_array: List[int], octave_array: List[int],custom_weights: List[int]=None):
        if(len(seed_array) != len(octave_array)):
            raise Exception("Seed array and octave array must be same length.")
        if(not(custom_weights) and perlin_type == PerlinType.MULTI_WEIGHT_CUSTOM):
            raise Exception("Must provide custom weights if custom weights are selected.")
        if(custom_weights and len(custom_weights) != len(seed_array)):
            raise Exception("Length of custom weights must match seeds and octaves")
        if(custom_weights and sum(custom_weights) != 1):
            raise Exception("Custom weights, if selected, must sum 1")
        self.perlin_type = perlin_type
        self.seed_array = seed_array
        self.octave_array = octave_array
        self.custom_weights = custom_weights
        self.num_seeds = len(self.seed_array)
    
    def __call__(self, flat_coords, **kwds):
        match self.perlin_type:
            case PerlinType.SINGLE:
                result = 0
                noise_values = np.array([PerlinNoise(seed=self.seed_array[0],octaves=self.octave_array[0]).__call__(tuple(coords)) for coords in flat_coords])
                result = noise_values
                return result
            case PerlinType.MULTI_WEIGHT_BALANCED:
                result = 0
                balanced_weight = 1/(len(self.seed_array))
                noises = [PerlinNoise(seed=self.seed_array[i],octaves=self.octave_array[i]) for i in range(self.num_seeds)]
                noise_values = np.array([balanced_weight*sum(noise.__call__(tuple(coords)) for noise in noises) for coords in flat_coords])

                result = noise_values
                return result
            case PerlinType.MULTI_WEIGHT_CUSTOM:
                result = 0
                noises = [PerlinNoise(seed=self.seed_array[i],octaves=self.octave_array[i]) for i in range(self.num_seeds)]
                noise_values = np.array([sum(noise.__call__(tuple(coords))*self.custom_weights[idx] for idx,noise in enumerate(noises)) for coords in flat_coords])

                result = noise_values
                return result



class DualPerlinCloud:
    '''
    
    '''
    def __init__(self, width_im: int, height_im: int,
                 perlin_func: PerlinFunc = None,
                 point_labels: List[str] = None,
                 transformation: Transformation = None,
                 t1_point_density: float = None,
                 t2_rigid_loss: float = None,
                 csv_name: str = None):

        self.width_im = width_im
        self.height_im = height_im
        
        self.perlin_func = perlin_func

        self.transformation = transformation

        self.t1_point_density = t1_point_density
        self.t2_rigid_loss = t2_rigid_loss


        self.base_perlin = None
        self.picture = None
        if(len(point_labels) != 2):
            raise Exception("Labels name should be two names")
        self.points_data = PointData(*point_labels)

        #change to standardized name
        self.csv_name = csv_name

    def generate_perlin_base_points(self):
        x_coords = np.linspace(0, 1, self.width_im)
        y_coords = np.linspace(0, 1, self.height_im)
        x_grid, y_grid = np.meshgrid(x_coords, y_coords)

        flat_coords = np.stack([x_grid.ravel(), y_grid.ravel()], axis=-1)

        noise_values = self.perlin_func(flat_coords)

        self.picture = noise_values.reshape(self.height_im, self.width_im)

    def generate_threshold(self):
        min_val,max_val = -1, 1
        normalized_pic = (self.picture - min_val) / (max_val - min_val)

        scaled_pic = (normalized_pic * 255).astype(np.uint8)
                                                
        thresholded_pic = (scaled_pic >= 128).astype(np.uint8) * 255

        binary_image = np.array(thresholded_pic) >= 128 
        self.black_pixel_coords = np.column_stack(np.where(binary_image))


    def generate_original_perlin_points(self):
        num_black_pixels = len(self.black_pixel_coords)
        num_samples = math.floor(self.t1_point_density*num_black_pixels)
        sampled_indices = np.random.choice(num_black_pixels, num_samples, replace=False)
        original_points = self.black_pixel_coords[sampled_indices]
        self.points_data.set_original_points(original_points)


    def generate_transformed_perlin_points(self):
        transformed_points = self.transformation(self.points_data.points_f1,self.t2_rigid_loss)
        self.points_data.set_transformed_points(transformed_points)

    def view_points(self):
        colored_image = np.zeros((self.width_im,self.height_im, 3), dtype=np.uint8)
        for point in self.points_data.points_f1:
            colored_image[point[0], point[1]] = [255, 0, 0] 

        for point in self.points_data.points_f2:
            if 0 <= point[0] < colored_image.shape[0] and 0 <= point[1] < colored_image.shape[1]:
                colored_image[point[0], point[1]] = [0, 255, 255]

        plt.figure(figsize=(10, 10))
        plt.imshow(colored_image, aspect='auto')
        plt.title('Sampled Points')
        plt.axis('off')
        plt.show()


    def generate_csv(self):
        csv_data = []
        for x, y in self.points_data.points_f1:
            csv_data.append((x,y,self.points_data.name_f1))
        for x, y in self.points_data.points_f2:
            csv_data.append((x,y,self.points_data.name_f2))

        Path(self.csv_name).parent.mkdir(exist_ok=True)

        with open(self.csv_name, mode='w', newline='') as file:
            writer = csv.writer(file,delimiter=',')

            writer.writerow(['x','y','Type'])

            for row in csv_data:
                writer.writerow(row)

        print(f"CSV file '{self.csv_name}' generated.")

    def process_pipeline(self):
        self.generate_perlin_base_points()
        self.generate_threshold()
        self.generate_original_perlin_points()
        self.generate_transformed_perlin_points()
        self.generate_csv()


    def load_perlin_cloud_from_file(self,csv_file: str):
        df = pd.read_csv(csv_file)

        type_1_points = df[df['Type'] == self.points_data.get_labels()[0]]
        type_2_points = df[df['Type'] == self.points_data.get_labels()[1]]

        type_1_points_list = type_1_points[['x', 'y']].values
        type_2_points_list = type_2_points[['x', 'y']].values
        

        self.points_data.set_original_points(type_1_points_list)
        self.points_data.set_transformed_points(type_2_points_list)

    def perform_transformation_from_points(self):
        """ 
        Function that translates points from file that are without transformation so the dual point generation is quicker, as
        Perlin Noise base generation is slower
        """
        transformed_points = self.transformation(self.points_data.points_f2,0)
        self.points_data.set_transformed_points(transformed_points)