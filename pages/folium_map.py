import folium
from sklearn.neighbors import NearestNeighbors
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import os 

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

st.page_link("pages/home.py", label="Home", icon=":material/home:")

col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>Existing Hub Analysis</h1>", unsafe_allow_html=True)

# Load the hub and customer data from the CSV file
file_path = os.path.join(os.path.dirname(__file__),'../database/database.csv')
data = load_data(file_path)

# Extract unique hubs with their coordinates
hubs_data = data[['hub', 'hub_coordinates']].drop_duplicates()
hubs = [(row['hub'], tuple(map(float, row['hub_coordinates'].strip('()').split(',')))) for _, row in hubs_data.iterrows()]

# Extract customers with their coordinates
customers = [(row['customer'], tuple(map(float, row['customer_coordinates'].strip('()').split(',')))) for _, row in data.iterrows()]

# Create a Folium map object
m = folium.Map(location=[20, 77], zoom_start=4)
folium.TileLayer('OpenStreetMap').add_to(m)

# Convert hubs and customers data to numpy arrays
hubs_array = np.array([hub[1] for hub in hubs])
customers_array = np.array([customer[1] for customer in customers])

# Apply KNN algorithm to find the nearest hub for each customer
def clusters(hubs_array, customers_array):
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(hubs_array)
    distances, indices = knn.kneighbors(customers_array)
    return distances, indices

distances, indices = clusters(hubs_array, customers_array)

# Create clusters of customers around each hub
def draw_markers(indices, hubs, customers, color):
    clusters = {}
    for i, index in enumerate(indices):
        hub_name = hubs[index[0]][0]
        if hub_name not in clusters:
            clusters[hub_name] = []
        clusters[hub_name].append(customers[i])

    # Add markers for each hub and its corresponding customers
    for hub_name, customers in clusters.items():
        hub_coords = [hub[1] for hub in hubs if hub[0] == hub_name][0]
        folium.CircleMarker(location=hub_coords, radius=5, color='red', fill=True,
                            tooltip=hub_name,  # Add hover-over text
                            popup=folium.Popup(f'<b>{hub_name}</b>', max_width=200)  # Customize pop-up window
                            ).add_to(m)
        for customer in customers:
            city, lat_lon = customer[0], customer[1]
            folium.CircleMarker(location=lat_lon, radius=2, color='blue', fill=True,
                                tooltip=city,  # Add hover-over text
                                popup=folium.Popup(f'<b>{city}</b>', max_width=200)  # Customize pop-up window
                                ).add_to(m)
            # Add a line connecting the customer to the hub
            folium.PolyLine([hub_coords, lat_lon], color=color, weight=1).add_to(m)

draw_markers(indices, hubs, customers, "red")

# Extract clusters and print them in a table format
clusters = {}
for i, index in enumerate(indices):
    hub_name = hubs[index[0]][0]
    if hub_name not in clusters:
        clusters[hub_name] = []
    clusters[hub_name].append(customers[i][0])

# Create a pandas DataFrame from the clusters
cluster_df = pd.DataFrame([(hub, ', '.join(customers)) for hub, customers in clusters.items()], columns=['Hub', 'Customers'])

# Display the clusters table
st.dataframe(cluster_df, hide_index=True)

# Display the Folium map
view_map = st.checkbox("Display Map")
if view_map:
    folium_static(m)

if st.button("Cost Calculator"):
    st.switch_page("pages/Cost_calculator.py")
