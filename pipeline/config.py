from enum import Enum, auto
from pathlib import Path

class DATASET_CONFIG_OPTIONS(Enum):
    CROSS = auto()
    PERTURBATION = auto()
    REMOVAL = auto()
    TRANSLATION = auto()
    ROTATION = auto()
    PERT_AND_REMOVAL = auto()
    IMPULSIVE_NOISE = auto()

class PIPELINE_CONFIG_OPTIONS(Enum):
    MCI_AND_HEATMAPS = auto() #Partial test: point sets are read from input_datasets/<dataset>/*.csv (in the repo), only MCI, NND and heatmaps are run.
    REBUILT_EACH_WITH_STEP = auto() #Full test: every file is regenerated from perlin_base_csv_dataset, step by step.
    USE_CUSTOM_FILENAMES = auto() #Custom test: the recommended values are loaded first, then overridden in the USE_CUSTOM_FILENAMES section below.

#GLOBAL CONFIG OPTIONS
#These are the only values that should be changed for a partial or full test.

PIPELINE_OPTIONS = PIPELINE_CONFIG_OPTIONS.MCI_AND_HEATMAPS

SELECTED_DATASET_OPTION = DATASET_CONFIG_OPTIONS.CROSS
DATEIDENTIFIER = "261021"

#NNDistance options
NND__SKIP_GENERATION = False
NND__SHOW_PLOTS = False

#MCI commands helper options (radius range can be taken from the NNDistances recommendation)
MCIHELP__N_BATCHES = 10
MCIHELP__MIN_RADIUS = 8
MCIHELP__MAX_RADIUS = 24
MCIHELP__RADIUS_STEP = 4

#Impulsive noise options (IMPULSIVE_NOISE): noise points on the white pixels (above the median) of each base cloud
NOISE__COUNTS = [25, 50, 75, 100]
#One noise variation per offset: generator seed = numpy_choice_rng_seed of the cloud (perlin_base_dataset.csv) + offset.
#The offset 0 is not used, it is the seed of the blobs. Changing the offsets gives other reproducible variations.
NOISE__SEED_OFFSETS = [1, 2, 3, 4]


#############################
# PATHS
#############################
#Every pipeline script reads and writes relative to these paths, not relative to the folder they are summoned from.

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#Small csv files used to generate the point sets (tracked in the repo).
PERLIN_BASE_CSV_DATASET_DIR = PROJECT_ROOT / "perlin_base_csv_dataset"

#Fixed point sets used by the partial tests (tracked in the repo): input_datasets/<dataset>/*.csv
INPUT_DATASETS_DIR = PROJECT_ROOT / "input_datasets"

#Working folder of the pipeline (generated files, not tracked in the repo). Each run has its own folder.
PIPELINE_TESTS_DIR = PROJECT_ROOT / "runs"
#Short names used in the run folder name, to keep the paths under the 260 characters limit of Windows.
PIPELINE_OPTIONS_SHORT_NAMES = {
    PIPELINE_CONFIG_OPTIONS.MCI_AND_HEATMAPS: "MCI_HMAPS",
    PIPELINE_CONFIG_OPTIONS.REBUILT_EACH_WITH_STEP: "REBUILT_STEPS",
    PIPELINE_CONFIG_OPTIONS.USE_CUSTOM_FILENAMES: "CUSTOM",
}
DATASET_OPTIONS_SHORT_NAMES = {
    DATASET_CONFIG_OPTIONS.CROSS: "CS",
    DATASET_CONFIG_OPTIONS.PERTURBATION: "PER",
    DATASET_CONFIG_OPTIONS.REMOVAL: "REM",
    DATASET_CONFIG_OPTIONS.TRANSLATION: "TRA",
    DATASET_CONFIG_OPTIONS.ROTATION: "ROT",
    DATASET_CONFIG_OPTIONS.PERT_AND_REMOVAL: "PER_REM",
    DATASET_CONFIG_OPTIONS.IMPULSIVE_NOISE: "IN",
}
RUN_NAME = f"{DATEIDENTIFIER}_{PIPELINE_OPTIONS_SHORT_NAMES[PIPELINE_OPTIONS]}_{DATASET_OPTIONS_SHORT_NAMES[SELECTED_DATASET_OPTION]}"
WORK_DIR = PIPELINE_TESTS_DIR / RUN_NAME

#Folder name inside input_datasets for each dataset option (partial tests only).
INPUT_DATASET_FOLDER_NAMES = {
    DATASET_CONFIG_OPTIONS.CROSS: "cross",
    DATASET_CONFIG_OPTIONS.PERTURBATION: "perturbation",
    DATASET_CONFIG_OPTIONS.REMOVAL: "removal",
    DATASET_CONFIG_OPTIONS.TRANSLATION: "rigid",
    DATASET_CONFIG_OPTIONS.ROTATION: "rigid",
    DATASET_CONFIG_OPTIONS.PERT_AND_REMOVAL: "pert_and_removal",
    DATASET_CONFIG_OPTIONS.IMPULSIVE_NOISE: "impulsive_noise",
}

