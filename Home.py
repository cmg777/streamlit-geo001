import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# Sidebar configuration
st.sidebar.title("About")
st.sidebar.info(
    """
    A Streamlit map template  
    [GitHub Repository](https://github.com/opengeos/streamlit-map-template)
    """
)
st.sidebar.image("https://i.imgur.com/UbOXYAU.png")

# Main page title and description
st.title("Streamlit for Geospatial Applications")
st.markdown(
    """
    This multipage app template showcases interactive web apps built with [Streamlit](https://streamlit.io) and [leafmap](https://leafmap.org).  
    Contributions are welcome on the [GitHub repository](https://github.com/opengeos/streamlit-map-template).
    """
)

# Instructions with bullet points
st.header("Instructions")
st.markdown(
    """
    - 🚀 **Template Usage:** Use the [GitHub repository](https://github.com/opengeos/streamlit-map-template) or generate your own template [here](https://github.com/opengeos/streamlit-map-template/generate).  
    - 🎨 **Customize Sidebar:** Edit the sidebar text and logo in the Python files.  
    - 🔍 **Find Emojis:** Visit [Emojipedia](https://emojipedia.org) for more options.  
    - 📂 **Add New Apps:** Place new apps in the `pages/` directory with an emoji in the filename, e.g., `1_🚀_Chart.py`.  
    - 🔗 **Additional Resources:** Explore the [GitHub repository](https://github.com/cmg777/streamlit-geo001/) and the [Streamlit app](https://quarcs-geo001.streamlit.app/).
    """
)

# Interactive map with minimap control
m = leafmap.Map(minimap_control=True)
m.add_basemap("NASAGIBS.ViirsEarthAtNight2012")
m.to_streamlit(height=500)
