from pathlib import Path
import json

import pandas as pd
import numpy as np
import streamlit as st

from jenerationlab.viewer import constants

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


def get_artifact_params(df, filename):
    run_row_mask = df["filename"] == filename
    df_run_params = df.loc[run_row_mask, "params"]
    params = df_run_params.iloc[0]
    params = json.loads(params)

    return params


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