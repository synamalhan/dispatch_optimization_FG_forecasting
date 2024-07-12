import streamlit as st
import pandas as pd
import os

# Load the new hub distance data from session state
new_hub_distance_df = st.session_state.get('distance_df', pd.DataFrame())

# Load the old hub data from 'new_final.csv'
old_hub_data = pd.read_csv(os.path.join(os.path.dirname(__file__),'../database/database.csv'))

# Default cost value
default_cost_per_km = 3.9

st.page_link("pages/home.py", label="Home", icon=":material/home:")

col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>New Hub Cost Analysis</h1>", unsafe_allow_html=True)

cost_per_km = st.number_input("Cost per Km", value=st.session_state.cost_per_km or default_cost_per_km)

# Update cost in new hub distance data
if not new_hub_distance_df.empty:
    new_hub_distance_df['Cost'] = new_hub_distance_df['Distance (km)'] * cost_per_km

# Filter old hub data to include only customers present in new hub data
filtered_old_hub_data = old_hub_data[old_hub_data['customer'].isin(new_hub_distance_df['Customer'].tolist())]

# Update cost in filtered old hub data
filtered_old_hub_data['Cost'] = filtered_old_hub_data['distance'] * cost_per_km

# Display the tables
col1, col2 = st.columns(2)

with col1:
    st.header("New Hub")
    if not new_hub_distance_df.empty:
        st.dataframe(new_hub_distance_df.drop(columns=['Hub Coordinates']), hide_index=True)
    else:
        st.write("No data available for the new hub.")

with col2:
    st.header("Old Hub")
    st.dataframe(filtered_old_hub_data[['hub', 'customer', 'distance', 'Cost']], hide_index=True)

if not new_hub_distance_df.empty and not filtered_old_hub_data.empty:
    cost_difference = filtered_old_hub_data['Cost'].sum() - new_hub_distance_df['Cost'].sum()
    distance_difference = filtered_old_hub_data['distance'].sum() - new_hub_distance_df['Distance (km)'].sum()

    with st.container(height=100, border=True):
        st.markdown(f"<div style='text-align: center;'><p style='color: white; display: inline-block; margin-right: 20px; '>Difference in Cost:</p>"
                f"<p style='color: {'green' if cost_difference >= 0 else 'red'}; display: inline-block; background-color: lightgreen;'> ₹{cost_difference:.2f}</p></div>",
                unsafe_allow_html=True)

        st.markdown(f"<div style='text-align: center;'><p style='color: white; display: inline-block; margin-right: 20px; '>Difference in Distance:</p>"
                    f"<p style='color: {'green' if distance_difference >= 0 else 'red'}; display: inline-block; background-color: lightgreen;'> {distance_difference:.2f} km</p></div>",
                    unsafe_allow_html=True)

    

else:
    st.write("Unable to calculate differences as data is incomplete.")

col1, col2 = st.columns(2)

if col1.button("Back"):
    st.switch_page("pages/page1.py")

if col2.button("Add New Hub"):
    # Ensure new_hub_distance_df is not empty
    if not new_hub_distance_df.empty:
        # Ensure old_hub_data has the customer_coordinates column
        if 'customer_coordinates' not in old_hub_data.columns:
            st.error("The 'customer_coordinates' column is missing in the old hub data.")
        else:
            archive_entries = []

            for i, row in new_hub_distance_df.iterrows():
                new_hub_name = row['Hub']
                customer_name = row['Customer']
                new_hub_coords = row['Hub Coordinates']
                distance = row['Distance (km)']

                # Filter old hub data for the specific customer
                filtered_old_hub_data = old_hub_data[old_hub_data['customer'] == customer_name]

                if not filtered_old_hub_data.empty:
                    existing_customer_row = filtered_old_hub_data.iloc[0]

                    # Archive the old entry
                    archive_entries.append(existing_customer_row)

                    # Delete old entry with the same customer name
                    old_hub_data = old_hub_data[old_hub_data['customer'] != customer_name]

                    # Create the new entry as a DataFrame
                    new_entry = pd.DataFrame([{
                        'hub': new_hub_name,
                        'state': "state",  # Make sure this is updated to the correct value or derived from somewhere
                        'customer': customer_name,
                        'distance': distance,
                        'hub_coordinates': new_hub_coords,
                        'customer_coordinates': existing_customer_row['customer_coordinates']
                    }])

                    # Add the new entry
                    old_hub_data = pd.concat([old_hub_data, new_entry], ignore_index=True)
                    
                else:
                    st.warning(f"No matching customer found in the old hub data for customer: {customer_name}")

            # Save archived entries to CSV
            if archive_entries:
                archive_df = pd.DataFrame(archive_entries)
                archive_df.to_csv(os.path.join(os.path.dirname(__file__),'../database/archive.csv'), mode='a', header=False, index=False)

            # Save updated data back to CSV
            old_hub_data.to_csv(os.path.join(os.path.dirname(__file__),'../database/database.csv'), index=False)

            st.write("Changes committed successfully.")
    else:
        st.warning("Please add a new hub and calculate distances before committing changes.")
