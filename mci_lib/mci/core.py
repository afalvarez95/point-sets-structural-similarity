from pathlib import Path
import datetime
import random

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import rc
rc('animation', html='html5')



from shapely.geometry import MultiPoint
from shapely.plotting import plot_polygon
from shapely import intersection,union

import numpy as np
import pandas as pd

from IPython.display import Video,display
from typing import List

def perform_closing(multipoint_obj: MultiPoint,radius:float):
    '''
    Performs a closing with a given radius.
    :param: multipoint_obj which is the point cloud.
    :param: radius of the closing disc.
    :returns: Polygon.
    '''
    dilation = multipoint_obj.buffer(radius,cap_style="round",join_style="round")
    closing = dilation.buffer(-radius,cap_style="round",join_style="round")
    return closing

def perform_closings(multipoint_obj,radius_list: List[float]):
    '''
    Performs a series of closings given a radius list.
    :param: multipoint_obj which is the point cloud.
    :param: which are the list of radii used to perform the closings.
    :returns: Polygon.
    '''
    result_closings = []
    for r in radius_list:
        result_closings.append(perform_closing(multipoint_obj,r))
    return result_closings


class RigidTransform:
    def __init__(self,tx: float,ty: float,angle: float,rot_over_center=True):
        '''
        Initializes a Rigid Transformation.

        :param tx: x coordinate of translation vector.
        :param ty: y coordinate of translation vector.
        :param angle: angle (in radians) of the rotation.
        :param rot_over_center: If true, rotates on the center of the point cloud, else does it on the upper left corner
        '''
        self.tx: float = tx
        self.ty: float = ty
        self.angle: float = angle
        self.rot_over_center: bool = rot_over_center
    def get_xyangle(self):
        '''
        :returns: (tX,tY,angle of rotation,type of rotation), a tuple with all the parameters of a RigidTransform.
        '''
        return self.tx,self.ty,self.angle,self.rot_over_center
    
    def __str__(self) -> str:
        '''
        :returns: A string that models a rigid transformation with the following syntax:
        r"T{x,y}_R{a}_(non)center"

        - T{x,y} -> The 2D vector used for translation.
        - R{a} -> The angle of rotation
        - (non)center -> If center, rotates on the center of the point cloud, else, noncenter, which does it on the upper left corner.
        '''
        roc: str = 'center' if self.rot_over_center else 'noncenter'
        if(self.rot_over_center):
            roc: str = ''
        return 'T{'+f'{self.tx:.4f}'+'#'+f'{self.ty:.4f}'+'}_'+'R'+f'{self.angle:.4f}'+roc
    

class PerturbationTransform:
    def __init__(self, epsilon: float, main_seed: int):
        '''
        Initializes a Perturbation Transformation.
        :param epsilon: weight of unitary vector of the perturbation.
        :param : 
        '''
        self.epsilon: float = epsilon
        self.main_seed: int = main_seed
    def get_params(self):
        '''
        :returns: (tX,tY,angle of rotation,type of rotation), a tuple with all the parameters of a RigidTransform.
        '''
        return self.epsilon,self.main_seed
    def __str__(self) -> str:
        '''
        :returns: A string that models a rigid transformation with the following syntax:
        r"S_seed_E_epsilon"
        '''
        return 'S_'+f'{self.main_seed}'+'E_{self.ty:.4f}'

