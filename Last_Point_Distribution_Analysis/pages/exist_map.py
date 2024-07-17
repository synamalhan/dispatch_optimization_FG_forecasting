import folium
from sklearn.neighbors import NearestNeighbors
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import os

@st.cache_data
def load_data(file):
    """
    Load data from a CSV file.

    Args:
        file (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data.

    Example:
        >>> data = load_data('database.csv')
    """
    return pd.read_csv(file)

st.page_link("pages/home.py", label="Home", icon=":material/home:")

col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(os.path.join(os.path.dirname(__file__),"../assets/logo_white.svg"), width=150)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 36px'>Existing Stockyard Analysis</h1>", unsafe_allow_html=True)

# Load the Stockyard and Customer data from the CSV file
file_path = os.path.join(os.path.dirname(__file__),'../database/database.csv')
data = load_data(file_path)

# Extract unique Stockyards with their coordinates
Stockyards_data = data[['Stockyard', 'Stockyard_coordinates']].drop_duplicates()
Stockyards = [(row['Stockyard'], tuple(map(float, row['Stockyard_coordinates'].strip('()').split(',')))) for _, row in Stockyards_data.iterrows()]

# Extract Customers with their coordinates
Customers = [(row['Customer'], tuple(map(float, row['Customer_coordinates'].strip('()').split(',')))) for _, row in data.iterrows()]

# Create a Folium map object
m = folium.Map(location=[20, 77], zoom_start=4)
folium.TileLayer('OpenStreetMap').add_to(m)

# Convert Stockyards and Customers data to numpy arrays
Stockyards_array = np.array([Stockyard[1] for Stockyard in Stockyards])
Customers_array = np.array([Customer[1] for Customer in Customers])

def clusters(Stockyards_array, Customers_array):
    """
    Apply KNN algorithm to find the nearest Stockyard for each Customer.

    Args:
        Stockyards_array (np.ndarray): Array of Stockyard coordinates.
        Customers_array (np.ndarray): Array of Customer coordinates.

    Returns:
        Distances (np.ndarray): Array of distances between Customers and their nearest Stockyards.
        indices (np.ndarray): Array of indices of the nearest Stockyards for each Customer.

    Example:
        >>> Distances, indices = clusters(Stockyards_array, Customers_array)
    """
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(Stockyards_array)
    Distances, indices = knn.kneighbors(Customers_array)
    return Distances, indices

Distances, indices = clusters(Stockyards_array, Customers_array)

def draw_markers(indices, Stockyards, Customers, color):
    """
    Create clusters of Customers around each Stockyard and add markers to the map.

    Args:
        indices (np.ndarray): Array of indices of the nearest Stockyards for each Customer.
        Stockyards (list): List of Stockyard names and coordinates.
        Customers (list): List of Customer names and coordinates.
        color (str): Color of the markers.

    Example:
        >>> draw_markers(indices, Stockyards, Customers, "red")
    """
    clusters = {}
    for i, index in enumerate(indices):
        Stockyard_name = Stockyards[index[0]][0]
        if Stockyard_name not in clusters:
            clusters[Stockyard_name] = []
        clusters[Stockyard_name].append(Customers[i])

    # Add markers for each Stockyard and its corresponding Customers
    for Stockyard_name, Customers in clusters.items():
        Stockyard_coords = [Stockyard[1] for Stockyard in Stockyards if Stockyard[0] == Stockyard_name][0]
        folium.CircleMarker(location=Stockyard_coords, radius=5, color='red', fill=True,
                            tooltip=Stockyard_name,  # Add hover-over text
                            popup=folium.Popup(f'<b>{Stockyard_name}</b>', max_width=200)  # Customize pop-up window
                            ).add_to(m)
        for Customer in Customers:
            city, lat_lon = Customer[0], Customer[1]
            folium.CircleMarker(location=lat_lon, radius=2, color='blue', fill=True,
                                tooltip=city,  # Add hover-over text
                                popup=folium.Popup(f'<b>{city}</b>', max_width=200)  # Customize pop-up window
                                ).add_to(m)
            # Add a line connecting the Customer to the Stockyard
            folium.PolyLine([Stockyard_coords, lat_lon], color=color, weight=1).add_to(m)

draw_markers(indices, Stockyards, Customers, "red")


# Create a dictionary for all clusters between Stockyards and Customers
clusters = {}
for i, index in enumerate(indices):
    Stockyard_name = Stockyards[index[0]][0]
    if Stockyard_name not in clusters:
        clusters[Stockyard_name] = []
    clusters[Stockyard_name].append(Customers[i][0])

cluster_df = pd.DataFrame([(Stockyard, ', '.join(Customers)) for Stockyard, Customers in clusters.items()], columns=['Stockyard', 'Customers'])

st.dataframe(cluster_df, hide_index=True, use_container_width=True)

# Checkbox to view map
view_map = st.checkbox("Display Map")
if view_map:
    folium_static(m, width=1000)


# Go forward to Cost Calculator for existing Stockyards and Customers
if st.button("Cost Calculator"):
    st.switch_page("pages/exist_cost_calc.py")