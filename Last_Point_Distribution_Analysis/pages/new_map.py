import folium
from sklearn.neighbors import NearestNeighbors
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import requests
import os

if 'new_Stockyard_coords' not in st.session_state:
    st.session_state.new_Stockyard_coords = None

if 'display_lines' not in st.session_state:
    st.session_state.display_lines = True

if 'cost_per_km' not in st.session_state:
    st.session_state.cost_per_km = 3.9

if 'Distance_data' not in st.session_state:
    st.session_state.Distance_data = None

if 'Distance_df' not in st.session_state:
    st.session_state.Distance_df = pd.DataFrame(columns=['Stockyard', 'Customer', 'Distance', 'Cost', 'Stockyard_coordinates'])

if 'clusters_dict' not in st.session_state:
    st.session_state.clusters_dict = {}

# Read the CSV file
data = pd.read_csv(os.path.join(os.path.dirname(__file__),'../database/database.csv'))

# Extract Stockyards and Customers from the CSV file
Stockyards = data[['Stockyard', 'Stockyard_coordinates']].drop_duplicates()
Customers = data[['Customer', 'Customer_coordinates']]

# Convert coordinates from string to tuple of floats
Stockyards['Stockyard_coordinates'] = Stockyards['Stockyard_coordinates'].apply(lambda x: tuple(map(float, x.split(','))))
Customers['Customer_coordinates'] = Customers['Customer_coordinates'].apply(lambda x: tuple(map(float, x.split(','))))


col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>New Stockyard Analysis</h1>", unsafe_allow_html=True)
    

# Create a Folium map object
m = folium.Map(location=[20, 77], zoom_start=4)  # Change map background
folium.TileLayer('OpenStreetMap').add_to(m)

# Convert Stockyards and Customers data to numpy arrays
Stockyards_array = np.array(Stockyards['Stockyard_coordinates'].tolist())
Customers_array = np.array(Customers['Customer_coordinates'].tolist())

# Apply KNN algorithm to find the nearest Stockyard for each Customer
def clusters(Stockyards_array, Customers_array):
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(Stockyards_array)
    Distances, indices = knn.kneighbors(Customers_array)
    return Distances, indices

Distances, indices = clusters(Stockyards_array, Customers_array)

# Create clusters of Customers around each Stockyard
def draw_markers(indices, Stockyards, Customers, color, display_lines):
    clusters = {}
    for i, index in enumerate(indices):
        Stockyard_name = Stockyards.iloc[index[0]]['Stockyard']
        if Stockyard_name not in clusters:
            clusters[Stockyard_name] = []
        clusters[Stockyard_name].append(Customers.iloc[i]['Customer'])

    # Define a color palette for the clusters
    color_palette = ["green", "orange", "purple", "#D227AF", "brown", "yellow"]

    # Add markers for each Stockyard and its corresponding Customers
    for i, (Stockyard_name, Customer_list) in enumerate(clusters.items()):
        Stockyard_coords = Stockyards[Stockyards['Stockyard'] == Stockyard_name]['Stockyard_coordinates'].values[0]
        folium.CircleMarker(location=Stockyard_coords, radius=7, color='red', fill=True,
                            tooltip=Stockyard_name,  # Add hover-over text
                            popup=folium.Popup(f'<b>{Stockyard_name}</b>', max_width=200)  # Customize pop-up window
                            ).add_to(m)
        for Customer in Customer_list:
            Customer_coords = Customers[Customers['Customer'] == Customer]['Customer_coordinates'].values[0]
            folium.CircleMarker(location=Customer_coords, radius=5, color="blue", fill=True,
                                tooltip=Customer,  # Add hover-over text
                                popup=folium.Popup(f'<b>{Customer}</b>', max_width=200)  # Customize pop-up window
                                ).add_to(m)
            if display_lines:
                # Add a line connecting the Customer to the Stockyard
                folium.PolyLine([Stockyard_coords, Customer_coords], color=color, weight=1).add_to(m)

# Sidebar elements
st.sidebar.page_link("pages/home.py", label="Home", icon=":material/home:")
st.sidebar.title("New Stockyard Data")
st.session_state.display_lines = st.sidebar.checkbox("Display Cluster Lines", value=st.session_state.display_lines)
cost_per_km = st.sidebar.number_input("Cost per Km", value=st.session_state.cost_per_km)
st.session_state.cost_per_km = cost_per_km