class PointSets:
    def __init__(self,
                 radius_list:List[float],
                 scale_factor:float=20,
                 B_as_A:bool=False,
                 rigid_transform:RigidTransform=None,
                 are_randomly_generated:bool=False,
                 n:int=300,
                 B_prop:float=None,
                 seed: int = None,
                 A_points=None,
                 B_points=None,
                 test_name=None,
                 metadata_override=None,
                 folder_name_override=None
                 ):
        '''
        Initializes an object with two point sets that will be used to perform incremental closings.
        There are two main ways of using this class: either the points are randomly chosen, or set by the user.
        The only parameters that those two options share are:

        :radius_list: List of floats used to generate the incremental closings.
        :scale_factor: If you want to apply a scale factor to the points you have chosen. Defaults as 20.
        :B_as_A: If you want to clone the first point set so it is the same as second point set. Defaults as False.
        :rigid_transform: The rigid transformation performed on point set 2, defaults to None (so no transformation is done)
        :B_prop: The proportion of points that will be deleted on point set 2. Defaults to None (so no elimination).
        :test_name: Custom name of test, in case the points are loaded and there is no seed.
        :metadata_override: In case of adding custom metadata. Iou_r and mci will be appended on the end.

        ## Random point sets options
        In case of using random points, you have to select **are_randomly_generated** to True.
        Additionally, **seed** allows to select the seed used to select those random points.

        ## Point sets selected by users
        **A_points** and **B_points** allows users to manually input the first and the second point set.

    
        

        '''
        self.test_name = test_name
        self.metadata_override = metadata_override
        self.folder_name_override = folder_name_override
        self.radius_list = radius_list
        def RT(points,rigid_transform):
            '''
            Function that does the Rigid Transformation to the second point set.
            '''
            tx,ty,angle,over_center = rigid_transform.get_xyangle()
            R = np.array([[np.cos(angle), -np.sin(angle)],
                          [np.sin(angle),  np.cos(angle)]])
            if(over_center):
                center = points.mean(axis=0)
                points = points - center
                points_r = points @ R.T
                points_rt = points_r + np.array([tx, ty]) +center
                return points_rt
            else:
                points_r = points @ R.T
                points_rt = points_r + np.array([tx, ty]) 
                return points_rt
                
        self.seed = None
        if(are_randomly_generated):
            if(seed is not None):
                self.seed = seed
                np.random.seed(seed)
            A=np.random.rand(n,2)*scale_factor
            B=np.random.rand(n,2)*scale_factor
            self.n=n
        else:
            A=A_points*scale_factor
            self.n = len(A_points)
            if(B_points is not None):  
                B=B_points*scale_factor
        self.A = A
        
        if(B_as_A):
            self.B = A
        else:
            self.B = B

        if(B_prop is not None):
            if(B_prop <= 1 and B_prop>=0):
                k= max(1, int(self.n * B_prop))
                chosen_idx = np.random.permutation(self.n)[:k]
                self.B = self.B[chosen_idx]
                
        if(rigid_transform is not None):
            self.rt = rigid_transform
            self.B = RT(self.B,rigid_transform)
        if(type(A) == list):
            self.ob_A = MultiPoint(self.A)
        else:
            self.ob_A = MultiPoint(self.A.tolist())
        if(type(B) == list):
            self.ob_B = MultiPoint(self.B)
        else:
            self.ob_B = MultiPoint(self.B.tolist())


    def __str__(self):
        '''
        :returns: A string in the format: seed_rigidtransformation_timestamp
        In case of no seed, just the rigid transform and timestamp.
        '''
        ts = datetime.datetime.now()
        str_timestamp = ts.strftime("%Y%m%d%H%M%S")
        if(self.seed == None):
            if(self.test_name is not None):
                    return self.test_name+'_'+'TMST'+str_timestamp
            else:
                return 'SNull_'+str(self.rt)+'_'+'TMST'+str_timestamp
        return 'S'+str(self.seed)+'_'+str(self.rt)+'_'+'TMST'+str_timestamp

    def generate_path(self) -> Path:
        '''
        :returns: A path to store all the data for each point set pair processing.
        '''
        ts: datetime = datetime.datetime.now()
        str_timestamp: str = ts.strftime("%Y%m%d%H%M%S")
        if(self.test_name == None):
            main_folder_name = Path('test_'+str_timestamp)
            subfolder_name = Path('S'+str(self.seed)+'_'+str(self.rt))
        else:
            main_folder_name = Path(self.test_name)
            subfolder_name = Path('S'+str(self.seed)+'_'+str(self.rt))
        if(self.folder_name_override is not None):
            subfolder_name = self.folder_name_override
        return main_folder_name / subfolder_name

    def plot_sets(self):
        '''
        Plots each point set: the first in red, and the second in cyan.
        '''
        plt.plot(self.A[:,0],self.A[:,1],'.r')
        plt.plot(self.B[:,0],self.B[:,1],'.c')
        plt.show()
        
    def calculate_closings(self):
        '''
        Calculates the incremental closings for each point set and stores it in the object.
        '''
        self.res_closings_A = perform_closings(self.ob_A,self.radius_list)
        self.res_closings_B = perform_closings(self.ob_B,self.radius_list)
        
    def get_radii(self):
        '''
        Outputs the radius list.
        '''
        return self.radius_list
        
    def calculate_iou_per_radius(self):
        '''
        Calculates an IoU per radius.
        '''
        def iou_A_B(A,B) -> float:
            int_A_B: float = intersection(A,B).area
            union_A_B: float  = union(A,B).area
            if(union_A_B == 0):
                return 0.0
            return int_A_B / union_A_B
        A = self.res_closings_A
        B = self.res_closings_B
        self.ious = list(map(iou_A_B, A,B))

    def get_ious(self) -> List[float]:
        '''
        :returns: The list of intersections over unions per radius.
        '''
        return self.ious

    def plot_iou_per_radius(self,base_folder_name: str='example',show_plot=False):    
        plt.clf()
        X = self.get_radii()
        Y = self.get_ious()
        plt.plot(X, Y, marker='o', linestyle='-')
        plt.fill_between(X, Y, color='red', alpha=0.3)
        plt.xlabel('Radius')
        plt.ylabel('IoU')
        plt.title(self.test_name+'\nIoU per radius (AUC in red)')
        plt.savefig(Path(base_folder_name) / (self.test_name+'_iou_per_r_plot.png'),dpi=300)
        if(show_plot):
            plt.show()

        plt.close()

    def calculate_auc(self) -> float:
        '''
        Calculates and stores in the object the area under the curve.
        '''
        self.auc = np.trapz(self.get_ious(), self.get_radii())

    def calculate_mci(self) -> float:
        '''
        :returns: The MCI of the point sets.
        '''
        self.mci = self.auc / (max(self.get_radii()) - min(self.get_radii()))
        return self.mci

    def plot_closing_animations(self,base_folder:str='example', output_file_name:str='animation.mp4',display_vid=True):
        '''
        Saves the incremental closings as an animation.
        '''
        fig, ax = plt.subplots()
        def update(closing_idx):
            ax.clear()
            ax.plot(self.A[:, 0], self.A[:, 1], '.r',markersize=3, label='Point set 1')
            ax.plot(self.B[:, 0], self.B[:, 1], '.c',markersize=3, label='Point set 2')
            plot_polygon(self.res_closings_A[closing_idx], ax=ax, color='r', add_points=False, alpha=0.5,linewidth=0)
            plot_polygon(self.res_closings_B[closing_idx], ax=ax, color='c', add_points=False, alpha=0.5,linewidth=0)
            ax.set_aspect('equal')
            ax.legend(loc='lower left',bbox_to_anchor=(0.94,1))
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            title = self.test_name+'\nClosing with a ball of radius '+f'{self.get_radii()[closing_idx]:.4f}'
            ax.set_title(title)
            frame_path = Path(base_folder) / "frames" / f"frame_{closing_idx}.png"
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(frame_path, dpi=200)
            return []
        plt.close()
        video_path = Path(base_folder) / output_file_name
        video_path.parent.mkdir(parents=True, exist_ok=True)
        anim = FuncAnimation(fig, update, frames=len(self.get_radii()), interval=1000, repeat=False)
        anim.save(video_path, dpi=200)
        if(display_vid): 
            display(Video(video_path, width=1200))
            return ax

    def generate_files(self,base_folder_name:str, video_file_name: str, csv_file_path :Path,
                        show_files: bool):
        '''
        Generates all the files for that point set incremental closing and stores all the measurements in a given csv file.
        '''
        self.calculate_closings()
        self.plot_closing_animations(base_folder = base_folder_name,output_file_name=video_file_name,display_vid=show_files)
        self.calculate_iou_per_radius()
        self.plot_iou_per_radius(base_folder_name,show_files)
        self.calculate_auc()
        self.calculate_mci()
        iou_r_str =  ';'.join(f'({r},{iou})' for r, iou in zip(self.radius_list,self.ious))
        print(self.__str__().split("_"))
        
        if(self.metadata_override is not None):
                data = self.metadata_override
                data['mci'] = self.mci
                data['iou_r'] = iou_r_str
        else:
            seed,t,r,timestamp = self.__str__().split("_")
            data = {'seed': seed[1:], 'translation':t[1:],'rotation':r[1:],'timestamp':timestamp[4:],'mci': self.mci, 'iou_r': iou_r_str}
        with open(csv_file_path, 'a') as f:

            df = pd.DataFrame([data])
            df.to_csv(f, header=f.tell()==0,index=False)

