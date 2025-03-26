import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os

# --- Constants ---
DATA_PATH = "map_and_data.geojson"
DEFINITIONS_PATH = 'dataDefinitions.csv'
DEFAULT_X_VAR = "imds"
DEFAULT_ADD_VAR = "ln_t400NTLpc2012"  # Default for additional indicator
ADM1 = 'dep'  # Administrative level 1 (department)
ADM3 = 'mun'  # Administrative level 3 (municipality)

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Geo Viz")

# --- Data Loading ---
@st.cache_data
def load_geo_data(path):
    if not os.path.exists(path):
        st.error(f"Required data file not found: {path}")
        st.stop()  # Halt execution if data isn't there
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=4326)
    gdf["id"] = gdf.index.astype(str)
    return gdf

@st.cache_data
def load_labels(path):
    labels = {}
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, encoding='utf-8')
            if 'Variable' in df.columns and 'Label' in df.columns:
                # Use variable name as label if label is missing
                df['Label'] = df['Label'].fillna(df['Variable'])
                labels = dict(zip(df['Variable'], df['Label']))
        except Exception as e:
            st.warning(f"Could not load labels from {path}: {e}")
    return labels

# --- Main App ---
st.title("Municipal Data Visualization")

data = load_geo_data(DATA_PATH)
labels = load_labels(DEFINITIONS_PATH)
numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
var_options = [(col, labels.get(col, col)) for col in numeric_cols]

# Find default indices (case-insensitive)
default_x_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == DEFAULT_X_VAR.lower()), 0)
default_add_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == DEFAULT_ADD_VAR.lower()), 0)

# Sidebar Selectors
st.sidebar.header("Variables")
selected_x_idx = st.sidebar.selectbox(
    "Select main indicator (x-axis):",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_x_idx
)
selected_x_col, selected_x_label = var_options[selected_x_idx]

selected_add_idx = st.sidebar.selectbox(
    "Select additional indicator (for hover):",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_add_idx
)
selected_add_col, selected_add_label = var_options[selected_add_idx]

# Verify that department column exists
if ADM1 not in data.columns:
    st.error(f"Required column '{ADM1}' not found in the dataset. Available columns: {', '.join(data.columns)}")
    st.stop()

# Verify that municipality column exists
if ADM3 not in data.columns:
    st.error(f"Required column '{ADM3}' not found in the dataset. Available columns: {', '.join(data.columns)}")
    st.stop()

# --- Create Histogram ---
st.subheader(f"Distribution of {selected_x_label}")

# Create a dictionary for custom labels
data_dict = {
    selected_x_col: selected_x_label,
    ADM1: labels.get(ADM1, "Department"),
    selected_add_col: selected_add_label
}

fig = px.histogram(
    data,
    x=selected_x_col,                # Main indicator for x-axis
    color=ADM1,                      # Color grouping based on department
    hover_name=ADM3,                 # Municipality for hover tooltip
    marginal='rug',                  # Display rug plot on the marginal axis
    hover_data=[ADM1, selected_add_col],  # Additional data for hover tooltip
    labels=data_dict                 # Custom labels
)

fig.update_layout(
    height=600,
    margin={"r": 0, "t": 30, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)
st.sidebar.info(f"Visualizing distribution of: {selected_x_label} (`{selected_x_col}`) by Department with additional hover data: {selected_add_label}")