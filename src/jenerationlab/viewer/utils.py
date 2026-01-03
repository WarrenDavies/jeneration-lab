from pathlib import Path
import json
import yaml

from PIL import Image
import pandas as pd
import numpy as np
import streamlit as st

from jenerationlab.viewer import constants


def get_config():
    with open("configs/core_config.yaml", 'r') as stream:
        core_config = yaml.safe_load(stream)

    core_config["outputs_path"] = Path(core_config["outputs_path"])
    core_config["data_source_path"] = Path(
        core_config["data_source_location"]
    )

    core_config["experiments_folders"] = [
        p.name 
        for p in core_config["outputs_path"].iterdir() 
        if p.is_dir()
    ]

    return core_config


def get_mtime(path: Path):
    return path.stat().st_mtime


def to_readable_timestamp(ts):
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}  {ts[8:10]}:{ts[10:12]}:{ts[12:]}"


@st.cache_data
def load_experiment_results(exp_path, experiments_folders, mtime):
    df = pd.read_csv(exp_path, header=0)
    experiment_exists = df["timestamp"].isin(experiments_folders)
    df = df[experiment_exists]
    return df


@st.cache_data
def get_experiment_list(df):
    df = df.copy()

    df["readable_timestamp"] = df["timestamp"].apply(to_readable_timestamp)
    df["dropdown_selector"] = (
        np.where( pd.notnull(df["experiment_name"]), 
        df["experiment_name"].str.cat(df["readable_timestamp"].astype(str), sep=" - "),
        df["readable_timestamp"].astype(str)
    ))
    df = df.sort_values(by="readable_timestamp", ascending=False)
    df = df[['dropdown_selector', 'output_path', 'experiment_id']]
    df = df.drop_duplicates()
    experiment_selectors = df.set_index('dropdown_selector').to_dict(
        orient="index"
    )
    return experiment_selectors


def expand_json_to_cols(df, json_col):
    dicts = df[json_col].apply(json.loads)
    df_params = pd.json_normalize(dicts)
    df_base = df.drop(columns=[json_col]).reset_index(drop=True)
    df = pd.concat(
        [df_base, df_params], 
        axis=1
    )
    return df


def apply_experiment_filter(
    df_all_experiments,
    selected_experiment,
    experiment_location_map
):
    if selected_experiment == "-- All --":
        return df_all_experiments

    selected_experiment_id = (
        experiment_location_map[selected_experiment]["experiment_id"]
    )
    selected_experiment_mask = (
        df_all_experiments["experiment_id"] == selected_experiment_id
    )
    df_selected_experiment = (
        df_all_experiments[selected_experiment_mask]
    )

    return df_selected_experiment


def add_range_filter(df, col, step, title):
    min_value = int(df[col].min())
    max_value = int(df[col].max())
    if min_value == max_value:
        max_value += 1
    range_ = st.sidebar.slider(
        title,
        min_value=min_value,
        max_value=max_value,
        value=(min_value, max_value),
        step=step
    )
    return range_


def apply_range_filter(df, col, range_):
    df = df.copy()
    df = df[
        (df[col] >= range_[0]) & 
        (df[col] <= range_[1])
    ]
    return df


def get_artifact_params(df, filename):
    params = df[df["filename"] == filename].to_dict(orient="records")

    return params[0]


def get_pretty_name(stat):
    if stat in constants.STAT_PRETTY_NAMES:
        return constants.STAT_PRETTY_NAMES[stat]

    return stat.title()


def display_artifact_stats(params, stats):
    lines = [
        f"**{get_pretty_name(stat)}:** {params[stat]}" 
        for stat in stats 
        if stat in params
    ]
    if lines:
        st.markdown("<br>".join(lines), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def get_images(experiment_location_map, selected_experiment, selected_files):
    image_dir = experiment_location_map[selected_experiment]["output_path"]
    images = sorted(Path(image_dir).glob('*'))
    images = [image for image in images if image.name in selected_files]

    return images


def render_image_grid(images, df, no_of_cols):
    cols = st.columns(no_of_cols)
    for i, img_path in enumerate(images):
        with cols[i % no_of_cols]:
            
            img = Image.open(img_path)
            st.image(img, caption=img_path.name, use_container_width=True)

            params_to_display = get_artifact_params(
                df,
                img_path.name
            )
            
            display_artifact_stats(
                params_to_display, 
                ["num_inference_steps", "guidance_scale"]
            )