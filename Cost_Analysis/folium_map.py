import folium
import pyodbc
from sklearn.neighbors import NearestNeighbors
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Define the database connection parameters
server = 'SYNA'
database = 'DISPATCH_DATA'
username = 'testuser'
password = 'User123'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

customers_query = "SELECT city, lat, lon FROM plate_table"
customers_data = cursor.execute(customers_query).fetchall()

# hubs = pd.read_csv('D:/Python/hub_locations.csv')
hubs = [
    ("BH (Bharuch), Gujarat", (21.7051, 72.9959)),
    ("BNHT (BANNIHATI) Bellary, Karnataka", (15.1394, 76.9214)),
    ("BRGT (BHERAGHAT), Jabalpur, MP", (23.1276, 79.7957)),
    ("BVH (BALLABGARH) Faridabad, Haryana", (28.3510, 77.3180)),
    ("CAR (CHUNAR), Mirzapur, UP", (25.1270, 82.8839)),
    ("CCMH-PFT CONCOR(Raipur)", (21.2514, 81.6296)),
    ("CDG (Chandigarh)", (30.7333, 76.7794)),
    ("CGMV (PFT- VARNAMA ), Vadora, Gujarat", (22.3080, 73.1914)),
    ("CGPT (PFT-TIHI (M.P.), Mhow, Indore, MP", (22.5536, 75.8210)),
    ("CJ (Kanchipuram), TN", (12.8342, 79.7036)),
    ("CCJS (PFT CONCOR) Visakhapatnam, AP", (17.6868, 83.2185)),
    ("CMCN (PFT-NAGALAPALLE), Medak, AP", (17.6122, 78.1543)),
    ("CMLK (Concor Green Field Neermana) Ateli, HR", (27.8891, 76.2830)),
    ("CTCS(Concor Terminal-Shalimar) Kolkata WB", (22.5565, 88.3191)),
    ("DDL(Dandri Kalan)Ludhiana,Punjab", (30.9005, 75.8573)),
    ("DKAE (DANKUNI), Kolkata, WB", (22.6646, 88.3073)),
    ("DPMT (Hyderabad), Telengana", (17.3850, 78.4867)),
    ("ICDD(Dadri), Delhi NCR", (28.5324, 77.5531)),
    ("ICDK(ICD kanapura), Jaipur, Rajasthan", (26.9124, 75.7873)),
    ("ICDP(Inland container depot Dapper) Chandigarh, Punjab", (30.7333, 76.7794)),
    ("ICDW (Bengaluru) Karnataka", (12.9716, 77.5946)),
    ("IGCS(Irugur), Tamil Nadu", (11.0183, 77.0128)),
    ("GSPR (Gosalpur), Jabalpur, MP", (23.2822, 80.0038)),
    ("GZB (Ghaziabad), UP", (28.6692, 77.4538)),
    ("JAB (Yamuna Bridge), Agra, UP", (27.1767, 78.0081)),
    ("GFPA(M/s. Punjab Logistics Infrastructure Ltd., Ahmedgarh), Punjab", (30.6952, 75.9731)),
    ("KAV (Kalamna), Nagpur, MH", (21.1466, 79.0888)),
    ("KKF (KANKARIA), Ahemedabad, Gujarat", (23.0225, 72.5714)),
    ("KKU (Kanakpura ), Jaipur, Rajasthan", (26.9124, 75.7873)),
    ("KRIR (KHARI ROAD) Ahemdebad, Gujarat", (23.0225, 72.5714)),
    ("KOKG (Korukkupet), TN", (13.1015, 80.2852)),
    ("KSV (KOSI KALAN), Mathura, UP", (27.7940, 77.4387)),
    ("KTIG(TISCO SDG KALAMBOLI ,Mumbai), Maharashtra", (19.0319, 73.0771)),
    ("LMNR(Laxmi Nagar) Indore.MP", (22.7196, 75.8577)),
    ("MBL (Manubolu,) Andhra", (14.1946, 79.8936)),
    ("NK (NASIK ROAD), MH", (19.9975, 73.7898)),
    ("NGC (New Guwahati Goods Shed), Assam", (26.1445, 91.7362)),
    ("PCWD (DP WORLD, PANIPAT), HR", (29.3901, 76.9635)),
    ("PIDN (NAMLI), Ratlam, MP", (23.3340, 75.0366)),
    ("PLMD (Pilamedu), Coimbatore, TN", (11.0183, 76.9725)),
    ("PLIN (PFT- Nalgonda), Telengana", (17.0544, 79.2684)),
    ("PRI -Pathri(MALU ELECTRODES -HARIDWAR)", (29.8585, 78.5460)),
    ("PNKD (Panki Dham), Kanpur, UP", (26.4499, 80.3319)),
    ("RSD (RAIPUR), CG", (21.2514, 81.6296)),
    ("SGBB (Bhilai Marshalling Yard) Bhilai, CG", (21.1938, 81.3509)),
    ("SGTY (Sankrail Goods), Kolkata, WB", (22.5646, 88.3012)),
    ("SNF (Sanathnagar, Hyderabad)", (17.4369, 78.4480)),
    ("SGWF (Whitefield Satellite Goods Terminal) Bangalore, Karnataka", (12.9698, 77.7499)),
    ("STD (Satrod), Hissar, HR", (29.1518, 75.7220)),
    ("SUW(Sukhisewaniyan), Bhopal, MP", (23.2844, 77.3438)),
    ("TPGY (TIRUCHIRAPALLI GOODS) Tiruchirapalli, Tamil Nadu", (10.7905, 78.7047)),
    ("VZP (Visakhapatnam Port), Visakhapatnam, AP", (17.6868, 83.2185)),
    ("WML (Bedeshwar Windmill), Jamnagar, Gujarat", (22.4797, 70.0577))
]
angul_lat,angul_lon=20.8444, 85.1511

