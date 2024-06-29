from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import folium
from sqlalchemy import create_engine

# Load data
df_hubs = pd.read_csv('D:/JSPL/Dispatch_FG/Code/Dispatch/hub_locations.csv')
engine = create_engine('mssql+pyodbc://testuser:User123@SYNA/DISPATCH_DATA?driver=ODBC+Driver+17+for+SQL+Server')
with engine.connect() as conn:
    df = pd.read_sql(
        sql="SELECT LAT, LON, VOLUME FROM PLATE_TABLE",
        con=conn.connection
    )

# Create a GeoDataFrame for hubs
gdf_hubs = gpd.GeoDataFrame(df_hubs, geometry=gpd.points_from_xy(df_hubs.Lon, df_hubs.Lat))

# Create a GeoDataFrame for customers
gdf_customers = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LON, df.LAT))

# Create a KNN model with k=1 (i.e., each customer is assigned to its nearest hub)
knn = NearestNeighbors(n_neighbors=1)
hub_coords = np.column_stack((gdf_hubs.geometry.x.values, gdf_hubs.geometry.y.values))
knn.fit(hub_coords)

# Predict the nearest hub for each customer
customer_coords = np.column_stack((gdf_customers.geometry.x.values, gdf_customers.geometry.y.values))
distances, indices = knn.kneighbors(customer_coords)

# Create a new column to store the hub ID
gdf_customers['hub_id'] = indices.flatten()

# Create a Folium map
m = folium.Map(location=[20, 77], zoom_start=4)  # India's coordinates

# Add hubs as markers
for i, row in gdf_hubs.iterrows():
    folium.Marker([row.geometry.y, row.geometry.x], popup=f"Hub {i}").add_to(m)

# Add customers as markers with different colors for each hub
hub_colors = plt.cm.tab20(np.linspace(0, 1, len(gdf_hubs)))
for hub_id, color in enumerate(hub_colors):
    customers_in_hub = gdf_customers[gdf_customers['hub_id'] == hub_id]
    for index, row in customers_in_hub.iterrows():
        folium.Marker([row.geometry.y, row.geometry.x], popup=f"Customer {index}", icon=folium.Icon(color=color)).add_to(m)

# Add lines connecting customers to their nearest hub
for index, row in gdf_customers.iterrows():
    hub_id = row['hub_id']
    hub_geometry = gdf_hubs.loc[hub_id].geometry
    folium.PolyLine([[row.geometry.y, row.geometry.x], [hub_geometry.y, hub_geometry.x]]).add_to(m)

# Save the map as an HTML file
m.save('plate_map.html')