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
        m = leafmap.Map()
        m.split_map(
            left_layer="NASAGIBS.ViirsEarthAtNight2012",
            right_layer="ESA WorldCover 2020",
            left_label="2012",
            right_label="2020",
            label_position="bottom",
            center=[52.5, 7.5],
            zoom=4,
        )
        m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
m.to_streamlit(height=700)
