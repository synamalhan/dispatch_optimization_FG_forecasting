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
supply_route_map ={
    'AR': 1, 
    'NR': 7,
    'N': 4, 
    'FN': 3, 
    'NR+SR': 8, 
    'TMCP(TMC+ACC)': 15,
    'N AND SR': 5, 
    'Q&T': 11, 
    'Q/Q&T': 12 , 
    'Q': 10, 
    'N&T': 6, 
    'ONLINE NORMALIZING': 9,
    'ASTM A-578 L-B': 2, 
    'THERMO MECHANICAL ROLLE': 13,
    'TMCP': 14
    
}

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
    supplyRouteOptions = list(supply_route_map.keys())
    supplyRoute = st.selectbox("Supply Route:", supplyRouteOptions)

# Create a new grid of 4 columns
col1, col2 = st.columns(2)

# WIP Date
with col1:
    wipDate = st.date_input("Start Date:")

# Internal Grade
with col2:
    internalGradeOptions = list(internal_grade_map.keys())
    internalGrade = st.selectbox("Internal Grade:", internalGradeOptions)

# Predict Button
if st.button("Predict"):
    # Create future dataframe
    future_df = pd.DataFrame({
        'QUANTITY': [quantity],
        'THICKNESS': [thickness],
        'LENGTH': [length],
        'WIDTH': [width],
        'SUPPLY_IND': [supply_route_map[supplyRoute]]
    })

    # Load data from SQL Server database
    server = 'SYNA'
    database = 'DISPATCH_DATA'
    username = 'testuser'
    password = 'User123'

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    cursor = cnxn.cursor()

    query = f"""
        SELECT 
            QUANTITY, THICKNESS, LENGTH, WIDTH, LAST_BIN_IND, WIP_ENTRY, FG_ENTRY, TOTAL_TIME, SUPPLY_IND
        FROM 
            FINAL
        WHERE
        GRADE_IND = {internal_grade_map[internalGrade]} AND TOTAL_TIME<10.28
    """

    cursor.execute(query)
    data = cursor.fetchall()

    data_values = [list(row) for row in data]
    df = pd.DataFrame(data_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH', 'WIDTH', 'LAST_BIN_IND', 'WIP_ENTRY', 'FG_ENTRY', 'TOTAL_TIME', 'SUPPLY_IND'])

    # Convert PRD and FG columns to datetime format
    df['WIP_ENTRY'] = pd.to_datetime(df['WIP_ENTRY'])
    df['FG_ENTRY'] = pd.to_datetime(df['FG_ENTRY'])

    # Calculate days between PRD and FG
    df['days'] = (df['FG_ENTRY'] - df['WIP_ENTRY']).dt.days

    # Create a new column 'y' for values
    df.rename(columns={'days': 'y'}, inplace=True)

    # Create additional regressor columns
    dummies = pd.get_dummies(df['SUPPLY_IND'])
    if dummies.shape[1] > 0:
        df['SUPPLY_IND'] = dummies.iloc[:, 0]
    else:
        # handle the case where there's only one unique value in df['SUPPLY_IND']
        df['SUPPLY_IND'] = 0  # or some other default value

    actual_timings = df['TOTAL_TIME'].tolist()

    # Drop unnecessary columns
    df.drop(['FG_ENTRY', 'TOTAL_TIME', 'WIP_ENTRY', 'LAST_BIN_IND'], axis=1, inplace=True)

    # Split data into training and testing sets
    X = df.drop('y', axis=1)
    y = df['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train an XGBoost model
    xgb_model = xgb.XGBRegressor()
    xgb_model.fit(X_train, y_train)

    # Make predictions on the future dataframe
    future_pred = xgb_model.predict(future_df)

    # Calculate predicted FG date
    predicted_fg_date = wipDate + pd.Timedelta(days=future_pred[0])

    # Output result
    st.write(f"The predicted FG date is: **{predicted_fg_date}**\nThe production is predicted to take **{future_pred[0]:.2f}** days")
    st.success("Prediction successful!")