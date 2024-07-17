"""
Streamlit App for Last Point Distribution Analysis

This app provides a user-friendly interface for analyzing last point distributions in stockyards.
It allows users to create a new stockyard analysis or load an existing one.

Example:
    To run the app, save this code to a file (e.g. `app.py`) and run it with `streamlit run app.py`.
    Then, open a web browser and navigate to `http://localhost:8501` to access the app.

"""
import base64
from io import BytesIO
import streamlit as st
from PIL import Image
import os

def image_to_base64(image):
    """
    Convert a PIL Image object to a base64-encoded string.

    Args:
        image (PIL.Image): The image to convert.

    Returns:
        str: The base64-encoded string representation of the image.

    Example:
        >>> image = Image.open('assets/bg_jspl.jpg')
        >>> img_str = image_to_base64(image)
        >>> print(img_str)  # Output: a base64-encoded string
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def set_streamlit_app_config(page_title, page_icon, background_image):
    """
    Set the configuration for a Streamlit app.

    Args:
        page_title (str): The title of the page.
        page_icon (str): The path to the page icon image.
        background_image (PIL.Image): The background image for the app.

    Example:
        >>> set_streamlit_app_config("Stockyard Analysis", "assets/jindal-flag.png", Image.open('assets/bg_jspl.jpg'))
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide"
    )

    # Add a background image with lower opacity to the Streamlit app
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: url(data:image/jpeg;base64,{image_to_base64(background_image)});
        background-size: cover
    }}
    </style>
    ''', unsafe_allow_html=True)

def create_streamlit_app(pages, position="hidden"):
    """
    Create a Streamlit app with a navigation menu.

    Args:
        pages (list): A list of Streamlit pages.
        position (str, optional): The position of the navigation menu. Defaults to "hidden".

    Returns:
        StreamlitApp: The created Streamlit app.

    Example:
        >>> pages = [st.Page("pages/home.py"), st.Page("pages/new_map.py"), ...]
        >>> app = create_streamlit_app(pages)
        >>> app.run()
    """
    pg = st.navigation(pages, position=position)
    return pg

# Load the background image
background_image = Image.open('assets/bg_jspl.jpg')

# Set the page configuration for Streamlit app
set_streamlit_app_config("Last Point Distribution Analysis", "assets/jindal-flag.png", background_image)

# Create the Streamlit app
pages = [st.Page("pages/home.py"), st.Page("pages/new_map.py"), st.Page("pages/new_cost_analysis.py"), st.Page("pages/exist_cost_calc.py"), st.Page("pages/exist_map.py")]
app = create_streamlit_app(pages, position="hidden")

# Run the Streamlit app
app.run()
