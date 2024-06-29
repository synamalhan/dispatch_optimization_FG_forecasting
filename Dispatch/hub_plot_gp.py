import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import numpy as np
from geodatasets import get_path
from sqlalchemy import create_engine
import shapefile as shp
from shapely.geometry import Point

# Load data
df_hubs = pd.read_csv('D:/JSPL/Dispatch_FG/Data/hub_locations.csv')
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

# Plot the map
fig, ax = plt.subplots(figsize=(8,6)) 
fp = r'D:/JSPL/Dispatch_FG/Data/india-polygon.shp'
map_df = gpd.read_file(fp) 
map_df.plot(ax=ax, color='white', edgecolor='grey')

# Plot the hubs in black
ax.scatter(gdf_hubs.geometry.x, gdf_hubs.geometry.y, c='black', alpha=1, s=30)

# Plot the customers with different colors for each hub
hub_colors = plt.cm.tab20(np.linspace(0, 1, len(gdf_hubs)))
for hub_id, color in enumerate(hub_colors):
    customers_in_hub = gdf_customers[gdf_customers['hub_id'] == hub_id]
    ax.scatter(customers_in_hub.geometry.x, customers_in_hub.geometry.y, c=[color], alpha=0.7, s=20)

# Plot the lines connecting customers to their nearest hub
for index, row in gdf_customers.iterrows():
    hub_id = row['hub_id']
    hub_geometry = gdf_hubs.loc[hub_id].geometry
    ax.plot([row.geometry.x, hub_geometry.x], [row.geometry.y, hub_geometry.y], linewidth=1, alpha=0.5)

# Add grid and title
ax.grid(alpha=0.5)
plt.title(f"PLATE")
plt.show()

