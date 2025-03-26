import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os

# --- Constants ---
DATA_PATH = "map_and_data.geojson"
DEFINITIONS_PATH = 'dataDefinitions.csv'
DEFAULT_X_VAR = "imds"
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

# Find default index for x variable (case-insensitive)
default_x_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == DEFAULT_X_VAR.lower()), 0)

# Sidebar Selectors
st.sidebar.header("Variables")
selected_x_idx = st.sidebar.selectbox(
    "Select indicator variable:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_x_idx
)
selected_x_col, selected_x_label = var_options[selected_x_idx]

# Verify that department column exists
if ADM1 not in data.columns:
    st.error(f"Required column '{ADM1}' not found in the dataset. Available columns: {', '.join(data.columns)}")
    st.stop()

# Verify that municipality column exists
if ADM3 not in data.columns:
    st.error(f"Required column '{ADM3}' not found in the dataset. Available columns: {', '.join(data.columns)}")
    st.stop()

# --- Create Strip Plot ---
st.subheader(f"{selected_x_label} by {ADM1}")

# Create a dictionary for custom labels
data_dict = {
    selected_x_col: selected_x_label,
    ADM1: labels.get(ADM1, "Department")
}

fig = px.strip(
    data,
    x=selected_x_col,            # Selected indicator
    y=ADM1,                      # Department for y-axis
    color=ADM1,                  # Color grouping based on department
    hover_name=ADM3,             # Municipality for hover tooltip
    labels=data_dict             # Custom labels
)

fig.update_layout(
    height=600,
    margin={"r": 0, "t": 30, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)
st.sidebar.info(f"Visualizing: {selected_x_label} (`{selected_x_col}`) by Department")