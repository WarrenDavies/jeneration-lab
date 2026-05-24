import streamlit as st
import pandas as pd
import yaml
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

selected_experiment_id = experiment_location_map[selected_experiment]["experiment_id"]
df_artifacts = pd.read_csv("data/artifacts.csv")
df_artifacts = df_artifacts[df_artifacts["experiment_id"] == selected_experiment_id]
df_artifacts = utils.expand_json_to_cols(
    df_artifacts,
    "params"
)

df_selected_experiment = utils.apply_experiment_filter(
    df_all_experiments,
    selected_experiment,
    experiment_location_map
)
selected_files = df_artifacts["filename"].to_list()

with open(Path(experiment_location_map[selected_experiment]["output_path"]).parent / "experiment.yaml" , 'r') as stream:
    experiment_config = yaml.safe_load(stream)

############################
#### Display Image Grid ####
############################
if experiment_config["experiment"]["generation_format"] == "image":

    if len(df_artifacts) > 0:
        steps_range = utils.add_range_filter(
            df_artifacts,
            "num_inference_steps", 
            1,
            "Select Inference Steps Range"
        )
        df_artifacts = utils.apply_range_filter(
            df_artifacts,
            "num_inference_steps",
            steps_range
        )

    if len(df_artifacts) > 0:
        cfg_range = utils.add_range_filter(
            df_artifacts,
            "guidance_scale", 
            1,
            "Select Guidance Scale Range"
        )
        df_artifacts = utils.apply_range_filter(
            df_artifacts,
            "guidance_scale",
            cfg_range
        )

    selected_files = df_artifacts["filename"].to_list()

    view_mode = st.radio("View Mode", ["Gallery", "Matrix"])

    if len(df_artifacts) > 0:
        if view_mode == "Matrix":
            st.markdown("""
                <style>
                    img {
                        border-radius: 0 !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            rows = sorted(df_artifacts["guidance_scale"].unique())
            cols = sorted(df_artifacts["num_inference_steps"].unique())

            st.write(f"**Rows: Guidance Scale | Columns: Inference Steps**")
            header_cols = st.columns([1] + [2 for _ in cols])
            for i, col_val in enumerate(cols):
                header_cols[i+1].write(f"**{col_val}**")

            for row_val in rows:
                row_cols = st.columns([1] + [2 for _ in cols])
                row_cols[0].write(f"**{str(int(row_val))}**")
                
                for i, col_val in enumerate(cols):
                    match = df_artifacts[
                        (df_artifacts["guidance_scale"] == row_val) & 
                        (df_artifacts["num_inference_steps"] == col_val)
                    ]
                    
                    with row_cols[i+1]:
                        if not match.empty:
                            img_path = df_selected_experiment.iloc[0]["output_path"] + "/" + match.iloc[0]["filename"] 
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
                st.write("The experiment folder may have been deleted, or you may need to adjust your filters.")

            utils.render_image_grid(images, df_artifacts, no_of_cols)
    else:
        st.write("No artifacts found.")

    ############################
    ##### Display Raw Data #####
    ############################
    st.write("Raw Data")
    st.dataframe(df_artifacts)

##############################
#### Display Text Outputs ####
##############################

if experiment_config["experiment"]["generation_format"] == "text":

    if len(df_artifacts) > 0:
        temperature_range = utils.add_range_filter(
            df_artifacts,
            "temperature", 
            0.1,
            "Select temperature Range",
            "float"
        )
        df_artifacts = utils.apply_range_filter(
            df_artifacts,
            "temperature",
            temperature_range
        )

    if len(df_artifacts) > 0:
        top_p_range = utils.add_range_filter(
            df_artifacts,
            "top_p", 
            0.1,
            "Select top_p Range",
            "float"
        )
        df_artifacts = utils.apply_range_filter(
            df_artifacts,
            "top_p",
            top_p_range
        )

    if len(df_artifacts) > 0:
        top_k_range = utils.add_range_filter(
            df_artifacts,
            "top_k", 
            0.1,
            "Select top_k Range",
            "float"
        )
        df_artifacts = utils.apply_range_filter(
            df_artifacts,
            "top_k",
            top_k_range
        )

    selected_files = df_artifacts["filename"].to_list()


    text_artifacts_paths = utils.get_images(
        experiment_location_map, 
        selected_experiment,
        selected_files
    )


    if len(df_artifacts) > 1:
        text_artifacts = []
        for text_artifact_path in text_artifacts_paths:
            with open(text_artifact_path, 'r') as file:
                content = file.read()
                text_artifacts.append({'filename': Path(text_artifact_path).name, 'text': content})
        
        df_text_artifacts = pd.DataFrame(text_artifacts)
        df_artifacts = pd.merge(df_text_artifacts, df_artifacts, on='filename', how='left')

        view_mode = st.radio("View Mode", ["Table", "json"])


        all_columns = df_artifacts.columns.tolist()
        selected_cols = st.multiselect(
            "Select columns to display:",
            options=all_columns,
            default=all_columns
        )
        if selected_cols:
            df_artifacts = df_artifacts[selected_cols]

            if view_mode == "Table":
                st.dataframe(df_artifacts)

            if view_mode == "json":
                dict_artifacts = df_artifacts.to_dict('records')
                st.write(dict_artifacts)

        else:
            st.warning("Please select at least one column to view.")
    else:
        st.write("No artifacts found.")
    
    


