import pandas as pd
import geopandas as gpd
import numpy as np
import math
import folium
from sqlalchemy import create_engine
import pyodbc
import matplotlib.pyplot as plt

# Load data
df_hubs = pd.read_csv('D:/JSPL/Dispatch_FG/Data/hub_locations.csv')
engine = create_engine('mssql+pyodbc://testuser:User123@SYNA/DISPATCH_DATA?driver=ODBC+Driver+17+for+SQL+Server')
with engine.connect() as conn:
    df = pd.read_sql(
        sql="SELECT CITY, LAT, LON FROM PLATE_TABLE",
        con=conn.connection
    )

# Create a GeoDataFrame for hubs
gdf_hubs = gpd.GeoDataFrame(df_hubs, geometry=gpd.points_from_xy(df_hubs.Lon, df_hubs.Lat))

# Create a GeoDataFrame for customers
gdf_customers = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LON, df.LAT))

# Define Angul location
angul_lat, angul_lon = 20.8444, 85.1511

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance

# Calculate distance from Angul to each customer
gdf_customers['distance_from_angul'] = gdf_customers.apply(lambda row: haversine(angul_lat, angul_lon, row.geometry.y, row.geometry.x), axis=1)

# Create a new column to store the cluster ID
gdf_customers['cluster_id'] = None

# Iterate over customers
for index, row in gdf_customers.iterrows():
    # If customer is within 300 km of Angul, assign cluster ID as 0 (Angul cluster)
    if row['distance_from_angul'] <= 300:
        gdf_customers.loc[index, 'cluster_id'] = 0
    else:
        # Calculate distance from customer to each hub
        distances_to_hubs = gdf_hubs.apply(lambda hub_row: haversine(row.geometry.y, row.geometry.x, hub_row.geometry.y, hub_row.geometry.x), axis=1)
        # Find the hub with the minimum distance
        min_distance_hub = distances_to_hubs.idxmin()
        # Assign the cluster ID to the customer
        gdf_customers.loc[index, 'cluster_id'] = min_distance_hub + 1

# Create a Folium map
m = folium.Map(location=[20, 77], zoom_start=4)

# Add Angul location as a marker
folium.Marker(location=[angul_lat, angul_lon], popup='Angul').add_to(m)

# Add hubs as markers
for index, row in gdf_hubs.iterrows():
    folium.CircleMarker(location=[row.geometry.y, row.geometry.x], fill=True, color='blue', radius=5).add_to(m)

# Add lines connecting hubs to Angul in red
for index, row in gdf_hubs.iterrows():
    folium.PolyLine([[angul_lat, angul_lon], [row.geometry.y, row.geometry.x]], color='grey', weight=0.5).add_to(m)

# Add lines connecting standalone points to Angul in red
for index, row in gdf_customers.iterrows():
    if row['cluster_id'] == 0:
        folium.PolyLine([[angul_lat, angul_lon], [row.geometry.y, row.geometry.x]], color='red', weight=2).add_to(m)

# Add lines connecting hubs to their corresponding customers in green
for index, row in gdf_customers.iterrows():
    if row['cluster_id'] > 0:
        hub_row = gdf_hubs.loc[row['cluster_id'] - 1]
        folium.PolyLine([[hub_row.geometry.y, hub_row.geometry.x], [row.geometry.y, row.geometry.x]], color='green', weight=2).add_to(m)

# Add customers as CircleMarkers with different colors for each cluster
cluster_colors = plt.cm.tab20(np.linspace(0, 1, len(gdf_hubs) + 1))
cluster_colors = [ '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255)) for r, g, b, _ in cluster_colors ]
for index, row in gdf_customers.iterrows():
    if row['cluster_id'] == 0:
        color = cluster_colors[0]  # Angul cluster
    else:
        color = cluster_colors[row['cluster_id']]
    folium.CircleMarker(location=[row.geometry.y, row.geometry.x], radius=2, color=color, fill=True).add_to(m)

# Add a legend to the map
# Add a legend to the map
legend_html = """
    <div style="position: absolute; top: 10px; right: 10px; z-index: 1000;">
        <h4>Legend</h4>
        <ul>
            <li><span style="color: blue;">&#9679;</span> Angul</li>
            <li><span style="color: blue;">&#9679;</span> Hubs</li>
            <li><span style="color: green;">&#9679;</span> Close Customers (within 300 km of Angul)</li>
            <li><span style="color: red;">&#9472;</span> Lines connecting hubs to Angul or customers</li>
            <li><span style="color: green;">&#9472;</span> Lines connecting hubs to their corresponding customers</li>
        </ul>
    </div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map to an HTML file
m.save('plate_map.html')