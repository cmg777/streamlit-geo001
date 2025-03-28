import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os

# --- Constants ---
DATA_PATH = "map_and_data.geojson"
DEFINITIONS_PATH = 'dataDefinitions.csv'
# Default indicators
INDICATOR1 = 'imds'                 # Default y-axis variable
INDICATOR3 = 'ln_t400NTLpc2012'     # Default x-axis variable
INDICATOR4 = 'rank_imds'            # Additional indicator for hover
ADM1 = 'dep'                        # Department (Administrative level 1)
ADM3 = 'mun'                        # Municipality (Administrative level 3)

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
default_x_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == INDICATOR3.lower()), 0)
default_y_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == INDICATOR1.lower()), 0)
default_hover_idx = next((i for i, (col, _) in enumerate(var_options) if col.lower() == INDICATOR4.lower()), 0)

# Sidebar Selectors
st.sidebar.header("Scatter Plot Configuration")
selected_x_idx = st.sidebar.selectbox(
    "Select X-axis variable:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_x_idx
)
selected_x_col, selected_x_label = var_options[selected_x_idx]

selected_y_idx = st.sidebar.selectbox(
    "Select Y-axis variable:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_y_idx
)
selected_y_col, selected_y_label = var_options[selected_y_idx]

selected_hover_idx = st.sidebar.selectbox(
    "Select additional hover data:",
    options=range(len(var_options)),
    format_func=lambda i: var_options[i][1],  # Display labels
    index=default_hover_idx
)
selected_hover_col, selected_hover_label = var_options[selected_hover_idx]

# Trendline options
trendline_options = ['None', 'OLS', 'Lowess']
selected_trendline = st.sidebar.selectbox(
    "Select trendline type:",
    options=trendline_options,
    index=1  # Default to OLS
)

# Trendline scope options
trendline_scope_options = ['Overall', 'Per Department']
selected_scope = st.sidebar.selectbox(
    "Select trendline scope:",
    options=trendline_scope_options,
    index=0  # Default to Overall
)

# Map the trendline option to the appropriate value for px.scatter
trendline_map = {
    'None': None,
    'OLS': 'ols',
    'Lowess': 'lowess'
}
trendline = trendline_map[selected_trendline]

# Map the scope option
trendline_scope = 'overall' if selected_scope == 'Overall' else 'trace'

# Verify that required columns exist
required_cols = [ADM1, ADM3, selected_x_col, selected_y_col, selected_hover_col]
missing_cols = [col for col in required_cols if col not in data.columns]

if missing_cols:
    st.error(f"Required column(s) not found: {', '.join(missing_cols)}")
    st.stop()

# --- Create Scatter Plot ---
st.subheader(f"{selected_y_label} vs {selected_x_label}")

# Create a dictionary for custom labels
data_dict = {
    selected_x_col: selected_x_label,
    selected_y_col: selected_y_label,
    selected_hover_col: selected_hover_label,
    ADM1: labels.get(ADM1, "Department"),
    ADM3: labels.get(ADM3, "Municipality")
}

fig = px.scatter(
    data,
    x=selected_x_col,                # Data for x-axis
    y=selected_y_col,                # Data for y-axis
    color=ADM1,                      # Color coding by department
    symbol=ADM1,                     # Symbol coding by department
    hover_name=ADM3,                 # Municipality for hover tooltip
    trendline=trendline,             # Adding trendline (OLS by default)
    trendline_scope=trendline_scope, # Scope of the trendline (overall or per department)
    trendline_color_override="red" if trendline_scope == "overall" else None,  # Override color for overall trendline
    hover_data=[selected_hover_col], # Additional data for hover tooltip
    labels=data_dict                 # Custom labels
)

# Update layout
fig.update_layout(
    height=600,
    margin={"r": 0, "t": 30, "l": 0, "b": 0},
    legend_title=labels.get(ADM1, "Department")
)

st.plotly_chart(fig, use_container_width=True)

# Explanation
st.sidebar.info(f"""
Scatter Plot Configuration:
- X-axis: {selected_x_label}
- Y-axis: {selected_y_label}
- Additional hover data: {selected_hover_label}
- Trendline: {selected_trendline}
- Trendline scope: {selected_scope}
""")

# Add description of the visualization
st.markdown(f"""
### About This Visualization

This scatter plot shows the relationship between {selected_x_label} and {selected_y_label} for each municipality:

- **Position**: X-axis shows {selected_x_label}, Y-axis shows {selected_y_label}
- **Color and Symbol**: Different departments are represented by unique colors and symbols
- **Trendline**: {selected_trendline if selected_trendline != 'None' else 'No'} regression line {'for each department' if selected_scope == 'Per Department' else 'showing the overall relationship'}
- **Hover**: Shows municipality name and {selected_hover_label}

This visualization helps identify patterns, correlations, and potential outliers in the data.
""")

# Calculate and display regression statistics for OLS trendline
if trendline == 'ols':
    try:
        # Import here to avoid issues if package is not available
        import numpy as np
        from scipy import stats
        import pandas as pd
        
        if trendline_scope == 'overall':
            # Overall regression statistics
            valid_data = data[[selected_x_col, selected_y_col]].dropna()
            
            if len(valid_data) > 2:  # Need at least 3 points for meaningful regression
                x = valid_data[selected_x_col].values
                y = valid_data[selected_y_col].values
                
                # Calculate linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                # Display overall statistics
                st.markdown(f"""
                ### Overall Regression Statistics
                
                - **R-squared**: {r_value**2:.4f}
                - **P-value**: {p_value:.4f}
                - **Formula**: {selected_y_label} = {slope:.4f} × {selected_x_label} + {intercept:.4f}
                """)
        else:
            # Per-department regression statistics
            st.markdown("### Regression Statistics by Department")
            
            # Create a container for the statistics
            stat_cols = st.columns(3)
            
            # Get unique departments
            departments = data[ADM1].unique()
            
            # Calculate and display statistics for each department
            stats_data = []
            
            for dept in departments:
                dept_data = data[data[ADM1] == dept][[ADM1, selected_x_col, selected_y_col]].dropna()
                
                if len(dept_data) > 2:  # Need at least 3 points for meaningful regression
                    x = dept_data[selected_x_col].values
                    y = dept_data[selected_y_col].values
                    
                    # Calculate linear regression
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    
                    # Store the statistics
                    stats_data.append({
                        'Department': dept,
                        'R-squared': r_value**2,
                        'P-value': p_value,
                        'Slope': slope,
                        'Intercept': intercept
                    })
            
            if stats_data:
                # Convert to DataFrame for display
                stats_df = pd.DataFrame(stats_data)
                
                # Sort by R-squared for better overview
                stats_df = stats_df.sort_values('R-squared', ascending=False)
                
                # Display as a table
                st.dataframe(
                    stats_df.style.format({
                        'R-squared': '{:.4f}',
                        'P-value': '{:.4f}',
                        'Slope': '{:.4f}',
                        'Intercept': '{:.4f}'
                    }),
                    use_container_width=True
                )
            else:
                st.info("Insufficient data to calculate per-department statistics.")
    except Exception as e:
        st.warning(f"Could not calculate regression statistics. Error: {str(e)}")