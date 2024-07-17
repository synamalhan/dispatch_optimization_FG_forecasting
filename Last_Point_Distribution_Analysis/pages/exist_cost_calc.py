import streamlit as st
import pandas as pd
import os

# Create the Streamlit frontend
st.page_link("pages/home.py", label="Home", icon=":material/home:")

col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__), "../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>Cost Calculator</h1>", unsafe_allow_html=True)

file_path = os.path.join(os.path.dirname(__file__), '../database/database.csv')  # replace with your csv file path
data = pd.read_csv(file_path)

# Get unique stockyard names for the dropdown
unique_stockyards = data["Stockyard"].unique()

st.subheader("")

cl1, cl2 = st.columns(2)
# Get user input for stockyard name and dynamically update customer dropdown
Stockyard_name = cl1.selectbox("Select the Stockyard name", options=unique_stockyards)

if Stockyard_name:
    unique_customers = data[data["Stockyard"] == Stockyard_name]["Customer"].unique()
    Customer_name = cl2.selectbox("Select the Customer name", options=unique_customers)
else:
    Customer_name = cl2.selectbox("Select the Customer name", options=[])

cost_per_km = st.text_input("Enter the cost per km", value = 3.90)

# Calculate the cost when the "Find Cost" button is clicked
if st.button("Find Cost"):
    if Stockyard_name and Customer_name:
        filtered_data = data[(data["Stockyard"] == Stockyard_name) & (data["Customer"] == Customer_name)]
        if not filtered_data.empty:
            Distance_array = filtered_data["Distance"].values
            Distance = float(Distance_array[0])  # Ensure Distance is a single number
            cost = Distance * float(cost_per_km)
            st.success(f"The distance between {Stockyard_name} and {Customer_name} is **{Distance:.2f}** and cost endured between {Stockyard_name} and {Customer_name} is **₹{cost:.2f}**")
        else:
            st.write("Stockyard or Customer not found in the CSV file")
    else:
        st.write("Please enter both Stockyard name and Customer name")

# Go back to the exist map page when the "Back" button is clicked
if st.button("Back"):
    st.switch_page("pages/exist_map.py")
