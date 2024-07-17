import streamlit as st
import pandas as pd
import os
from git import Repo

# Function to commit and push changes to the Git repository
# def commit_and_push_changes(csv_file_path):
#     """
#     Commits and pushes changes to the specified CSV file in the Git repository.
#     
#     Args:
#         csv_file_path (str): Path to the CSV file to commit and push.
#     """
#     repo = Repo(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#     repo.git.add(csv_file_path)
#     repo.index.commit("Updated database.csv through Streamlit app")
#     origin = repo.remote(name='origin')
#     origin.push()

# Load the new Stockyard Distance data from session state
new_Stockyard_Distance_df = st.session_state.get('Distance_df', pd.DataFrame())

# Load the old Stockyard data from 'new_final.csv'
old_Stockyard_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../database/database.csv'))

# Default cost value
default_cost_per_km = 3.9

# Set up the page link for navigation
st.page_link("pages/home.py", label="Home", icon=":material/home:")

# Layout for the title and logo
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__), "../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>New Stockyard Cost Analysis</h1>", unsafe_allow_html=True)

# Input for the cost per kilometer
cost_per_km = st.number_input("Cost per Km", value=default_cost_per_km)

# Update cost in new Stockyard Distance data
if not new_Stockyard_Distance_df.empty:
    new_Stockyard_Distance_df['Cost'] = new_Stockyard_Distance_df['Distance'] * cost_per_km

# Filter old Stockyard data to include only Customers present in new Stockyard data
filtered_old_Stockyard_data = old_Stockyard_data[old_Stockyard_data['Customer'].isin(new_Stockyard_Distance_df['Customer'].tolist())]

# Update cost in filtered old Stockyard data
filtered_old_Stockyard_data['Cost'] = filtered_old_Stockyard_data['Distance'] * cost_per_km

# Display the tables
col1, col2 = st.columns(2)

with col1:
    st.header("New Stockyard")
    if not new_Stockyard_Distance_df.empty:
        st.dataframe(new_Stockyard_Distance_df.drop(columns=['Stockyard_coordinates']), hide_index=True)
    else:
        st.write("No data available for the new Stockyard.")

with col2:
    st.header("Old Stockyard")
    st.dataframe(filtered_old_Stockyard_data[['Stockyard', 'Customer', 'Distance', 'Cost']], hide_index=True)

# Calculate and display differences in cost and distance
if not new_Stockyard_Distance_df.empty and not filtered_old_Stockyard_data.empty:
    cost_difference = filtered_old_Stockyard_data['Cost'].sum() - new_Stockyard_Distance_df['Cost'].sum()
    distance_difference = filtered_old_Stockyard_data['Distance'].sum() - new_Stockyard_Distance_df['Distance'].sum()

    with st.container(height=100, border=True):
        st.markdown(f"<div style='text-align: center;'><p style='color: white; display: inline-block; margin-right: 20px;'>Difference in Cost:</p>"
                    f"<p style='color: {'green' if cost_difference >= 0 else 'red'}; display: inline-block; background-color: lightgreen;'> ₹{cost_difference:.2f}</p></div>",
                    unsafe_allow_html=True)

        st.markdown(f"<div style='text-align: center;'><p style='color: white; display: inline-block; margin-right: 20px;'>Difference in Distance:</p>"
                    f"<p style='color: {'green' if distance_difference >= 0 else 'red'}; display: inline-block; background-color: lightgreen;'> {distance_difference:.2f} km</p></div>",
                    unsafe_allow_html=True)
else:
    st.write("Unable to calculate differences as data is incomplete.")

# Layout for the action buttons
col1, col2 = st.columns(2)

if col1.button("Back"):
    st.switch_page("pages/new_map.py")

if col2.button("Add New Stockyard"):
    """
    Adds the new Stockyard data to the existing database, archives the old data, 
    and commits the changes to the Git repository.
    """
    if not new_Stockyard_Distance_df.empty:
        if 'Customer_coordinates' not in old_Stockyard_data.columns:
            st.error("The 'Customer_coordinates' column is missing in the old Stockyard data.")
        else:
            archive_entries = []

            for i, row in new_Stockyard_Distance_df.iterrows():
                new_Stockyard_name = row['Stockyard']
                customer_name = row['Customer']
                new_Stockyard_coords = row['Stockyard_coordinates']
                distance = row['Distance']

                # Filter old Stockyard data for the specific customer
                filtered_old_Stockyard_data = old_Stockyard_data[old_Stockyard_data['Customer'] == customer_name]

                if not filtered_old_Stockyard_data.empty:
                    existing_customer_row = filtered_old_Stockyard_data.iloc[0]

                    # Archive the old entry
                    archive_entries.append(existing_customer_row)

                    # Delete old entry with the same customer name
                    old_Stockyard_data = old_Stockyard_data[old_Stockyard_data['Customer'] != customer_name]

                    # Create the new entry as a DataFrame
                    new_entry = pd.DataFrame([{
                        'Stockyard': new_Stockyard_name,
                        'state': "state",  # Make sure this is updated to the correct value or derived from somewhere
                        'Customer': customer_name,
                        'Distance': distance,
                        'Stockyard_coordinates': new_Stockyard_coords,
                        'Customer_coordinates': existing_customer_row['Customer_coordinates']
                    }])

                    # Add the new entry
                    old_Stockyard_data = pd.concat([old_Stockyard_data, new_entry], ignore_index=True)
                    
                else:
                    st.warning(f"No matching Customer found in the old Stockyard data for Customer: {customer_name}")

            # Save archived entries to CSV
            if archive_entries:
                archive_df = pd.DataFrame(archive_entries)
                archive_df.to_csv(os.path.join(os.path.dirname(__file__), '../database/archive.csv'), mode='a', header=False, index=False)
                # commit_and_push_changes(os.path.join(os.path.dirname(__file__), '../database/archive.csv'))

            # Save updated data back to CSV
            old_Stockyard_data.to_csv(os.path.join(os.path.dirname(__file__), '../database/database.csv'), index=False)
            # commit_and_push_changes(os.path.join(os.path.dirname(__file__), '../database/database.csv'))

            st.success("Changes committed successfully.")
    else:
        st.warning("Please add a new Stockyard and calculate Distances before committing changes.")
