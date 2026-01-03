from pathlib import Path
import yaml
import json

from PIL import Image
import streamlit as st
import pandas as pd

from jenerationlab.viewer import utils


with open("configs/core_config.yaml", 'r') as stream:
    core_config = yaml.safe_load(stream)

outputs_path = Path(core_config["outputs_path"])
data_source_path = Path(core_config["data_source_location"])

experiments_folders = [p.name for p in outputs_path.iterdir() if p.is_dir()]
df_all_experiments = utils.load_experiment_results(
    data_source_path,
    experiments_folders,
    data_source_path.stat().st_mtime
)
experiment_location_map = utils.get_experiment_list(
    df_all_experiments
)
experiment_dropdown_options = list(experiment_location_map.keys())


# front-end

st.title("Jeneration Lab")
st.write("Experiment Result Viewer.")
selected_experiment = st.selectbox(
    "Select experiment",
    experiment_dropdown_options,
    index=0    
)

selected_experiment_id = (
    experiment_location_map[selected_experiment]["experiment_id"]
)
selected_experiment_mask = df_all_experiments["experiment_id"] == selected_experiment_id
df_selected_experiment = (
    df_all_experiments[selected_experiment_mask]
)

dicts = df_selected_experiment['params'].apply(json.loads)
df_params = pd.json_normalize(dicts)

df_base = df_selected_experiment.drop(columns=['params']).reset_index(drop=True)

df_selected_experiment = pd.concat(
    [df_base, df_params], 
    axis=1
)

st.sidebar.header("Filters")

min_steps = int(df_selected_experiment["num_inference_steps"].min())
max_steps = int(df_selected_experiment["num_inference_steps"].max())
steps_range = st.sidebar.slider(
    "Select Inference Steps Range",
    min_value=min_steps,
    max_value=max_steps,
    value=(min_steps, max_steps),
    step=1
)
df_selected_experiment = df_selected_experiment[
    (df_selected_experiment["num_inference_steps"] >= steps_range[0]) & 
    (df_selected_experiment["num_inference_steps"] <= steps_range[1])
]
selected_files = df_selected_experiment["filename"].to_list()


image_dir = experiment_location_map[selected_experiment]["output_path"]
images = sorted(Path(image_dir).glob('*'))

images = [image for image in images if image.name in selected_files]

if len(images) == 0:
    st.write("No images found for this experiment.")
    st.write("The experiment folder may have been deleted, or you may need to chill out on your filtering a bit.")
cols = st.columns(3)


for i, img_path in enumerate(images):
    with cols[i % 3]:
        
        img = Image.open(img_path)
        st.image(img, caption=img_path.name, use_container_width=True)

        params_to_display = utils.get_artifact_params(
            df_all_experiments,
            img_path.name
        )
        utils.display_artifact_stats(params_to_display, ["num_inference_steps", "guidance_scale"])
st.dataframe(df_selected_experiment)
