import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from geodatasets import get_path
from sqlalchemy import create_engine
import shapefile as shp
from shapely.geometry import Point


engine = create_engine('mssql+pyodbc://testuser:User123@SYNA/DISPATCH_DATA?driver=ODBC+Driver+17+for+SQL+Server')

# Load data from SQL Server into a pandas DataFrame
with engine.connect() as conn:
    df = pd.read_sql(
        sql="SELECT LAT, LON, VOLUME FROM REBAR_TABLE",
        con=conn.connection
    )

fig, ax = plt.subplots(figsize=(8,6)) 

fp = r'india-polygon.shp'
map_df = gpd.read_file(fp) 
map_df_copy = gpd.read_file(fp)
map_df.head()
map_df.plot(ax=ax, color='white', edgecolor='grey')

# Set the color and size of the points based on the VOLUME column
sc = ax.scatter(df['LON'], df['LAT'], c=df['VOLUME'], cmap='plasma', s=df['VOLUME']/10)
# add grid
ax.grid(alpha=0.5)

# Add a colorbar
cbar = plt.colorbar(sc)
cbar.set_label('Volume')

plt.title(f"PLate")
plt.show()