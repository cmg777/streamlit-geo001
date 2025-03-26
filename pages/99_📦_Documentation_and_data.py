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

# --- Project Information ---
def show_project_info():
    st.header("About the Project")
    
    with st.expander("🌐 Context and Motivation", expanded=True):
        st.markdown("""
        Adopted in 2015, the **2030 Agenda for Sustainable Development** established 17 Sustainable Development Goals. 
        While global metrics offer useful benchmarks, they often overlook subnational disparities—particularly in 
        heterogeneous countries like Bolivia. The **Municipal Sustainable Development Index (IMDS)** summarizes municipal performance using 62 indicators 
        across 15 Sustainable Development Goals. Systematic and reliable information on goals 12 and 14 are not 
        available at municipal level.
        
        - 📥 Data availability from official or trusted sources
        - 🌐 Full municipal coverage (339 municipalities)
        - 🕒 Data mostly from 2012–2019

        """)
    

    
    with st.expander("📚 Data Sources and Credits"):
        st.markdown("""
        - Primary data source: [Municipal Atlas of the SDGs in Bolivia 2020.](https://sdsnbolivia.org/Atlas/) 
        - Additional indicators for multiple years were sourced from the [GeoQuery project.](https://www.aiddata.org/geoquery) 
        - Administrative boundaries from the [GeoBoundaries database](https://www.geoboundaries.org/)                                                            
        - Streamlit web app and computational notebook by [Carlos Mendez.](https://carlos-mendez.org)
        - Erick Gonzales and Pedro Leoni also collaborated in the organization of the data and the creation of the initial geospatial database.
         
        **Citation**:  
        Mendez, C. (2025, March 24). *Regional Development Indicators of Bolivia: A Dashboard for Exploratory Analysis* (Version 0.0.2) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.15074864
        """)
    

    with st.expander("🔗 Access Links"):
        st.markdown("""
        - **Original website**: [atlas.sdsnbolivia.org](http://atlas.sdsnbolivia.org)  
        - **Original Publication**: [sdsnbolivia.org/Atlas](http://www.sdsnbolivia.org/Atlas)  
        - **Source Code of the Web App**: [github.com/cmg777/streamlit-geo001](https://github.com/cmg777/streamlit-geo001)  
        - **Computational Notebook**: [Google Colab](https://colab.research.google.com/drive/1JHf8wPxSxBdKKhXaKQZUzhEpVznKGiep?usp=sharing)
        """)
    
    with st.expander("🗃️ Indicators by Sustainable Development Goal"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🧱 Goal 1: No Poverty
            - Energy poverty rate
            - Multidimensional Poverty Index
            - Unmet Basic Needs
            - Access to basic services
            
            ### 🌾 Goal 2: Zero Hunger
            - Chronic malnutrition in children
            - Obesity prevalence
            - Agricultural unit size
            - Tractor density
            
            ### 🏥 Goal 3: Good Health
            - Infant and under-five mortality
            - Institutional birth coverage
            - Disease incidence rates
            - Adolescent fertility rate
            
            ### 📚 Goal 4: Quality Education
            - School dropout rates
            - Adult literacy rate
            - Higher education attainment
            - Qualified teachers
            
            ### ⚖️ Goal 5: Gender Equality
            - Gender parity in education
            - Labor participation parity
            - Poverty gender disparities
            
            ### 💧 Goal 6: Clean Water
            - Access to potable water
            - Access to sanitation
            - Wastewater treatment
            
            ### ⚡ Goal 7: Clean Energy
            - Electricity coverage
            - Per capita electricity use
            - Clean cooking energy
            """)
            
        with col2:
            st.markdown("""
            ### 💼 Goal 8: Decent Work
            - Informality proxies
            - Labor force participation
            - Youth NEET rate
            
            ### 🏗️ Goal 9: Infrastructure
            - Internet access
            - Mobile signal coverage
            - Urban infrastructure
            
            ### ⚖️ Goal 10: Reduced Inequality
            - Municipal inequality measures
            
            ### 🏘️ Goal 11: Sustainable Cities
            - Urban housing adequacy
            - Access to transportation
            
            ### 🌍 Goal 13: Climate Action
            - Disaster resilience
            - CO₂ emissions
            - Forest degradation
            
            ### 🌳 Goal 15: Life on Land
            - Deforestation rates
            - Biodiversity loss indicators
            
            ### 🕊️ Goal 16: Peace & Justice
            - Birth registration
            - Crime and homicide rates
            - Corruption perceptions
            
            ### 🤝 Goal 17: Partnerships
            - Municipal fiscal capacity
            - Public investment per capita
            """)

# --- Main App ---
st.title("Documentation and Data")

# Project introduction
st.markdown("""
## Regional Development Indicators of Bolivia: A Dashboard for Exploratory Analysis

This project provides comprehensive data on sustainable development indicators at the municipal level in Bolivia. 
The dataset integrates 62 indicators across 15 Sustainable Development Goals for all 339 Bolivian municipalities, 
enabling detailed spatial analysis of development patterns and disparities.

The Municipal Sustainable Development Index (IMDS) reveals significant intra-national inequalities in Bolivia, 
with development levels varying dramatically between municipalities despite national-level progress. This dashboard 
allows researchers, policymakers, and citizens to explore these patterns through interactive visualizations and 
download the underlying data for further analysis.
""")

st.markdown("This page provides information about the project and allows you to download the municipal datasets in various formats.")

# Show project information
show_project_info()

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
    
    
    # Display data samples
    with st.expander("Preview Municipal Data"):
        st.dataframe(gdf_csv.head(10))
    
    with st.expander("Preview Data Definitions"):
        st.dataframe(definitions)

except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}")