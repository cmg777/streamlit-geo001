import os
import logging
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set page config
st.set_page_config(layout="wide", page_title="Geographic Data Visualization")

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
        st.error(f"Could not load geographic data: {e}")
        return None

# 📌 load_data_dictionary:
#    - Loads a CSV file with variable definitions.
#    - Converts it to a dictionary mapping variable names to labels.
@st.cache_data
def load_data_dictionary() -> Dict[str, str]:
    """Loads and parses the data dictionary."""
    try:
        variable_labels = {}
        if os.path.exists('dataDefinitions.csv'):
            # Read CSV directly with pandas
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
        # Prepare geojson data for mapping
        geojson_dict = data.__geo_interface__
        column_label = variable_labels.get(color_column, color_column)
        hover_cols = [color_column] + [col for col in numeric_columns[:3] if col != color_column]
        labels = {col: variable_labels.get(col, col) for col in hover_cols + ["mun"]}
        
        # Mark selected regions if any
        if selected_regions:
            data['is_selected'] = data['mun'].isin(selected_regions)
            hover_cols.append('is_selected')
            labels['is_selected'] = 'Selected Region'
            
        # Create the choropleth map using Plotly
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
        
        # Update layout parameters for the map
        if 'map_height' not in st.session_state:
            st.session_state.map_height = 600
            
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=st.session_state.map_height,
            autosize=True,
            coloraxis_colorbar=dict(title=column_label, title_side="right")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        return True
        
    except Exception as e:
        logging.error(f"Error creating map: {e}", exc_info=True)
        st.error(f"Failed to create map: {e}")
        return False

# Main app function
def main():
    # App title and description
    st.title("Geographic Data Visualization")
    st.write("This application visualizes geographic data on an interactive map.")
    
    # Initialize session state variables if they don't exist
    if 'map_height' not in st.session_state:
        st.session_state.map_height = 600
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_data()
        variable_labels = load_data_dictionary()
    
    if data is None:
        st.error("Failed to load data. Please check the logs for more information.")
        return
    
    # Sidebar controls
    st.sidebar.header("Map Controls")
    
    # Get numeric columns
    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # Color variable selection
    color_column = st.sidebar.selectbox(
        "Select variable to display:", 
        options=numeric_columns,
        index=0 if numeric_columns else None
    )
    
    if not color_column:
        st.warning("No numeric columns found in the data.")
        return
    
    # Map style selection
    map_style = st.sidebar.selectbox(
        "Map style:",
        options=["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner"],
        index=1
    )
    
    # Color scale selection
    color_scale = st.sidebar.selectbox(
        "Color scale:",
        options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Greens", "Reds", "YlOrRd"],
        index=0
    )
    
    # Map opacity
    opacity = st.sidebar.slider("Map opacity:", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
    
    # Map zoom
    zoom = st.sidebar.slider("Map zoom:", min_value=5.0, max_value=12.0, value=7.0, step=0.5)
    
    # Map height
    st.session_state.map_height = st.sidebar.slider("Map height (px):", min_value=400, max_value=1000, value=st.session_state.map_height, step=50)
    
    # Region selection (if 'mun' column exists)
    selected_regions = None
    if 'mun' in data.columns:
        all_regions = sorted(data['mun'].unique().tolist())
        selected_regions = st.sidebar.multiselect("Highlight regions:", options=all_regions)
    
    # Calculate midpoint for color scale
    midpoint = None
    if color_column in data.columns:
        midpoint = (data[color_column].max() + data[color_column].min()) / 2
    
    # Create map
    st.subheader(f"Map of {variable_labels.get(color_column, color_column)}")
    create_map(
        data=data,
        variable_labels=variable_labels,
        color_column=color_column,
        numeric_columns=numeric_columns,
        selected_regions=selected_regions,
        color_scale=color_scale,
        map_style=map_style,
        zoom=zoom,
        opacity=opacity,
        midpoint=midpoint
    )
    
    # Display data table
    with st.expander("View Data Table"):
        st.dataframe(data)

# Run the app
if __name__ == "__main__":
    main()