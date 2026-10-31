import os
import gradio as gr
import glob
import pandas as pd
from pathlib import Path

image_files = []
current_index = 0
image_folder = ""

def list_first_level_folders(folder_path):
    try:
        entries = os.listdir(folder_path)
        folders = [entry for entry in entries if os.path.isdir(os.path.join(folder_path, entry))]
        return folders
    except Exception as e:
        return []


def dual_cloud_folder(selected_folder, base_folder_input):
    #<selected>/<dual cloud>/: the dual cloud folder has the same name in the pipeline runs, but not in sample_results
    folder = os.path.join(base_folder_input, selected_folder)
    inner = list_first_level_folders(folder)
    return os.path.join(folder, selected_folder if selected_folder in inner else inner[0])


def change_frames_folder(selected_folder, base_folder_input):
    global image_files, image_folder, current_index
    image_folder = os.path.join(dual_cloud_folder(selected_folder, base_folder_input), "frames")
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith('.png')]
    image_files = sorted(image_files, key = lambda x: int(x.split('_')[1].split('.')[0]))
    current_index = 0
    return get_image_at_index(current_index)



def get_image_at_index(index):
    if 0 <= index < len(image_files):
        return os.path.join(image_folder, image_files[index])
    return None

def next_image():
    global current_index
    if current_index < len(image_files) - 1:
        current_index += 1
    return get_image_at_index(current_index)

def prev_image():
    global current_index
    if current_index > 0:
        current_index -= 1
    return get_image_at_index(current_index)

def get_video_file(selected_folder,base_folder_input):
    mp4_files = glob.glob(os.path.join(dual_cloud_folder(selected_folder,base_folder_input),'*.mp4'))
    if mp4_files:
        return mp4_files[0]
    else:
        return ''


def get_measurements(selected_folder,base_folder_input):
    measurements_csv = os.path.join(base_folder_input,selected_folder,'measurements.csv')
    measurements_df = pd.read_csv(measurements_csv)
    return tuple(measurements_df.loc[0, ['mci', 'wasserstein', 'avg_haussdorf_distance_value','p95_haussdorf_distance_value','haussdorf_distance_value']])

def get_jd_per_radius_plot(selected_folder,base_folder_input):
    return glob.glob(os.path.join(dual_cloud_folder(selected_folder,base_folder_input),'*_jd_per_r_plot.png'))[0]


with gr.Blocks(fill_height=True,fill_width=True) as demo:
    with gr.Row():
        with gr.Column():
            default_folder = Path(__file__).parent.parent / "sample_results"
            with gr.Row():
                base_folder_input = gr.Textbox(label="Enter folder path of the data...", value=default_folder)
            list_button = gr.Button("List Subfolders")
            folder_dropdown = gr.Dropdown(choices=[], label="Select or search a subfolder")
            with gr.Row():
                mci_value = gr.Textbox(label="MCI",interactive=False)
                wass_value = gr.Textbox(label="Sliced Wasserstein Distance",interactive=False)
                avg_haus_value = gr.Textbox(label="Average Haussdorf Distance",interactive=False)
                p95_haus_value = gr.Textbox(label="P95 Haussdorf Distance",interactive=False)
                haus_value = gr.Textbox(label="Haussdorf Distance",interactive=False)
            plot_jd_image = gr.Image(label="AuC of J_δ per radius")

        
        with gr.Column():
            with gr.Row():
                prev_button = gr.Button("⯇", size="sm")
                next_button = gr.Button("⯈", size="sm")
            frame_image_slideshow = gr.Image(label='Closing per radius frames')
            frame_video = gr.Video(label="Closing per radius video", show_label=True,elem_id="closing_video")

        
        def update_folder_list(folder_path):
            folders = list_first_level_folders(folder_path)
            return gr.update(choices=folders)
        
    
        def initialize():
            folders = list_first_level_folders(default_folder)
            return gr.update(choices=folders)
        
        demo.load(lambda: initialize(), inputs=None, outputs=folder_dropdown)
    
        list_button.click(update_folder_list, base_folder_input, folder_dropdown)
        folder_dropdown.change(get_video_file, inputs=[folder_dropdown,base_folder_input], outputs=frame_video)
        folder_dropdown.change(get_measurements, inputs=[folder_dropdown,base_folder_input], outputs=[mci_value,wass_value,avg_haus_value,p95_haus_value,haus_value])
        folder_dropdown.change(get_jd_per_radius_plot, inputs=[folder_dropdown,base_folder_input], outputs=plot_jd_image)
        folder_dropdown.change(change_frames_folder, inputs=[folder_dropdown, base_folder_input], outputs=frame_image_slideshow)
        prev_button.click(prev_image, inputs=[], outputs=frame_image_slideshow)
        next_button.click(next_image, inputs=[], outputs=frame_image_slideshow)

#The frames, plots and videos are served from the project folder (sample_results/, runs/)
demo.launch(server_port=7860,share=False,allowed_paths=[str(Path(__file__).parent.parent)])