class MCITestFamily:
    def __init__(self,
                 radius_list,
                 n:int=300,
                 scale_factor:float=20,
                 B_as_A:bool=False,
                 rigid_transforms:list[RigidTransform]=None,
                 B_prop:float=None,
                 A_points=None,
                 B_points=None,
                 seeds=None,
                 are_randomly_generated=False,
                 test_name=None,
                 metadata_override=None,
                 folder_name_override=None
                 ):
        '''
        Initializes options for a MCITestFamily given a list of RigidTransforms and PointSet parameters.
        For more information on the parameters, see PointSet initialization function.
        '''
        if(rigid_transforms is None):
            self.rts = [RigidTransform(0,0,0,False)]
        else:
            self.rts = rigid_transforms

        if(not are_randomly_generated):
            ps_init = np.vectorize(lambda rt: PointSets(A_points = A_points,
                                                             B_points= B_points,
                                                             scale_factor = scale_factor,
                                                             B_as_A = B_as_A,
                                                             B_prop=B_prop,
                                                             rigid_transform = rt,
                                                             radius_list=radius_list,
                                                             test_name=test_name,
                                                             metadata_override=metadata_override,
                                                             folder_name_override=folder_name_override))
            
            ps = ps_init(self.rts)
            print(ps[0])
        else:
            if(seeds is not None):
                ps_init = np.vectorize(lambda rt,seed: PointSets(n = n,
                                                                 seed = seed,
                                                                 scale_factor = scale_factor,
                                                                 B_as_A = B_as_A,
                                                                 B_prop=B_prop,
                                                                 rigid_transform = rt,
                                                                 radius_list=radius_list,
                                                                 are_randomly_generated=True,
                                                                 test_name=test_name,
                                                                 metadata_override=metadata_override,
                                                                 folder_name_override=folder_name_override))
            else:
                seeds = [random.randint(1, int(10e6))]
                ps_init = np.vectorize(lambda rt,seed: PointSets(n = n,
                                                            scale_factor = scale_factor,
                                                            B_as_A = B_as_A,
                                                            B_prop=B_prop,
                                                            rigid_transform = rt,
                                                            seed =seed,
                                                            radius_list=radius_list,
                                                            are_randomly_generated=True,
                                                            test_name=test_name,
                                                            metadata_override=metadata_override,
                                                            folder_name_override=folder_name_override))
            ps = ps_init(self.rts,seeds)
        
        self.pss: List[PointSets] = ps
        print('Created',len(self.pss),'point set pairs.')
    def generate_mci_files(self,csv_filename:str,output_folder_name:str=None,show_output=False):
        '''
        Generates the files for that MCITestFamily.
        '''   
        paths = [ps.generate_path() for ps in self.pss]
        if output_folder_name is None:
            csv_file_path : Path = Path.cwd() / 'tests' / paths[0].parent / Path(csv_filename+'.csv')
        else:
            csv_file_path : Path = Path.cwd() / output_folder_name / paths[0].parent / Path(csv_filename+'.csv')
        

        names = [str(ps) for ps in self.pss]
        for ps, path, name in zip(self.pss, paths, names): 
            if output_folder_name is None:
                ps.generate_files(Path.cwd() / 'tests' / path, name + '.mp4',csv_file_path,show_output)
            else:
                ps.generate_files(Path.cwd() / output_folder_name / path, name + '.mp4',csv_file_path,show_output)

        print('Generated files for',len(self.pss),'point set pairs.')

class BatchMCITester:
    def __init__(self,mci_tests: list[MCITestFamily], csv_filename:str):
        '''
        Creates a batch class that runs a list of MCITestFamily, and stores all the calculations in a csv file.
        :param mci_test: A list of MCITestFamily objects.
        :param csv_filename: A string with the name of the csv file that will store all the calculations for the test. No file format needed.
        '''
        self.mci_tests = np.array(mci_tests)
        self.csv_filename = csv_filename
    
    def get_csv_filename(self) -> str:
        '''
        :returns: The string with the name of the csv file that will store all the calculations.
        '''
        return self.csv_filename
        
    def get_mci_tests(self):
        '''
        :returns: The list of MCITestFamily objects used.
        '''
        return self.mci_tests
        
    def run_batch(self,show_output:bool=False,output_folder_name=None):
        '''
        Runs each MCITestFamily object and generates their files.
        :params: Shows output below the cell.
        '''
        print(self.get_mci_tests())
        for mci_test in self.get_mci_tests():
            mci_test.generate_mci_files(self.csv_filename,show_output=show_output,output_folder_name=output_folder_name)
        
