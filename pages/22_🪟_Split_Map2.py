import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

markdown = """
A Streamlit map template
<https://github.com/opengeos/streamlit-map-template>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

st.title("Split-panel Map")

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map(center=[47.653149, -117.59825], zoom=3)
        m.add_basemap("NASAGIBS.ViirsEarthAtNight2012")
        image1 = "https://github.com/quarcs-lab/datasets/releases/download/DMSP-like/Harmonized_DN_NTL_2014_simVIIRS.tif"
        image2 = "https://github.com/quarcs-lab/datasets/releases/download/DMSP-like/Harmonized_DN_NTL_2021_simVIIRS.tif"
        m.split_map(
            image1,
            image2,
            left_label="NTL in 2014",
            right_label="NTL in 2021"
        )
        m
m.to_streamlit(height=700)
