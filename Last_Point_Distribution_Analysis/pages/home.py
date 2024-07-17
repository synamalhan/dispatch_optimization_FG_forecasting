import streamlit as st
import os


# """
# Create the Streamlit app for Last Point Distribution Analysis
# """

col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=120)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>Last Point Distribution Analysis</h1>", unsafe_allow_html=True)

cl1, cl2, cl3 = st.columns([1,5,1])

cl2.write("")
with cl2.expander("About the project"):
    st.write("""The :blue[Last Point Distribution Analysis] project is designed to enhance logistics and distribution efficiency. It allows users to visualize current stockyards and customers on an interactive map, providing a clear overview of the existing distribution network. By utilizing distance and cost metrics, the tool helps determine which stockyard would best serve each customer, ensuring optimal resource allocation.

In addition to visualizing the network, users can calculate the actual road distance and cost between any two locations. This feature is particularly useful for making precise logistical decisions. The tool also offers the ability to add new stockyards, enabling users to explore whether these additions could serve customers more effectively.

Moreover, the project includes a comprehensive cost analysis component. By comparing the original costs with the new costs after adding potential stockyards, users can evaluate the financial impact of their decisions. This analysis empowers users to confirm or reconsider their choices, leading to improved efficiency and cost savings in their distribution process.
""")

cl2.write("")

if cl2.button("New Stockyard Analysis", use_container_width =True, type ='primary'):
    st.switch_page("pages/new_map.py")

if cl2.button("Existing Stockyard Analysis",  use_container_width =True, type ='primary'):
    st.switch_page("pages/exist_map.py")

