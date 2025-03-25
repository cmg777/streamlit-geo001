import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os

# --- Constants ---
DATA_PATH = "map_and_data.geojson"
DEFINITIONS_PATH = 'dataDefinitions.csv'
DEFAULT_VAR_NAME = "imds"

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Geo Viz")

# --- Data Loading ---
@st.cache_data
def load_geo_data(path):
    if not os.path.exists(path):
        st.error(f"Required data file not found: {path}")
        st.stop() # Halt execution if data isn't there
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
            st.warning(f"Could not load labels from {path}: {e}") # Optional warning
    return labels

# --- Main App ---
st.title("Geographic Data Visualization")

data = load_geo_data(DATA_PATH)
labels = load_labels(DEFINITIONS_PATH)

numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
var_options = [(col, labels.get(col, col)) for col in numeric_cols]

# Find default index (case-insensitive)
default_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == DEFAULT_VAR_NAME.lower()), 0)

# Sidebar Selector
selected_idx = st.sidebar.selectbox(
    "Select variable:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1], # Display labels
    index=default_idx
)
selected_col, selected_label = var_options[selected_idx]

# --- Create Map ---
st.subheader(f"Map of: {selected_label}")

# Calculate center (optional, Plotly often auto-centers well)
bounds = data.total_bounds
center = {"lat": (bounds[1] + bounds[3]) / 2, "lon": (bounds[0] + bounds[2]) / 2}

fig = px.choropleth_mapbox(
    data,
    geojson=data.geometry, # Directly use geometry
    locations="id",
    color=selected_col,
    hover_name="mun", # Assumes 'mun' column exists
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=5.0,
    center=center,
    opacity=0.7,
    labels={selected_col: selected_label} # Nicer label in legend/tooltip
)

fig.update_layout(margin={"r":0, "t":30, "l":0, "b":0}, height=600)
st.plotly_chart(fig, use_container_width=True)

st.sidebar.info(f"Displaying: {selected_label} (`{selected_col}`)")