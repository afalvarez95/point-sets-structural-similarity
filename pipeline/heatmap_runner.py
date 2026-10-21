import subprocess
import matplotlib
import os
import sys

matplotlib.use('TkAgg') 


from config import HR__HEATMAP_CASES, HR__MCI_FOLDERS, HR__OUTPUT_FOLDER

for option in HR__HEATMAP_CASES:
    suboption = "1nn"
    suboption_title = f"{suboption.upper()}"

    HAS_TYPES = option == "rigid"

    script = {"cross":"generate_heatmap_cross_perlin_files.py",
            "perturbations":"generate_heatmap_perturbations.py",
            "removals":"generate_heatmap_removal.py",
            "rigid":"generate_heatmap_transl_rot.py",
            "per+rem":"generate_heatmap_rem_and_pert.py"}

    initial_titles = {"cross":f"Cross Perlin Point Sets",
                "perturbations":f"Perturbed Perlin Point Sets",
                "removals":f"Point Removal Perlin Point Sets",
                "rigid":f"Rigid Transform operators Perlin Point Sets",
                "per+rem":f"Perturbed and Removed Perlin Point Sets"}

    MCI_FOLDER = str(HR__MCI_FOLDERS[option])

    MCI_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), script[option])


    MEASUREMENTS = ["mci","avg_haussdorf_distance_value","p95_haussdorf_distance_value","haussdorf_distance_value","wasserstein"]

    MEASUREMENTS_TITLES = [f"MCI using P95 Max {suboption_title}","Avg Haussdorf Distance","P95 Haussdorf Distance","Haussdorf Distance","Sliced Wasserstein Distance"]

    OUTPUT_FOLDER = os.path.join(HR__OUTPUT_FOLDER, option)

    TYPES = ["rotation","translation"]


    TYPES_NAMES = {"rotation":"Rotations","translation":"Translations"}

    REVERSE = "--reverse"



    if not HAS_TYPES:
        for m,mt in zip(MEASUREMENTS,MEASUREMENTS_TITLES):
            formatted_title = f"{initial_titles[option]} {mt} Heatmap"
            print(MCI_SCRIPT, MCI_FOLDER ,f"\"{m}\"", f"\"{mt}\"", REVERSE)

            subprocess.run(
            [sys.executable, MCI_SCRIPT, MCI_FOLDER ,m, formatted_title, OUTPUT_FOLDER, REVERSE],
            encoding="cp1252"
            )
    else:
        for type_ in TYPES:
            for m,mt in zip(MEASUREMENTS,MEASUREMENTS_TITLES):
                print("IN TYPES")
                formatted_title = f"{initial_titles[option]} - {TYPES_NAMES[type_]} - {mt} Heatmap"
                print(MCI_SCRIPT, MCI_FOLDER ,f"\"{m}\"", f"\"{mt}\"", type_, OUTPUT_FOLDER, REVERSE)

                subprocess.run(
                [sys.executable, MCI_SCRIPT, MCI_FOLDER ,m, formatted_title, f"{type_}", OUTPUT_FOLDER, REVERSE],
                encoding="cp1252"
                )