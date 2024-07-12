import streamlit as st


col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image((os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=120)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>HOME</h1>", unsafe_allow_html=True)

st.title("")



if st.button("New Hub Analysis", use_container_width =True, type ='primary'):
    st.switch_page("pages/page1.py")

st.write("")

if st.button("Existing Hub Analysis",  use_container_width =True, type ='primary'):
    st.switch_page("pages/folium_map.py")