#Point cloud folders generated inside WORK_DIR by steps 1 and 2.
BASE_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_base_point_clouds"
BASE_REM_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_base_point_clouds_rem"
CROSS_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_base_point_clouds_crossproduct"
PERTURBED_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_point_clouds_perturbed"
PER_REM_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_point_clouds_per_rem"
#Rotation and translation are applied in the same step (rigid_transforms.csv), the heatmaps split them afterwards.
RIGID_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_point_clouds_rigid"
#Clean vs noisy dual clouds of the impulsive noise: <cloud>_n<count>s<offset>.csv
NOISE_POINT_CLOUD_FOLDER = WORK_DIR / "perlin_point_clouds_noise"


#############################
# RECOMMENDED OPTIONS PER DATASET
#############################

match SELECTED_DATASET_OPTION:
    case DATASET_CONFIG_OPTIONS.CROSS:

        #STEP 1 GENERATION
        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset.csv"
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = BASE_POINT_CLOUD_FOLDER

        #STEP 2 TRANSFORMATION/CROSS (in this case: CROSS)
        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER
        GCPF__OUTPUT_FOLDER = CROSS_POINT_CLOUD_FOLDER
        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = None
        GTPF__OPTION = None

        #Point sets used by the steps 3 to 6
        POINT_CLOUD_FOLDER = GCPF__OUTPUT_FOLDER

        #STEP 4 NNDistances Plots
        NND__CURRENT_CASE_IDX = 0

        #STEP 5 MCI COMMANDS HELPER
        MCIHELP__SET_TYPE = "Cross_Set"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"

        #STEP 6 HEATMAP RUNNER
        HR__HEATMAP_CASES = ["cross"]

    case DATASET_CONFIG_OPTIONS.PERTURBATION:

        #STEP 1 GENERATION
        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset.csv"
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = BASE_POINT_CLOUD_FOLDER

        #STEP 2 TRANSFORMATION/CROSS (in this case: Perturbation)
        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GCPF__OUTPUT_FOLDER = None
        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = PERTURBED_POINT_CLOUD_FOLDER
        GTPF__OPTION = "Perturbation"

        #Point sets used by the steps 3 to 6
        POINT_CLOUD_FOLDER = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER

        #STEP 4 NNDistances Plots
        NND__CURRENT_CASE_IDX = 2

        #STEP 5 MCI COMMANDS HELPER
        MCIHELP__SET_TYPE = "Perturbation"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"

        #STEP 6 HEATMAP RUNNER
        HR__HEATMAP_CASES = ["perturbations"]

    case DATASET_CONFIG_OPTIONS.REMOVAL:

        #STEP 1 GENERATION
        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset_with_removal.csv"
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = BASE_REM_POINT_CLOUD_FOLDER

        #STEP 2 TRANSFORMATION/CROSS (in this case: NOT APPLICABLE, as generation deals with removal)
        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GCPF__OUTPUT_FOLDER = None
        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = None
        GTPF__OPTION = None

        #Point sets used by the steps 3 to 6
        POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER

        #STEP 4 NNDistances Plots
        NND__CURRENT_CASE_IDX = 1

        #STEP 5 MCI COMMANDS HELPER
        MCIHELP__SET_TYPE = "Rigid_Transformation"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"

        #STEP 6 HEATMAP RUNNER
        HR__HEATMAP_CASES = ["removals"]

    case DATASET_CONFIG_OPTIONS.TRANSLATION | DATASET_CONFIG_OPTIONS.ROTATION:

        #STEP 1 GENERATION
        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset.csv"
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = BASE_POINT_CLOUD_FOLDER

        #STEP 2 TRANSFORMATION/CROSS (in this case: rotation and translation are applied within the same file)
        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GCPF__OUTPUT_FOLDER = None
        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = RIGID_POINT_CLOUD_FOLDER
        GTPF__OPTION = "Translation_Rotation"

        #Point sets used by the steps 3 to 6
        POINT_CLOUD_FOLDER = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER

        #STEP 4 NNDistances Plots
        NND__CURRENT_CASE_IDX = 5 if SELECTED_DATASET_OPTION == DATASET_CONFIG_OPTIONS.TRANSLATION else 4

        #STEP 5 MCI COMMANDS HELPER
        MCIHELP__SET_TYPE = "Rigid_Transformation"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"

        #STEP 6 HEATMAP RUNNER
        HR__HEATMAP_CASES = ["rigid"]

    case DATASET_CONFIG_OPTIONS.PERT_AND_REMOVAL:

        #STEP 1 GENERATION
        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset_with_removal.csv"
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = BASE_REM_POINT_CLOUD_FOLDER

        #STEP 2 TRANSFORMATION/CROSS (in this case: Perturbation)
        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GCPF__OUTPUT_FOLDER = None
        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = PER_REM_POINT_CLOUD_FOLDER
        GTPF__OPTION = "Perturbation"

        #Point sets used by the steps 3 to 6
        POINT_CLOUD_FOLDER = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER

        #STEP 4 NNDistances Plots
        NND__CURRENT_CASE_IDX = 3

        #STEP 5 MCI COMMANDS HELPER
        MCIHELP__SET_TYPE = "Perturbation"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"

        #STEP 6 HEATMAP RUNNER
        HR__HEATMAP_CASES = ["per+rem"]

    case DATASET_CONFIG_OPTIONS.IMPULSIVE_NOISE:

        #STEP 1 GENERATION (not needed: step 2 builds the clean and the noisy cloud from the Perlin field)
        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset.csv"
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = BASE_POINT_CLOUD_FOLDER

        #STEP 2 TRANSFORMATION/CROSS (in this case: impulsive noise, generate_noise_perlin_files.py)
        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GCPF__OUTPUT_FOLDER = None
        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = None
        GTPF__OPTION = None

        #Point sets used by the steps 3 to 6
        POINT_CLOUD_FOLDER = NOISE_POINT_CLOUD_FOLDER

        #STEP 4 NNDistances Plots
        NND__CURRENT_CASE_IDX = 6

        #STEP 5 MCI COMMANDS HELPER
        MCIHELP__SET_TYPE = "Impulsive_Noise"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"

        #STEP 6 HEATMAP RUNNER (bars per cloud, mean of the noise variations)
        HR__HEATMAP_CASES = ["noise"]

