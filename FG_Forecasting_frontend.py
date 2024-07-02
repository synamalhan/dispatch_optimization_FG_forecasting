import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO



# Page setup and configuration
def page_configuration():

    # Function to convert image to base64
    def image_to_base64(image):

        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    # Set the page configuration for Streamlit app
    st.set_page_config(
        page_title="Plate FG Forecasting",
        page_icon="D:/JSPL/Dispatch_FG/Code/FG/jindal-flag.png",
        layout="wide"
    )

    # Load the background image
    image = Image.open('D:/JSPL/Dispatch_FG/Code/FG/image.jpg')

    # Add a background image with lower opacity to the Streamlit app
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: url(data:image/jpeg;base64,{image_to_base64(image)});
        background-size: cover;
        font-size: 28px; /* increase font size */
    }}
    </style>
    ''', unsafe_allow_html=True)



def page_layout(internal_grade_map, supply_condition_map):
    # Create columns for layout and add images/text
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image("D:/JSPL/Dispatch_FG/Code/FG/logo_white.svg", width=150)
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 36px'>Plate FG Forecasting</h1>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Create a grid of 3 columns for user inputs
    col1, col2, col3 = st.columns(3)

    # User input for thickness
    with col1:
        thickness = st.number_input("Thickness:", value=0.0, step=0.1, format="%.1f")

    # User input for width
    with col2:
        width = st.number_input("Width:", value=0.0, step=0.1, format="%.1f")

    # User input for length
    with col3:
        length = st.number_input("Length:", value=0.0, step=0.1, format="%.1f")

    # Create a new grid of 3 columns for more user inputs
    col1, col2, col3 = st.columns(3)

    # User input for quantity
    with col1:
        quantity = st.number_input("Quantity:", value=0.0, step=0.1, format="%.3f")

    # User input for third party inspection
    with col2:
        tpip = st.selectbox("Third Party Inspection:", ['Yes', 'No'])

    # User input for supply route
    with col3:
        supply_condition = st.selectbox("Supply Condition:", supply_condition_map)

    # Create another grid of 3 columns for more user inputs
    col1, col2, col3 = st.columns(3)

    # User input for internal grade
    with col1:
        internal_grade = st.selectbox("Internal Grade:", internal_grade_map)

    # User input for buffer date
    with col2:
        buffer_cutting = st.number_input("Buffer:", value=0, step=1, format="%d")

    # User input for HTC buffer
    with col3:
        buffer_htc = st.number_input("HTC Buffer:", value=0, step=1, format="%d")


    # Predict Button
    if st.button("Predict", help="Click to predict the production days"):

        # Create future dataframe for prediction
        future_df = pd.DataFrame({
            'QUANTITY': [quantity],
            'THICKNESS': [thickness],
            'LENGTH': [length],
            'WIDTH': [width],
            'SUPPLY_CONDITION': [supply_condition]
        })

        future_df['SUPPLY_CONDITION'] = pd.Categorical(future_df['SUPPLY_CONDITION'])

        return True, internal_grade, supply_condition, tpip, thickness, buffer_cutting, buffer_htc, future_df



# Output result

def display_output(predicted_days):
    st.write(f"The production is predicted to take **{predicted_days:.2f}** days", unsafe_allow_html=True)