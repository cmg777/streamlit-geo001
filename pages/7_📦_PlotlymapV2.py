import os
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(layout="wide", page_title="Geographic Data Visualization")

# Load geographic data
@st.cache_data
def load_data():
    data_path = "map_and_data.geojson"
    if os.path.exists(data_path):
        data = gpd.read_file(data_path)
    else:
        with st.spinner("Loading data..."):
            data = gpd.read_file('https://github.com/quarcs-lab/project2021o-notebook/raw/main/map_and_data.geojson')
            data.to_file(data_path, driver="GeoJSON")
    data = data.to_crs(epsg=4326)
    data["id"] = data.index.astype(str)
    return data

# Load data dictionary
@st.cache_data
def load_data_dictionary():
    variable_labels = {}
    if os.path.exists('dataDefinitions.csv'):
        reader = pd.read_csv('dataDefinitions.csv', encoding='utf-8')
        if 'Variable' in reader.columns and 'Label' in reader.columns:
            variable_labels = dict(zip(reader['Variable'], reader['Label']))
    return variable_labels

# Main app
st.title("Geographic Data Visualization")
st.write("This application visualizes geographic data on an interactive map.")

# Load data
data = load_data()
variable_labels = load_data_dictionary()

# Get numeric columns
numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Create variable options with labels
variable_options = [(col, variable_labels.get(col, col)) for col in numeric_columns]

# Find default index for imds
default_index = 0
for i, (col, _) in enumerate(variable_options):
    if col.lower() == "imds":
        default_index = i
        break

# Display dropdown with labels
selected_index = st.sidebar.selectbox(
    "Select variable to display:", 
    options=range(len(variable_options)),
    format_func=lambda i: variable_options[i][1],
    index=default_index
)

# Get selected column name
color_column = variable_options[selected_index][0]

# Display map title
st.subheader(f"Map of {variable_options[selected_index][1]}")

# Create map
bounds = data.total_bounds
center_lon = (bounds[0] + bounds[2]) / 2
center_lat = (bounds[1] + bounds[3]) / 2

fig = px.choropleth_mapbox(
    data_frame=data,
    geojson=data.__geo_interface__,
    locations="id",
    color=color_column,
    hover_name="mun",
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=5.0,
    center={"lat": center_lat, "lon": center_lon},
    opacity=0.7
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=600,
    autosize=True
)

st.plotly_chart(fig, use_container_width=True)