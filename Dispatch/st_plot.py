import streamlit as st
import pandas as pd
import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sqlalchemy import create_engine

# Load data
df_hubs = pd.read_csv('D:/JSPL/Dispatch_FG/Data/hub_locations.csv')
engine = create_engine('mssql+pyodbc://testuser:User123@SYNA/DISPATCH_DATA?driver=ODBC+Driver+17+for+SQL+Server')
with engine.connect() as conn:
    df = pd.read_sql(
        sql="SELECT LAT, LON FROM PLATE_TABLE",
        con=conn.connection
    )

# Create a GeoDataFrame for hubs
gdf_hubs = gpd.GeoDataFrame(df_hubs, geometry=gpd.points_from_xy(df_hubs.Lon, df_hubs.Lat))

# Create a GeoDataFrame for customers
gdf_customers = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LON, df.LAT))

# Create a KNN model with k=1 (i.e., each customer is assigned to its nearest hub)
knn = NearestNeighbors(n_neighbors=1)
hub_coords = np.column_stack((gdf_hubs.geometry.x.values, gdf_hubs.geometry.y.values)).tolist()
knn.fit(hub_coords)

# Predict the nearest hub for each customer
customer_coords = np.column_stack((gdf_customers.geometry.x.values, gdf_customers.geometry.y.values)).tolist()
distances, indices = knn.kneighbors(customer_coords)

# Convert NumPy arrays to lists
distances = distances.tolist()
indices = indices.tolist()

# Create a new column to store the hub ID
gdf_customers['hub_id'] = indices

# Create a Streamlit app
st.title("Plate Map")
st.write("Select a location to add a new hub:")

gdf_hubs.rename(columns={'Lat': 'lat', 'Lon': 'lon'}, inplace=True)
gdf_customers.rename(columns={'Lat': 'lat', 'Lon': 'lon'}, inplace=True)

# Remove rows with null values in 'lat' or 'lon' columns
gdf_hubs.dropna(subset=['lat', 'lon'], inplace=True)
gdf_customers.dropna(subset=['lat', 'lon'], inplace=True)

# Create a combined GeoDataFrame
gdf_combined = pd.concat([gdf_hubs, gdf_customers], ignore_index=True)

# Add a column to distinguish between hubs and customers
gdf_combined['type'] = ['hub'] * len(gdf_hubs) + ['customer'] * len(gdf_customers)

# Create a map
st.title("Plate Map")
st.write("Map of hubs and customers:")

# Create a map with different colors for hubs and customers
st.map(gdf_combined, zoom=10, use_container_width=True)