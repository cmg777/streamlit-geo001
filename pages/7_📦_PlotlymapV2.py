import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px

# Title
st.title("Geographic Data Visualization")

# Load data
data = gpd.read_file("map_and_data.geojson")
data = data.to_crs(epsg=4326)
data["id"] = data.index.astype(str)

# Try to load labels
try:
    df = pd.read_csv('dataDefinitions.csv')
    labels = dict(zip(df['Variable'], df['Label']))
except:
    labels = {}

# Get numeric columns
num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Variable selector
selected_col = st.sidebar.selectbox(
    "Select variable:", 
    options=num_cols,
    format_func=lambda col: labels.get(col, col),
    index=num_cols.index("imds") if "imds" in num_cols else 0
)

# Map title
st.subheader(f"Map of {labels.get(selected_col, selected_col)}")

# Create map
fig = px.choropleth_mapbox(
    data_frame=data,
    geojson=data.__geo_interface__,
    locations="id",
    color=selected_col,
    hover_name="mun",
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=5
)

fig.update_layout(margin=dict(r=0,t=0,l=0,b=0), height=600)
st.plotly_chart(fig, use_container_width=True)