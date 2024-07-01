import streamlit as st
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pyodbc
import shap
from PIL import Image
import base64
from io import BytesIO

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

# Lists for internal grade and supply route options
internal_grade_map = [
    'JA35XLNR01', 'JA35STTM01C', 'JAMA45TM01', 'JA30NEXP01', 'JA35XPNR01', 'JA25STTM01',
    'JA35XPNR02N', 'JA23NEXP01', 'JA25STTMN02', 'JA35XPNR01T', 'JA35STNR01', 'JA35XLNR02',
    'JA25STTM01N', 'JA49PVFN01', 'JA35STTM01', 'JA41NRBS01N', 'JA25STTMN02C', 'JA35XLNR01T',
    'JA25STTM01C', 'JA35STTM02C', 'JA41NRBS02N', 'JASB35TM01D', 'JA49PVFN02', 'JA35IMOP01Di',
    'JA27MGTM01', 'JADMRN01Di', 'JAMA45TM01C', 'JARH40EX01C', 'JA41NRBS01', 'JA35STNR01N'
]
supply_condition_map = ['AR', 'NR', 'N', 'NRSR', 'TMCP', 'QT', 'Q', 'NT']

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
    internalGrade = st.selectbox("Internal Grade:", internal_grade_map)

# User input for buffer date
with col2:
    buffer_date = st.number_input("Buffer:", value=0, step=1, format="%d")

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

    # Determine supply route condition
    if(supply_condition in ['AR','NR','TMCP']):
        supply_route = 'NON HTC'
    else:
        supply_route = 'HTC'

    # Load data from SQL Server database
    server = 'SYNA'
    database = 'FG_DATA'
    username = 'testuser'
    password = 'User123'

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    cursor = cnxn.cursor()

    # SQL query to fetch data
    query = f"""
        SELECT 
            QUANTITY, THICKNESS, LENGTH, WIDTH, DAYS, SUPPLY_CONDITION
        FROM 
            MASTER_DATA
        WHERE
        ROLLING_DATE IS NOT NULL AND INTERNAL_GRADE = '{internalGrade}' AND ROLLING_DATE < '2024-03-01' AND DAYS<20;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    # Convert data to DataFrame
    data_values = [list(row) for row in data]
    df = pd.DataFrame(data_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH', 'WIDTH', 'DAYS', 'SUPPLY_CONDITION'])

    # Convert SUPPLY_CONDITION to categorical
    df['SUPPLY_CONDITION'] = pd.Categorical(df['SUPPLY_CONDITION'])
    # Create a new column 'y' for values
    df.rename(columns={'DAYS': 'y'}, inplace=True)

    # Split data into training and testing sets
    X = df.drop('y', axis=1)
    y = df['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train an XGBoost model
    xgb_model = xgb.XGBRegressor(enable_categorical=True)
    xgb_model.fit(X_train, y_train)

    # Make predictions on the future dataframe
    future_pred = xgb_model.predict(future_df)
    predicted_days = future_pred[0]

    # Adjust predicted days based on user inputs
    if tpip == 'Yes':
        predicted_days += 7
    
    if thickness < 32:
        predicted_days += (buffer_date / 2000)
    else:
        predicted_days += (buffer_date / 1400)

    if supply_condition not in ['AR','NR','TMCP']:
        predicted_days += (buffer_htc / 350)

    # Output result
    st.write(f"The production is predicted to take **{predicted_days:.2f}** days", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Plot actual vs predicted days
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(y_train, xgb_model.predict(X_train), color='red', s=10, alpha=0.2)
        ax.set_xlabel('Actual Days')
        ax.set_ylabel('Predicted Days')
        ax.set_title('Trend of the Model')
        st.pyplot(fig)

    # SHAP value analysis for feature importance
    with col2:
        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(X_train)

        shap_exp = shap.Explanation(values=shap_values, 
                            base_values=explainer.expected_value, 
                            data=X_train.values, 
                            feature_names=X_train.columns.tolist())
       
        # Plot SHAP beeswarm plot
        plt.figure(figsize=(10, 6))
        shap.plots.beeswarm(shap_exp, show=False)
        st.pyplot(plt)
