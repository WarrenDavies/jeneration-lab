from pathlib import Path
import yaml

from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np


# config

with open("configs/core_config.yaml", 'r') as stream:
    core_config = yaml.safe_load(stream)

OUTPUTS_DIR = Path(core_config["outputs_path"])
DATA_SOURCE_PATH = Path(core_config["data_source_location"])


# functions

def get_mtime(path: Path):
    return path.stat().st_mtime

def to_readable_timestamp(ts):
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}  {ts[8:10]}:{ts[10:12]}:{ts[12:]}"

@st.cache_data
def load_experiment_results(exp_path, mtime):
    return pd.read_csv(exp_path, header=0)

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
    experiment_selectors = df.set_index('dropdown_selector')['output_path'].to_dict()

    return experiment_selectors


# setup

experiments_folders = [p for p in OUTPUTS_DIR.iterdir() if p.is_dir()] # to validate drop-down options
df_experiment_results = load_experiment_results(
    DATA_SOURCE_PATH,
    DATA_SOURCE_PATH.stat().st_mtime
)
experiment_location_map = get_experiment_list(df_experiment_results)
experiment_dropdown_options = list(experiment_location_map.keys())
# experiment_dropdown_options.sort(reverse=True)


# front-end

st.title("Jeneration Lab")
st.write("Experiment Result Viewer.")
selected_experiment = st.selectbox("Select experiment", experiment_dropdown_options)

if selected_experiment:
    image_dir = experiment_location_map[selected_experiment]
    
    images = sorted(Path(image_dir).glob("*.jpg"))

    cols = st.columns(3)

    for i, img_path in enumerate(images):
        with cols[i % 3]:
            img = Image.open(img_path)
            st.image(img, caption=img_path.name, use_container_width=True)
