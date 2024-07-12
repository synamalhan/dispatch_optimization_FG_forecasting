import streamlit as st
import pandas as pd

st.page_link("pages/home.py", label="Home", icon=":material/home:")

# Create the Streamlit frontend
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(_file_),"../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>Cost Calculator</h1>", unsafe_allow_html=True)

file_path = (os.path.join(os.path.dirname(_file_),'../database/database.csv'))  # replace with your csv file path
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

if st.button("Back"):
    st.switch_page("pages/folium_map.py")
