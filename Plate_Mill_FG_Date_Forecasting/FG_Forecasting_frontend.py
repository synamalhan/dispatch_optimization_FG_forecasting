from datetime import date, timedelta
import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import os

# -----------------------------Home----------------------------------
def home():
    with st.expander("About this Application"):
        st.caption("""Welcome to the :red[Plate Mill FG Prediction Project]! This platform is designed to enhance the plate production process by providing insights and ideal dates for FG (Finished Goods) completion. By accurately predicting these dates, you can plan and allocate resources more effectively, ensuring smoother operations and better productivity.
                   \n\nPlate production involves several steps, including raw material processing, rolling, heat treatment, and finishing. Each of these steps must be meticulously managed to meet quality standards and deadlines. Our project leverages advanced machine learning techniques to predict FG completion dates, helping you stay ahead of potential delays and optimize your workflow.""")

    cl1, cl2 = st.columns([1,3])
    
    cl1.image(os.path.join(os.path.dirname(__file__), "../assets/plate_mill.png"), caption ="Jindal Steel & Power has the first plate mill in India, which manufactures 3m wide plates.")
    if cl2.button("Predict FG Date", use_container_width=True, type='primary'):
        st.switch_page("pages/predict.py")
    
    cl2.write("")

    if cl2.button("Predict Multiple FG Dates", use_container_width=True, type='primary'):
        st.switch_page("pages/multi_predict.py")

    cl2.write("")

    if cl2.button("Add New Data", use_container_width=True, type='primary'):
        st.switch_page("pages/train.py")

    

# -----------------------------Single Prediction Page------------------------------------
# Page setup and configuration for Predict Page
def page_configuration():
    
    # Function to convert image to base64
    def image_to_base64(image):

        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    # Set the page configuration for Streamlit app
    st.set_page_config(
        page_title="Plate FG Date Forecasting",
        page_icon=os.path.join(os.path.dirname(__file__), "../assets/jindal-flag.png"),
        layout="wide"
    )

    # Load the background image
    image = Image.open(os.path.join(os.path.dirname(__file__), "../assets/image.jpg"))

    # Add a background image with lower opacity to the Streamlit app
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: url(data:image/jpeg;base64,{image_to_base64(image)});
        background-size: cover;
        font-size: 15px; /* increase font size */
    }}
    </style>
    ''', unsafe_allow_html=True)

def headers():
    col1, col2, col3 = st.columns([3, 6, 1])
    with col1:
        st.image(os.path.join(os.path.dirname(__file__), "../assets/logo_white.svg"), width=150)
    with col2:
        st.title("Plate Mill FG Date Forecasting")
    st.write("")
    st.write("")

    
#----------------------------Predict FG Date Page---------------------------------------------------------------

# Page layout for Predict page
def page_layout_single(internal_grade_map, supply_condition_map):

    
    cl1, cl2, cl3 = st.columns([3,4,1])

    cl1.page_link("pages/home.py", label="Home", icon=":material/home:")

    cl2.page_link("pages/multi_predict.py", label="Predict FG Date for Multiple Orders", icon=":material/batch_prediction:")

    cl3.page_link("pages/train.py", label="Add New Data", icon=":material/model_training:")

    headers()


    with st.expander("Description"):
        st.caption('''
            On this page, we use the powerful XGBoost algorithm combined with key metrics to predict the approximate completion date for different grades of plates. These metrics have been carefully selected through consultations with users and data analysis to determine their importance in the production process.

By entering relevant data, you can generate predictions for when the plates will be ready for FG. This allows you to plan production schedules more effectively, allocate resources efficiently, and meet customer demands on time.
        ''')

    container = st.container(border=True)
    # Create a grid of 3 columns for user inputs
    col1, col2, col3 = st.columns(3)

    # User input for thickness
    with col1:
        thickness = st.number_input("Thickness (in mm):", value=0.0, step=0.1, format="%.1f")

    # User input for width
    with col2:
        width = st.number_input("Width (in mm):", value=0.0, step=0.1, format="%.1f")

    # User input for length
    with col3:
        length = st.number_input("Length (in m):", value=0.0, step=0.1, format="%.1f")

    # Create a new grid of 3 columns for more user inputs
    col1, col2, col3 = st.columns(3)

    # User input for quantity
    with col1:
        quantity = st.number_input("Quantity (in tonnes):", value=0.0, step=0.1, format="%.3f")

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
        buffer_cutting = st.number_input("Buffer (in tonnes):", value=0, step=1, format="%d")

    # User input for HTC buffer
    with col3:
        buffer_htc = st.number_input("HTC Buffer (in tonnes):", value=0, step=1, format="%d")


    # Optional user input for start date
    start_date = st.date_input("Start Date (Optional, default is today):", value=date.today())


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

        return True, internal_grade, supply_condition, tpip, thickness, buffer_cutting, buffer_htc, future_df, container, start_date

# Output result
def display_output_single(predicted_days, container, approximate_completion_date):
    container.subheader("Predicted Date")

    container.write("")
    container.warning(f"Predicted production duration is approximately **{predicted_days:.2f}** days")
    container.warning(f"With an estimated completion date around **{approximate_completion_date.strftime('%Y-%m-%d')}**.")
                      
                      
                


#---------------------------Multi Prediction Page-----------------------------
def page_layout_multi(internal_grade_map, supply_condition_map):
    # Set up the navigation links
    cl1, cl2, cl3 = st.columns([4, 4, 2])
    cl1.page_link("pages/home.py", label="Home", icon=":material/home:")
    cl2.page_link("pages/predict.py", label="Predict FG Date", icon=":material/online_prediction:")
    cl3.page_link("pages/train.py", label="Add New Data", icon=":material/model_training:")

    # Display headers
    headers()

    with st.expander("Description"):
        st.caption('''
            The Multi-Predict page extends the functionality of the Predict page by allowing you to make multiple predictions simultaneously. This is particularly useful when managing large batches of orders or when you need to forecast completion dates for various grades at once.

