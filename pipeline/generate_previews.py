import pandas as pd
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
from pathlib import Path

from config import GP__PREVIEW_INPUT,GP__PREVIEW_OUTPUT

PREVIEW_INPUT = GP__PREVIEW_INPUT
PREVIEW_OUTPUT = GP__PREVIEW_OUTPUT

def create_preview(csv_file, output_image):
    fig, ax = plt.subplots()
    data = pd.read_csv(csv_file)
    ax.clear()


    colors = {
        'Type 1': (0, 0, 255),
        'Type 2': (255, 255, 0)
    }
    original_points_df = data[data['Type'] == 'Type 1']
    modified_points_df = data[data['Type'] == 'Type 2']

    ax.plot(original_points_df['x'], original_points_df['y'], '.r',markersize=3, label='Point set 1')
    ax.plot(modified_points_df['x'], modified_points_df['y'], '.c',markersize=3, label='Point set 2')

    ax.set_aspect('equal')
    ax.legend(loc='lower left',bbox_to_anchor=(0.94,1))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    csv_file_title = Path(csv_file).name
    title = f'{csv_file_title}'
    ax.set_title(title)
    frame_path = Path(output_path) / output_image
    fig.savefig(frame_path, dpi=200)
    plt.close()


def process_csvs_in_folder(folder_path,output_path):
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            csv_file_path = os.path.join(folder_path, file)
            output_image_path = os.path.join(output_path, f"{os.path.splitext(file)[0]}_preview.png")
            create_preview(csv_file_path, output_image_path)
            print(f"Created preview for {file} in the path {output_image_path}")


folder_path = str(PREVIEW_INPUT)
output_path = str(PREVIEW_OUTPUT)
Path(output_path).mkdir(parents=True, exist_ok=True)
process_csvs_in_folder(folder_path,output_path)

