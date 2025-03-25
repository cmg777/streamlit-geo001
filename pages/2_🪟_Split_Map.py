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

url1 = "https://github.com/quarcs-lab/datasets/releases/download/DMSP-like/Harmonized_DN_NTL_1992_calDMSP.tif"
url2 = "https://github.com/quarcs-lab/datasets/releases/download/DMSP-like/Harmonized_DN_NTL_2020_simVIIRS.tif"

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map()
        m.split_map(
            left_layer=url2, right_layer="ESA WorldCover 2020"
        )
        m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")

m.to_streamlit(height=700)