The logic used here is similar to the Predict page, ensuring consistency and reliability in the predictions. With this feature, you can quickly generate a comprehensive overview of your production timelines, helping you make informed decisions and streamline your operations.
        ''')

    result = st.container(border = True)

    
    # Initialize the data DataFrame with appropriate data types
    data_df = pd.DataFrame(
        {
            "order_num": [0],
            "thickness": [0.0],
            "width": [0.0],
            "length": [0.0],
            "quantity": [0.0],
            "int_grade": [internal_grade_map[0] if internal_grade_map else ""],
            "supply_condition": [supply_condition_map[0] if supply_condition_map else ""],
            "tpip":False,
            "buffer": [0.0],
            "htc_buffer": [0.0],
            "start_date": [date.today()]
        }
    )

    # Use st.data_editor to display and edit the DataFrame
    edited_data = st.data_editor(
        data_df,
        column_config={
            "order_num": st.column_config.NumberColumn("Order Number", default = 0),
            "thickness": st.column_config.NumberColumn("Thickness (in mm)",default = 0),
            "width": st.column_config.NumberColumn("Width (in mm)",default = 0),
            "length":st.column_config.NumberColumn( "Length (in m)",default = 0),
            "tpip":st.column_config.CheckboxColumn("Third Party Inspection",default = False),
            "quantity":st.column_config.NumberColumn( "Quantity (in tonnes)",default = 0),
            "buffer": st.column_config.NumberColumn("Buffer (in tonnes)",default = 0),
            "htc_buffer":st.column_config.NumberColumn( "HTC Buffer (in tonnes)",default = 0),
            "int_grade": st.column_config.SelectboxColumn(
                "Internal Grade",
                help="The internal grade of the plate",
                options=internal_grade_map,  # Ensure this is a list of strings
                required=True,
            ),
            "supply_condition": st.column_config.SelectboxColumn(
                "Supply Condition",
                help="The supply condition of the plate",
                options=supply_condition_map,  # Ensure this is a list of strings
                required=True,
            ),
            "start_date": st.column_config.DateColumn(
                "Start Date",
                min_value=date(2000, 1, 1),
                max_value=date(2100, 1, 1),
                format="DD.MM.YYYY",
                step=1,
                default = date.today()
            ),
        },
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("Predict"):
        return True, edited_data, result


def display_output_multi(predicted_df, container):
    predicted_df = pd.DataFrame(predicted_df)

    # Display the predicted DataFrame
    container.subheader("Predicted Days")
    container.dataframe(predicted_df, 
                     column_config ={
                         "order_num":"Order Number",
                         "PREDICTED_DAYS":"Approximate Days for completion",
                         },
                         hide_index=True, use_container_width=True)


    

# ---------------------------Train Page----------------------------------------
def page_layout_train():
    
    cl1, cl2, cl3 = st.columns([4,3,3])

    cl1.page_link("pages/home.py", label="Home", icon=":material/home:")
    cl2.page_link("pages/predict.py", label="Predict FG Date", icon=":material/online_prediction:")
    cl3.page_link("pages/multi_predict.py", label="Predict FG Date for Multiple Orders", icon=":material/batch_prediction:")

    headers()

    with st.expander("Description"):
        st.caption('''
            The Train page empowers you to continuously improve the accuracy of our prediction models by adding new and updated data. You can upload data files, which are then used to train and refine the XGBoost models.

By keeping the model updated with the latest production data, you ensure that the predictions remain accurate and relevant to current conditions. This ongoing training process allows the system to adapt to changes in the production environment, providing you with reliable and up-to-date forecasts.
        ''')

def upload_files():

    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader("Upload PM Operation File")
    
    with col2:
        file2 = st.file_uploader("Upload MasterdataGoodsMovement file")

    confirm = st.button("Add Data")

    if (file1 is not None) and (file2 is not None) and (confirm):
        return file1, file2, confirm
    else:
        return None, None, False


