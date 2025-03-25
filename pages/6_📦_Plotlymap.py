import os
import logging
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
from typing import Dict, List, Optional

# Custom exception for data loading errors
class DataLoadError(Exception):
    """Exception raised when data cannot be loaded properly."""
    pass

# 🔹 DATA LOADING FUNCTIONS
# These functions handle the loading and caching of geographic and dictionary data.
# 📌 load_data:
#    - Loads geographic data from a local file if available.
#    - Otherwise, retrieves from a remote source, saves locally, and converts CRS.
@st.cache_data(ttl=3600, max_entries=10)
def load_data():
    """Loads and prepares geographic data."""
    try:
        data_path = "map_and_data.geojson"
        if os.path.exists(data_path):
            data = gpd.read_file(data_path)
            logging.info("Loaded data from local file")
        else:
            with st.spinner("Loading geographic data from remote source..."):
                data = gpd.read_file('https://github.com/quarcs-lab/project2021o-notebook/raw/main/map_and_data.geojson')
                data.to_file(data_path, driver="GeoJSON")
                logging.info("Saved data to local file")
        data = data.to_crs(epsg=4326)
        data["id"] = data.index.astype(str)
        return data
    except Exception as e:
        logging.error(f"Failed to load data: {e}", exc_info=True)
        raise DataLoadError(f"Could not load geographic data: {e}")

# 📌 load_data_dictionary:
#    - Loads a CSV file with variable definitions.
#    - Converts it to a dictionary mapping variable names to labels.
@st.cache_data
def load_data_dictionary() -> Dict[str, str]:
    """Loads and parses the data dictionary."""
    try:
        variable_labels = {}
        if os.path.exists('dataDefinitions.csv'):
            # Fixed: Use pandas to read CSV directly
            reader = pd.read_csv('dataDefinitions.csv', encoding='utf-8')
            if 'Variable' in reader.columns and 'Label' in reader.columns:
                variable_labels = dict(zip(reader['Variable'], reader['Label']))
            logging.info(f"Loaded {len(variable_labels)} variable definitions")
            return variable_labels
        else:
            logging.warning("Data dictionary file not found")
            return {}
    except Exception as e:
        logging.error(f"Error loading data dictionary: {e}", exc_info=True)
        st.warning(f"Could not load data dictionary: {e}. Using original column names.")
        return {}

# 📌 create_map:
#    - Creates and displays a choropleth map with the provided data.
def create_map(data, variable_labels, color_column, numeric_columns, selected_regions=None,
               color_scale="Viridis", map_style="carto-positron", zoom=7.0, opacity=0.7, midpoint=None):
    """Creates and displays a choropleth map of the data."""
    try:
        # Prepare geojson data for mapping.
        geojson_dict = data.__geo_interface__
        column_label = variable_labels.get(color_column, color_column)
        hover_cols = [color_column] + [col for col in numeric_columns[:3] if col != color_column]
        labels = {col: variable_labels.get(col, col) for col in hover_cols + ["mun"]}
        
        # Mark selected regions if any.
        if selected_regions:
            data['is_selected'] = data['mun'].isin(selected_regions)
            hover_cols.append('is_selected')
            labels['is_selected'] = 'Selected Region'
            
        # Create the choropleth map using Plotly.
        fig = px.choropleth_mapbox(
            data_frame=data,
            geojson=geojson_dict,
            locations="id",
            color=color_column,
            hover_name="mun",
            hover_data=hover_cols,
            color_continuous_scale=color_scale,
            mapbox_style=map_style,
            zoom=zoom,
            center={"lat": data.geometry.centroid.y.mean(), "lon": data.geometry.centroid.x.mean()},
            opacity=opacity,
            labels=labels,
            color_continuous_midpoint=midpoint
        )
        
        # Update layout parameters for the map.
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=st.session_state.get('map_height', 600),  # Added default value
            autosize=True,
            coloraxis_colorbar=dict(title=column_label, title_side="right")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logging.error(f"Error creating map: {e}", exc_info=True)
        st.error(f"Failed to create map: {e}")