#STEP 2 IMPULSIVE NOISE (generate_noise_perlin_files.py)
GNPF__DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / "perlin_base_dataset.csv"
GNPF__OUTPUT_FOLDER = NOISE_POINT_CLOUD_FOLDER


#STEP 3 PREVIEWS
GP__PREVIEW_INPUT = POINT_CLOUD_FOLDER
GP__PREVIEW_OUTPUT = WORK_DIR / f"{POINT_CLOUD_FOLDER.name}_previews"

#STEP 4 NNDistances (NND)
NND__ANALYSIS_DATE = DATEIDENTIFIER

#generate_nearest_neighbour_distances_files.py handles rotation and translation cases plot cases in isolation, so
#the same folder where transformations can be used.
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__BASE = BASE_POINT_CLOUD_FOLDER
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__REMOVAL = BASE_REM_POINT_CLOUD_FOLDER
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PERTURBED = PERTURBED_POINT_CLOUD_FOLDER
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PER_REM = PER_REM_POINT_CLOUD_FOLDER
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__ROTATION = RIGID_POINT_CLOUD_FOLDER
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__TRANSLATION = RIGID_POINT_CLOUD_FOLDER
NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__NOISE = NOISE_POINT_CLOUD_FOLDER

#STEP 5 MCI COMMANDS HELPER
#Arguments for mci_lib/processes/mci_process.py: the point sets folder and the folder where the MCI files are written.
MCIHELP__POINT_CLOUD_FOLDER = POINT_CLOUD_FOLDER

#STEP 6 HEATMAP RUNNER
#MCI folder read by each heatmap case.
HR__MCI_FOLDERS = {case: MCIHELP__OUTPUT_FOLDER for case in HR__HEATMAP_CASES}
HR__OUTPUT_FOLDER = WORK_DIR / "heatmap"


#############################
# PIPELINE OPTIONS
#############################