# Draw initial markers
draw_markers(indices, Stockyards, Customers, "red", st.session_state.display_lines)

# Add new marker if it exists in session state
if st.session_state.new_Stockyard_coords:
    folium.Marker(location=st.session_state.new_Stockyard_coords, popup="New Marker").add_to(m)

col1, col2, col3 = st.columns([1, 1, 1])
# Create a Streamlit text input for user input
with col1:
    new_Stockyard_name = st.text_input("Enter Name of new location:")
with col2:
    lat = st.text_input("Enter Latitude:")
with col3:
    lon = st.text_input("Enter Longitude:")

colw1, colw2 = st.columns(2)

# Add a button to add the marker
if colw1.button("Add Marker"):
    try:
        lat = float(lat)
        lon = float(lon)
        st.session_state.new_Stockyard_coords = (lat, lon)  # Store new Stockyard coordinates in session state
        new_Stockyard = pd.DataFrame([[new_Stockyard_name, (lat, lon)]], columns=Stockyards.columns)
        Stockyards = pd.concat([Stockyards, new_Stockyard], ignore_index=True)

        Stockyards_array = np.array(Stockyards['Stockyard_coordinates'].tolist())
        Distances, indices = clusters(Stockyards_array, Customers_array)
        draw_markers(indices, Stockyards, Customers, "green", st.session_state.display_lines)

        # Extract clusters and print them in a table format
        clusters_dict = {}
        for i, index in enumerate(indices):
            Stockyard_name = Stockyards.iloc[index[0]]['Stockyard']
            if Stockyard_name not in clusters_dict:
                clusters_dict[Stockyard_name] = []
            clusters_dict[Stockyard_name].append(Customers.iloc[i]['Customer'])

        # Store clusters_dict in session state
        st.session_state.clusters_dict = clusters_dict

    except ValueError:
        st.error("Please enter valid latitude and longitude values separated by a comma.")

# Add a "New Trial" button to reset everything
if colw2.button("New Trial"):
    st.session_state.new_Stockyard_coords = None
    st.session_state.display_lines = True
    st.session_state.cost_per_km = 3.9
    st.session_state.Distance_data = None
    st.session_state.Distance_df = pd.DataFrame(columns=['Stockyard', 'Customer', 'Distance', 'Cost', 'Stockyard_coordinates'])
    st.session_state.clusters_dict = {}
    new_Stockyard_name = ""
    lat = ""
    lon = ""
    st.experimental_rerun()

# Display the Folium map
folium_static(m)

# Display the "Find Road Distance" button only if a new Stockyard is added
if st.session_state.new_Stockyard_coords and 'clusters_dict' in st.session_state:
    if st.sidebar.button("Find Road Distance"):
        new_Stockyard_coords = st.session_state.new_Stockyard_coords
        Distance_data = []

        for Customer in st.session_state.clusters_dict.get(new_Stockyard_name, []):
            Customer_coords = Customers[Customers['Customer'] == Customer]['Customer_coordinates'].values[0]
            url = f"http://router.project-osrm.org/route/v1/driving/{new_Stockyard_coords[1]},{new_Stockyard_coords[0]};{Customer_coords[1]},{Customer_coords[0]}?overview=false"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'routes' in data and len(data['routes']) > 0:
                    Distance = data['routes'][0]['distance'] / 1000  # Convert to kilometers
                    cost = Distance * st.session_state.cost_per_km
                    Distance_data.append((new_Stockyard_name.upper(), Customer, Distance, cost, f"{new_Stockyard_coords[0]}, {new_Stockyard_coords[1]}"))
                else:
                    st.error(f"Could not find route for Customer {Customer}")
            else:
                st.error(f"OSRM request failed for Customer {Customer} with status code {response.status_code}")

        if Distance_data:
            Distance_df = pd.DataFrame(Distance_data, columns=['Stockyard', 'Customer', 'Distance', 'Cost', 'Stockyard_coordinates'])
            st.session_state.Distance_df = Distance_df

# Display clusters and Distances if available in session state
if 'Distance_df' in st.session_state:
    st.sidebar.dataframe(st.session_state.Distance_df.drop(columns=['Stockyard_coordinates']), hide_index=True, use_container_width=True)

# Add a "Cost Comparison" button in the sidebar
if st.sidebar.button("Cost Comparison"):
    st.switch_page("pages/new_cost_analysis.py")
