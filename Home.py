import streamlit as st
import leafmap.foliumap as leafmap
import leafmap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
A Streamlit map template
<https://github.com/opengeos/streamlit-map-template>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

# Customize page title
st.title("Streamlit for Geospatial Applications")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and [leafmap](https://leafmap.org). It is an open-source project and you are very welcome to contribute to the [GitHub repository](https://github.com/opengeos/streamlit-map-template).
    """
)

st.header("Instructions")

markdown = """
1. For the [GitHub repository](https://github.com/opengeos/streamlit-map-template) or [use it as a template](https://github.com/opengeos/streamlit-map-template/generate) for your own project.
2. Customize the sidebar by changing the sidebar text and logo in each Python files.
3. Find your favorite emoji from https://emojipedia.org.
4. Add a new app to the `pages/` directory with an emoji in the file name, e.g., `1_🚀_Chart.py`.

"""

st.markdown(markdown)

# NASA Black Marble (VIIRS) for a given date
date = "2022-01-01"
url = (
    f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
    f"VIIRS_Black_Marble/default/{date}/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.jpg"
)
m.add_tile_layer(
    url=url,
    name="NASA Black Marble",
    attribution="NASA GIBS / VIIRS",
    opacity=1.0
)

m.to_streamlit(height=500)