# Title for the page
st.title("Hubs and Customers")

# Create a Folium map object
m = folium.Map(location=[20, 77], zoom_start=4)  # Change map background
folium.TileLayer('OpenStreetMap').add_to(m)

# Convert hubs and customers data to numpy arrays
hubs_array = np.array([hub[1] for hub in hubs])
customers_array = np.array([[customer[1], customer[2]] for customer in customers_data])

# Apply KNN algorithm to find the nearest hub for each customer
def clusters(hubs_array, customers_array):
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(hubs_array)
    distances, indices = knn.kneighbors(customers_array)
    return distances, indices

distances, indices=clusters(hubs_array, customers_array)

# Create clusters of customers around each hub
def draw_markers(indices, hubs, color):
    clusters = {}
    for i, index in enumerate(indices):
        hub_name = hubs[index[0]][0]
        if hub_name not in clusters:
            clusters[hub_name] = []
        clusters[hub_name].append(customers_data[i])


    # Add markers for each hub and its corresponding customers
    for i, (hub_name, customers) in enumerate(clusters.items()):
        hub_coords = [hub[1] for hub in hubs if hub[0] == hub_name][0]
        folium.CircleMarker(location=hub_coords, radius=5, color='red', fill=True,
                            tooltip=hub_name,  # Add hover-over text
                            popup=folium.Popup(f'<b>{hub_name}</b>', max_width=200)  # Customize pop-up window
                            ).add_to(m)
        for customer in customers:
            city, lat, lon = customer
            folium.CircleMarker(location=[lat, lon], radius=2, color='blue', fill=True,
                                tooltip=city,  # Add hover-over text
                                popup=folium.Popup(f'<b>{city}</b>', max_width=200)  # Customize pop-up window
                                ).add_to(m)
            # Add a line connecting the customer to the hub
            folium.PolyLine([hub_coords, [lat, lon]], color=color, weight=1).add_to(m)


draw_markers(indices, hubs, "red")

# Extract clusters and print them in a table format
clusters = {}
for i, index in enumerate(indices):
    hub_name = hubs[index[0]][0]
    if hub_name not in clusters:
        clusters[hub_name] = []
    clusters[hub_name].append(customers_data[i][0])

# Create a pandas DataFrame from the clusters
cluster_df = pd.DataFrame([(hub, ', '.join(customers)) for hub, customers in clusters.items()], columns=['Hub', 'Customers'])


# Display the clusters table
st.write(cluster_df)

# Display the Folium map
view_map = st.checkbox("Display Map")
if view_map:
    folium_static(m)

if st.button("Cost_calculator"):
    st.switch_page("D:/Python/pages/Cost_calculator.py")