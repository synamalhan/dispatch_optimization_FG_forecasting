import streamlit as st
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pyodbc

# Set page config
st.set_page_config(
    page_title="Plate FG Forecasting",
    page_icon="D:/JSPL/Dispatch_FG/Code/FG/jindal-flag.png",
    layout="wide"
)

col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image("D:/JSPL/Dispatch_FG/Code/FG/lightadmin-custom-logo.png", width=150)
with col2:
    st.markdown("<h1 style='text-align: center'>Plate FG Forecasting</h1>", unsafe_allow_html=True)

st.write("")
st.write("")
# Create a grid of 4 columns
col1, col2 = st.columns(2)

internal_grade_map = {
    "JAMA45TM01": 385,
    "JA35XPNR02N": 262,
    "JA35XLNR01": 240,
    "JA35STTM01C": 226,
    "JA25STTMN02": 80,
    "JA35XPNR01": 249
}
supply_route_map =[
    'AR', 
    'NR',
    'TMCP',

    'N', 
    'NR+SR', 
    'Q&T', 
    'Q', 
    'N&T'
 
    
]

# Slab ID
with col1:
    slabID = st.text_input("Slab ID:", value="", max_chars=8)

# Length
with col2:
    length = st.number_input("Length:", value=0.0, step=0.1, format="%.1f")

# Create a new grid of 4 columns
col1, col2 = st.columns(2)

# Width
with col1:
    width = st.number_input("Width:", value=0.0, step=0.1, format="%.1f")

# Thickness
with col2:
    thickness = st.number_input("Thickness:", value=0.0, step=0.1, format="%.1f")

# Create a new grid of 4 columns
col1, col2 = st.columns(2)

# Quantity
with col1:
    quantity = st.number_input("Quantity:", value=0.0, step=0.1, format="%.3f")

# Supply Route
with col2:
    supplyRoute = st.selectbox("Supply Route:", supply_route_map)

# Create a new grid of 4 columns
col1, col2 = st.columns(2)

# WIP Date
with col1:
    wipDate = st.date_input("Start Date:")

# Internal Grade
with col2:
    internalGradeOptions = list(internal_grade_map.keys())
    internalGrade = st.selectbox("Internal Grade:", internalGradeOptions)

# Create a new grid of 4 columns
col1, col2 = st.columns(2)

# Buffer
with col1:
    buffer_date = st.number_input("Buffer:", value=0, step=1, format="%d")

# Third Party Inspection
with col2:
    tpip = st.checkbox('Third Party Inspection')

# Predict Button
if st.button("Predict"):
    # Create future dataframe
    future_df = pd.DataFrame({
        'QUANTITY': [quantity],
        'THICKNESS': [thickness],
        'LENGTH': [length],
        'WIDTH': [width],
        'SUPPLY_IND': [supplyRoute]
    })

    predicted_days = 0

    if tpip:
        predicted_days+=7
    
    if thickness <32:
        predicted_days += ((quantity+buffer_date)/2000)
    else:
        predicted_days += ((quantity+buffer_date)/1400)
    
    # predicted_days +=(quantity/buffer_date)

    if( supplyRoute not in ['AR', 'NR', 'TMCP']):
        predicted_days += ((quantity+buffer_date)/350)
    
    predicted_fg_date = wipDate + pd.Timedelta(days=predicted_days)
    # Output result
    st.write(f"The predicted FG date is: **{predicted_fg_date}**\nThe production is predicted to take **{predicted_days:.2f}** days")
    st.success("Prediction successful!")