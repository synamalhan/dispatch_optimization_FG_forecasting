import folium
from sklearn.neighbors import NearestNeighbors
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import requests

if 'new_hub_coords' not in st.session_state:
    st.session_state.new_hub_coords = None

if 'display_lines' not in st.session_state:
    st.session_state.display_lines = True

if 'cost_per_km' not in st.session_state:
    st.session_state.cost_per_km = 3.9

if 'distance_data' not in st.session_state:
    st.session_state.distance_data = None

if 'distance_df' not in st.session_state:
    st.session_state.distance_df = pd.DataFrame(columns=['Hub', 'Customer', 'Distance (km)', 'Cost', 'Hub Coordinates'])

if 'clusters_dict' not in st.session_state:
    st.session_state.clusters_dict = {}

# Read the CSV file
data = pd.read_csv(os.path.join(os.path.dirname(__file__),'../database/database.csv'))

# Extract hubs and customers from the CSV file
hubs = data[['hub', 'hub_coordinates']].drop_duplicates()
customers = data[['customer', 'customer_coordinates']]

# Convert coordinates from string to tuple of floats
hubs['hub_coordinates'] = hubs['hub_coordinates'].apply(lambda x: tuple(map(float, x.split(','))))
customers['customer_coordinates'] = customers['customer_coordinates'].apply(lambda x: tuple(map(float, x.split(','))))


col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>New Hub Analysis</h1>", unsafe_allow_html=True)
    

# Create a Folium map object
m = folium.Map(location=[20, 77], zoom_start=4)  # Change map background
folium.TileLayer('OpenStreetMap').add_to(m)

# Convert hubs and customers data to numpy arrays
hubs_array = np.array(hubs['hub_coordinates'].tolist())
customers_array = np.array(customers['customer_coordinates'].tolist())

# Apply KNN algorithm to find the nearest hub for each customer
def clusters(hubs_array, customers_array):
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(hubs_array)
    distances, indices = knn.kneighbors(customers_array)
    return distances, indices

distances, indices = clusters(hubs_array, customers_array)

# Create clusters of customers around each hub
def draw_markers(indices, hubs, customers, color, display_lines):
    clusters = {}
    for i, index in enumerate(indices):
        hub_name = hubs.iloc[index[0]]['hub']
        if hub_name not in clusters:
            clusters[hub_name] = []
        clusters[hub_name].append(customers.iloc[i]['customer'])

    # Define a color palette for the clusters
    color_palette = ["green", "orange", "purple", "#D227AF", "brown", "yellow"]

    # Add markers for each hub and its corresponding customers
    for i, (hub_name, customer_list) in enumerate(clusters.items()):
        hub_coords = hubs[hubs['hub'] == hub_name]['hub_coordinates'].values[0]
        folium.CircleMarker(location=hub_coords, radius=7, color='red', fill=True,
                            tooltip=hub_name,  # Add hover-over text
                            popup=folium.Popup(f'<b>{hub_name}</b>', max_width=200)  # Customize pop-up window
                            ).add_to(m)
        for customer in customer_list:
            customer_coords = customers[customers['customer'] == customer]['customer_coordinates'].values[0]
            folium.CircleMarker(location=customer_coords, radius=5, color="blue", fill=True,
                                tooltip=customer,  # Add hover-over text
                                popup=folium.Popup(f'<b>{customer}</b>', max_width=200)  # Customize pop-up window
                                ).add_to(m)
            if display_lines:
                # Add a line connecting the customer to the hub
                folium.PolyLine([hub_coords, customer_coords], color=color, weight=1).add_to(m)

# Sidebar elements
st.sidebar.page_link("pages/home.py", label="Home", icon=":material/home:")
st.sidebar.title("New Hub Data")
st.session_state.display_lines = st.sidebar.checkbox("Display Cluster Lines", value=st.session_state.display_lines)
cost_per_km = st.sidebar.number_input("Cost per Km", value=st.session_state.cost_per_km)
st.session_state.cost_per_km = cost_per_km

# Draw initial markers
draw_markers(indices, hubs, customers, "red", st.session_state.display_lines)

# Add new marker if it exists in session state
if st.session_state.new_hub_coords:
    folium.Marker(location=st.session_state.new_hub_coords, popup="New Marker").add_to(m)

col1, col2, col3 = st.columns([1, 1, 1])
# Create a Streamlit text input for user input
with col1:
    new_hub_name = st.text_input("Enter Name of new location:")
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
        st.session_state.new_hub_coords = (lat, lon)  # Store new hub coordinates in session state
        new_hub = pd.DataFrame([[new_hub_name, (lat, lon)]], columns=hubs.columns)
        hubs = pd.concat([hubs, new_hub], ignore_index=True)

        hubs_array = np.array(hubs['hub_coordinates'].tolist())
        distances, indices = clusters(hubs_array, customers_array)
        draw_markers(indices, hubs, customers, "green", st.session_state.display_lines)

        # Extract clusters and print them in a table format
        clusters_dict = {}
        for i, index in enumerate(indices):
            hub_name = hubs.iloc[index[0]]['hub']
            if hub_name not in clusters_dict:
                clusters_dict[hub_name] = []
            clusters_dict[hub_name].append(customers.iloc[i]['customer'])

        # Store clusters_dict in session state
        st.session_state.clusters_dict = clusters_dict

    except ValueError:
        st.error("Please enter valid latitude and longitude values separated by a comma.")

# Add a "New Trial" button to reset everything
if colw2.button("New Trial"):
    st.session_state.new_hub_coords = None
    st.session_state.display_lines = True
    st.session_state.cost_per_km = 3.9
    st.session_state.distance_data = None
    st.session_state.distance_df = pd.DataFrame(columns=['Hub', 'Customer', 'Distance (km)', 'Cost', 'Hub Coordinates'])
    st.session_state.clusters_dict = {}
    new_hub_name = ""
    lat = ""
    lon = ""
    st.experimental_rerun()

# Display the Folium map
folium_static(m)

# Display the "Find Road Distance" button only if a new hub is added
if st.session_state.new_hub_coords and 'clusters_dict' in st.session_state:
    if st.sidebar.button("Find Road Distance"):
        new_hub_coords = st.session_state.new_hub_coords
        distance_data = []

        for customer in st.session_state.clusters_dict.get(new_hub_name, []):
            customer_coords = customers[customers['customer'] == customer]['customer_coordinates'].values[0]
            url = f"http://router.project-osrm.org/route/v1/driving/{new_hub_coords[1]},{new_hub_coords[0]};{customer_coords[1]},{customer_coords[0]}?overview=false"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'routes' in data and len(data['routes']) > 0:
                    distance = data['routes'][0]['distance'] / 1000  # Convert to kilometers
                    cost = distance * st.session_state.cost_per_km
                    distance_data.append((new_hub_name.upper(), customer, distance, cost, f"{new_hub_coords[0]}, {new_hub_coords[1]}"))
                else:
                    st.error(f"Could not find route for customer {customer}")
            else:
                st.error(f"OSRM request failed for customer {customer} with status code {response.status_code}")

        if distance_data:
            distance_df = pd.DataFrame(distance_data, columns=['Hub', 'Customer', 'Distance (km)', 'Cost', 'Hub Coordinates'])
            st.session_state.distance_df = distance_df

# Display clusters and distances if available in session state
if 'distance_df' in st.session_state:
    st.sidebar.write(st.session_state.distance_df.drop(columns=['Hub Coordinates']))

# Add a "Cost Comparison" button in the sidebar
if st.sidebar.button("Cost Comparison"):
    st.switch_page("pages/page2.py")
