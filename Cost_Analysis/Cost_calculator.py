import streamlit as st
from streamlit_folium import folium_static
import pandas as pd

# Create the Streamlit frontend
st.title("Cost Calculator")

file_path = 'D:/JSPL/new_final.csv'  # replace with your csv file path
data = pd.read_csv(file_path)

hub_name = st.text_input("Enter the hub name")
customer_name = st.text_input("Enter the customer name")
cost_per_km = st.text_input("Enter the cost per km")

if st.button("Find Cost"):
    if hub_name and customer_name:
        filtered_data = data[(data["hub"] == hub_name) & (data["customer"] == customer_name)]
        if not filtered_data.empty:
            distance_array = (filtered_data["distance"].values)
            distance = float(distance_array[0])  # Ensure distance is a single number
            print(type(distance))
            cost = distance * float(cost_per_km)
            st.write(f"The cost endured between {hub_name} and {customer_name} is {cost}")
        else:
            st.write("Hub or customer not found in the CSV file")
    else:
        st.write("Please enter both hub name and customer name")