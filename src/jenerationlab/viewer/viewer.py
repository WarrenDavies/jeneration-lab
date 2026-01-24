import streamlit as st
import pandas as pd
from pathlib import Path

from PIL import Image

from jenerationlab.viewer import utils


config = utils.get_config()


#############################
####### Process Data ########
#############################
df_all_experiments = utils.load_experiment_results(
    config["data_source_path"],
    config["experiments_folders"],
    config["data_source_path"].stat().st_mtime
)

df_all_experiments = utils.expand_json_to_cols(
    df_all_experiments,
    "params"
)

experiment_location_map = utils.get_experiment_list(
    df_all_experiments
)

experiment_dropdown_options = list(experiment_location_map.keys())


#############################
##### Add site sections #####
#############################
st.set_page_config(layout="wide")
st.title("Jeneration Lab")
st.write("Experiment Result Viewer.")
st.sidebar.header("Filters")


############################
######### Filters ##########
############################
selected_experiment = st.selectbox(
    "Select experiment",
    experiment_dropdown_options,
    index=0
)

df_selected_experiment = utils.apply_experiment_filter(
    df_all_experiments,
    selected_experiment,
    experiment_location_map
)

steps_range = utils.add_range_filter(
    df_selected_experiment,
    "num_inference_steps", 
    1,
    "Select Inference Steps Range"
)

df_selected_experiment = utils.apply_range_filter(
    df_selected_experiment,
    "num_inference_steps",
    steps_range
)

cfg_range = utils.add_range_filter(
    df_selected_experiment,
    "guidance_scale", 
    1,
    "Select Guidance Scale Range"
)

df_selected_experiment = utils.apply_range_filter(
    df_selected_experiment,
    "guidance_scale",
    cfg_range
)

selected_files = df_selected_experiment["filename"].to_list()


############################
#### Display Image Grid ####
############################
view_mode = st.radio("View Mode", ["Gallery", "Matrix"])

if view_mode == "Matrix":
    st.markdown("""
        <style>
            img {
                border-radius: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    rows = sorted(df_selected_experiment["guidance_scale"].unique())
    cols = sorted(df_selected_experiment["num_inference_steps"].unique())

    st.write(f"**Rows: Guidance Scale | Columns: Inference Steps**")
    header_cols = st.columns([1] + [2 for _ in cols])
    for i, col_val in enumerate(cols):
        header_cols[i+1].write(f"**{col_val}**")

    for row_val in rows:
        row_cols = st.columns([1] + [2 for _ in cols])
        row_cols[0].write(f"**{str(int(row_val))}**")
        
        for i, col_val in enumerate(cols):
            match = df_selected_experiment[
                (df_selected_experiment["guidance_scale"] == row_val) & 
                (df_selected_experiment["num_inference_steps"] == col_val)
            ]
            
            with row_cols[i+1]:
                if not match.empty:
                    img_path = match.iloc[0]["output_path"] + "/" + match.iloc[0]["filename"] 
                    img = Image.open(img_path)
                    st.image(img)
                else:
                    st.write("-")

if view_mode == "Gallery":
    no_of_cols = st.slider("Number of columns", 0, 10, 3)
    images = utils.get_images(
        experiment_location_map, 
        selected_experiment,
        selected_files
    )

    if len(images) == 0:
        st.write("No images found for this experiment.")
        st.write("The experiment folder may have been deleted, or you may need to chill out on your filtering a bit.")

    utils.render_image_grid(images, df_all_experiments, no_of_cols)


############################
##### Display Raw Data #####
############################
st.write("Raw Data")
st.dataframe(df_selected_experiment)
