import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os

# --- Constants ---
DATA_PATH = "map_and_data.geojson"
DEFINITIONS_PATH = 'dataDefinitions.csv'
# Default indicators
INDICATOR1 = 'imds'         # For coloring
INDICATOR2 = 'pop2020'      # For size of treemap blocks
INDICATOR3 = 'ln_t400NTLpc2012'  # Additional indicator
INDICATOR4 = 'rank_imds'    # For hover data
ADM1 = 'dep'               # Department (Administrative level 1)
ADM3 = 'mun'               # Municipality (Administrative level 3)

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

# Find default indices for indicators (case-insensitive)
default_color_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == INDICATOR1.lower()), 0)
default_size_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == INDICATOR2.lower()), 0)
default_hover_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == INDICATOR4.lower()), 0)

# Sidebar Selectors
st.sidebar.header("Treemap Configuration")
selected_color_idx = st.sidebar.selectbox(
    "Select color indicator:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_color_idx
)
selected_color_col, selected_color_label = var_options[selected_color_idx]

selected_size_idx = st.sidebar.selectbox(
    "Select size indicator:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_size_idx
)
selected_size_col, selected_size_label = var_options[selected_size_idx]

selected_hover_idx = st.sidebar.selectbox(
    "Select additional hover data:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_hover_idx
)
selected_hover_col, selected_hover_label = var_options[selected_hover_idx]

# Verify that required columns exist
required_cols = [ADM1, ADM3, selected_color_col, selected_size_col, selected_hover_col]
missing_cols = [col for col in required_cols if col not in data.columns]

if missing_cols:
    st.error(f"Required column(s) not found: {', '.join(missing_cols)}")
    st.stop()

# --- Create Treemap ---
st.subheader(f"Treemap of Municipalities by Department")

# Create a dictionary for custom labels
data_dict = {
    selected_color_col: selected_color_label,
    selected_size_col: selected_size_label,
    selected_hover_col: selected_hover_label,
    ADM1: labels.get(ADM1, "Department"),
    ADM3: labels.get(ADM3, "Municipality")
}

fig = px.treemap(
    data,
    color=selected_color_col,              # Data for coloring (e.g., IMDS)
    values=selected_size_col,              # Data for size of treemap blocks (e.g., population)
    path=[ADM1, ADM3],                     # Path for hierarchical display (department -> municipality)
    hover_name=ADM3,                       # Municipality name for hover tooltip
    hover_data=[selected_hover_col],       # Additional data for hover tooltip
    labels=data_dict                       # Custom labels
)

fig.update_layout(
    height=700,
    margin={"r": 0, "t": 30, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)

# Explanation
st.sidebar.info(f"""
Treemap Configuration:
- Color: {selected_color_label}
- Size: {selected_size_label}
- Additional hover data: {selected_hover_label}
""")

# Add description of the visualization
st.markdown("""
### About This Visualization

This treemap organizes municipalities hierarchically by department. Each rectangle represents a municipality, with:

- **Size** proportional to the selected size indicator
- **Color** representing the selected color indicator
- **Hover** showing municipality name and additional selected indicator

Click on a department section to zoom in and see more details about its municipalities.
""")