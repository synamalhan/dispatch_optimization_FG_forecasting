import base64
from io import BytesIO
import streamlit as st
from PIL import Image

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Set the page configuration for Streamlit app
st.set_page_config(
    page_title="Hub Analysis",
    page_icon="D:/JSPL/Dispatch_FG/Dispatch/last_point/assets/jindal-flag.png"
)

# Load the background image
image = Image.open('D:/JSPL/Dispatch_FG/Dispatch/last_point/assets/bg_jspl.jpg')

# Add a background image with lower opacity to the Streamlit app
st.markdown(f'''
<style>
.stApp {{
    background-image: url(data:image/jpeg;base64,{image_to_base64(image)});
    background-size: cover
}}
</style>
''', unsafe_allow_html=True)

pg = st.navigation([st.Page("pages/home.py"),st.Page("pages/page1.py"), st.Page("pages/page2.py"), st.Page("pages/Cost_calculator.py"), st.Page("pages/folium_map.py")],position="hidden")

pg.run()
