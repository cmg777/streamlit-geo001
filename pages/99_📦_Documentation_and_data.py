import streamlit as st
import geopandas as gpd
import pandas as pd
import io
import os

# --- Constants ---
DATA_PATH = "map_and_data.geojson"
DEFINITIONS_PATH = 'dataDefinitions.csv'
STATA_PATH = 'dataStata.dta'

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Data Download")

# --- Data Loading ---
@st.cache_data
def load_geo_data(path):
    if not os.path.exists(path):
        st.error(f"Required data file not found: {path}")
        st.stop()  # Halt execution if data isn't there
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=4326)
    return gdf

@st.cache_data
def load_definitions(path):
    if not os.path.exists(path):
        st.error(f"Required data file not found: {path}")
        st.stop()  # Halt execution if data isn't there
    return pd.read_csv(path)

# --- Main App ---
st.title("Municipal Data Download")
st.markdown("This page allows you to download the municipal datasets in various formats.")

# Load the datasets
try:
    gdf = load_geo_data(DATA_PATH)
    definitions = load_definitions(DEFINITIONS_PATH)
    
    # Section for downloading GeoJSON data
    st.header("Download Municipal Data")
    st.markdown("Choose your preferred format:")
    
    col1, col2, col3 = st.columns(3)
    
    # Prepare data for different formats
    # GeoJSON
    # Option 1: Generate on the fly
    geojson_buffer = io.BytesIO()
    gdf.to_file(geojson_buffer, driver='GeoJSON')
    geojson_data = geojson_buffer.getvalue()
    
    # CSV
    gdf_csv = gdf.drop(columns=['geometry'])
    csv_data = gdf_csv.to_csv(index=False).encode('utf-8')
    
    # Definitions CSV
    definitions_csv = definitions.to_csv(index=False).encode('utf-8')
    
    # GeoJSON download
    with col1:
        try:
            st.download_button(
                label="Download GeoJSON",
                data=geojson_data,
                file_name="municipal_data.geojson",
                mime="application/geo+json",
                help="Download the complete dataset with geographic information in GeoJSON format",
            )
        except Exception as e:
            st.warning(f"Could not create GeoJSON format: {str(e)}")
    
    # CSV download
    with col2:
        try:
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="municipal_data.csv",
                mime="text/csv",
                help="Download the dataset without geographic information in CSV format",
            )
        except Exception as e:
            st.warning(f"Could not create CSV format: {str(e)}")
    
    # Stata download from existing file
    with col3:
        try:
            # Check if Stata file exists
            if not os.path.exists(STATA_PATH):
                st.warning(f"Stata file not found: {STATA_PATH}")
            else:
                # Read the existing Stata file
                with open(STATA_PATH, 'rb') as f:
                    stata_data = f.read()
                    
                st.download_button(
                    label="Download Stata (.dta)",
                    data=stata_data,
                    file_name="municipal_data.dta",
                    mime="application/octet-stream",  # Generic MIME type for .dta files
                    help="Download the dataset in Stata format",
                )
        except Exception as e:
            st.warning(f"Could not load Stata file: {str(e)}")
    
    # Section for downloading definitions
    st.header("Download Data Definitions")
    st.markdown("The data definitions file contains descriptions of each variable in the dataset:")
    
    # Definitions CSV download
    try:
        st.download_button(
            label="Download Data Definitions (CSV)",
            data=definitions_csv,
            file_name="data_definitions.csv",
            mime="text/csv",
            help="Download the data dictionary explaining each variable in the dataset",
        )
    except Exception as e:
        st.warning(f"Could not create Data Definitions CSV: {str(e)}")
    
    # Display data info
    st.header("Dataset Information")
    
    # Info about municipal data
    with st.expander("About the Municipal Dataset"):
        num_municipalities = len(gdf)
        num_columns = len(gdf.columns) - 1  # Subtracting the geometry column
        # Get Stata file size if available
        stata_size_info = ""
        if os.path.exists(STATA_PATH):
            stata_size = os.path.getsize(STATA_PATH) / 1024  # Size in KB
            stata_size_info = f", {stata_size:.1f} KB (Stata)"
            
        st.markdown(f"""
        ### Municipal Dataset
        
        - **Number of Municipalities**: {num_municipalities}
        - **Number of Variables**: {num_columns}
        - **File Size**: Approximately {len(geojson_data)/1024:.1f} KB (GeoJSON), {len(csv_data)/1024:.1f} KB (CSV){stata_size_info}
        
        This dataset contains various indicators and metrics for municipalities, including geographic boundaries.
        """)
    
    # Info about definitions data
    with st.expander("About the Data Definitions"):
        num_definitions = len(definitions)
        st.markdown(f"""
        ### Data Definitions
        
        - **Number of Variables Defined**: {num_definitions}
        - **File Size**: Approximately {len(definitions_csv)/1024:.1f} KB
        
        This file contains descriptions of the variables found in the municipal dataset.
        """)
    
    # Display data samples
    with st.expander("Preview Municipal Data"):
        st.dataframe(gdf_csv.head(10))
    
    with st.expander("Preview Data Definitions"):
        st.dataframe(definitions)

except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}")