match PIPELINE_OPTIONS:
    case PIPELINE_CONFIG_OPTIONS.MCI_AND_HEATMAPS:

        #The point sets are not generated (steps 1 and 2 are skipped), they are read from input_datasets.
        POINT_CLOUD_FOLDER = INPUT_DATASETS_DIR / INPUT_DATASET_FOLDER_NAMES[SELECTED_DATASET_OPTION]

        GP__PREVIEW_INPUT = POINT_CLOUD_FOLDER
        GP__PREVIEW_OUTPUT = WORK_DIR / f"{POINT_CLOUD_FOLDER.name}_previews"

        match NND__CURRENT_CASE_IDX:
            case 0: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__BASE = POINT_CLOUD_FOLDER
            case 1: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__REMOVAL = POINT_CLOUD_FOLDER
            case 2: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PERTURBED = POINT_CLOUD_FOLDER
            case 3: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PER_REM = POINT_CLOUD_FOLDER
            case 4: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__ROTATION = POINT_CLOUD_FOLDER
            case 5: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__TRANSLATION = POINT_CLOUD_FOLDER
            case 6: NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__NOISE = POINT_CLOUD_FOLDER

        MCIHELP__POINT_CLOUD_FOLDER = POINT_CLOUD_FOLDER

    case PIPELINE_CONFIG_OPTIONS.REBUILT_EACH_WITH_STEP:

        #Every value is the recommended one above.
        pass

    case PIPELINE_CONFIG_OPTIONS.USE_CUSTOM_FILENAMES:

    #This section in case you want to use custom settings.
    #Any value not set here keeps the recommended value of SELECTED_DATASET_OPTION.
    #Relative folder names are written as WORK_DIR / "name"; absolute paths can also be used.
    #Example below: a full rigid run (translation + rotation), every value of every step is listed.
    #Use it with SELECTED_DATASET_OPTION = TRANSLATION or ROTATION so the run folder name matches.



        #############################
        # [generate_perlin_files.py]
        #############################

        # STEP 1 Perlin Files Generation (PFG)

        PFG__DEFAULT_DATASET_CSV_FILE = PERLIN_BASE_CSV_DATASET_DIR / 'perlin_base_dataset.csv'
        PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER = WORK_DIR / 'perlin_base_point_clouds'


        ##################################
        # generate_cross_perlin_files.py
        ##################################

        # STEP 2 Perlin Cross Files Generation (GCPF) (this only makes sense to do on original Perlin Clouds)
        # Not used in a rigid run, set both to a folder to generate the cross point sets.

        GCPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = None
        GCPF__OUTPUT_FOLDER = None


        #####################################
        # generate_transformation_perlin_files.py
        ########################################

        # STEP 2 Perlin Transformation Files Generation (GTPF)
        # GTPF__OPTION: "Perturbation" (perturbation_transforms.csv) or "Translation_Rotation" (rigid_transforms.csv)

        GTPF__DEFAULT_BASE_POINT_CLOUD_FOLDER = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER
        GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER = WORK_DIR / 'perlin_point_clouds_rigid'
        GTPF__OPTION = "Translation_Rotation"


        ##################################################
        # generate_previews.py
        ##################################################

        # STEP 3 Previews (GP)

        GP__PREVIEW_INPUT = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER
        GP__PREVIEW_OUTPUT = WORK_DIR / 'perlin_point_clouds_rigid_previews'


        ##################################################
        # generate_nearest_neighbour_distances_files.py
        ##################################################

        # STEP 4 Perlin NN Distances (NND)

        NND__ANALYSIS_DATE = DATEIDENTIFIER

        # Point sets folder of each case, only the one of NND__CURRENT_CASE_IDX is read.
        # Cases not generated in this run are set to None.
        NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__BASE = PFG__DEFAULT_BASE_POINT_CLOUD_FOLDER
        NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__REMOVAL = None
        NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PERTURBED = None
        NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__PER_REM = None

        #generate_nearest_neighbour_distances_files.py handles rotation and translation cases plot cases in isolation, so
        #the same folder where transformations can be used.
        NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__ROTATION = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER
        NND__TRANSFORMED_POINT_CLOUD_FOLDER_NAMES__CASE__TRANSLATION = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER

        # Case index: 0 Base, 1 Removal, 2 Perturbed, 3 Perturbed+Removal, 4 Rotation, 5 Translation, 6 Impulsive noise
        NND__CURRENT_CASE_IDX = 4


        ############################
        # mci_commands_helper.py
        ############################

        # STEP 5 MCI (MCIHELP)
        # MCIHELP__SET_TYPE: "Cross_Set", "Perturbation" or "Rigid_Transformation" (must match the point sets names)

        MCIHELP__POINT_CLOUD_FOLDER = GTPF__DESTINATION_TRANSFORMED_POINT_CLOUD_FOLDER
        MCIHELP__SET_TYPE = "Rigid_Transformation"
        MCIHELP__OUTPUT_FOLDER = WORK_DIR / "MCI"


        ##############################
        # heatmap_runner.py
        ##############################

        # STEP 6 Heatmaps (HR)
        # Cases: "cross", "perturbations", "removals", "rigid", "per+rem", each one needs its MCI folder in HR__MCI_FOLDERS.

        HR__HEATMAP_CASES = ["rigid"]
        HR__MCI_FOLDERS = {"rigid": MCIHELP__OUTPUT_FOLDER}
        HR__OUTPUT_FOLDER = WORK_DIR / 'heatmap'



#Do not modify these.
########

MEASURMENTS_CSV_FILENAME = "measurements.csv" #Measurements csv file per folder name which are autogenerated by the MCI calculator.
NO_VALUE = "0" #Null string for the heatmaps except the perturbation + removal which cannot be used because none removals are possible.
