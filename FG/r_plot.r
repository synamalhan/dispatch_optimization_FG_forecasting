# Load necessary libraries
library(sf)
library(dplyr)
library(geosphere)
library(leaflet)
library(DBI)
library(odbc)

# Function to convert degrees to radians
deg2rad <- function(deg) {
  return(deg * (pi / 180))
}

# Load hub data from CSV file
df_hubs <- read.csv('D:/JSPL/Dispatch_FG/Data/hub_locations.csv')

# Connect to the SQL Server database
conn <- dbConnect(odbc::odbc(), 
                  Driver = "ODBC Driver 17 for SQL Server", 
                  Server = "SYNA", 
                  Database = "DISPATCH_DATA", 
                  UID = "testuser", 
                  PWD = "User123")

# Load customer data from database
df_customers <- dbGetQuery(conn, "SELECT CITY, LAT, LON FROM PLATE_TABLE")
dbDisconnect(conn)

# Create a GeoDataFrame for hubs
gdf_hubs <- st_as_sf(df_hubs, coords = c("Lon", "Lat"), crs = 4326)

# Create a GeoDataFrame for customers
gdf_customers <- st_as_sf(df_customers, coords = c("LON", "LAT"), crs = 4326)

# Define Angul location
angul_lat <- 20.8444
angul_lon <- 85.1511

# Haversine distance function
haversine <- function(lat1, lon1, lat2, lon2) {
  R <- 6371  # Radius of the Earth in kilometers
  dlat <- deg2rad(lat2 - lat1)
  dlon <- deg2rad(lon2 - lon1)
  lat1 <- deg2rad(lat1)
  lat2 <- deg2rad(lat2)
  
  a <- sin(dlat / 2)^2 + cos(lat1) * cos(lat2) * sin(dlon / 2)^2
  c <- 2 * atan2(sqrt(a), sqrt(1 - a))
  distance <- R * c
  return(distance)
}

# Calculate distance from Angul to each customer
gdf_customers$distance_from_angul <- mapply(haversine, angul_lat, angul_lon, st_coordinates(gdf_customers)[, 2], st_coordinates(gdf_customers)[, 1])

# Create a new column to store the cluster ID
gdf_customers$cluster_id <- NA

# Iterate over customers
for (i in 1:nrow(gdf_customers)) {
  row <- gdf_customers[i, ]
  if (row$distance_from_angul <= 300) {
    gdf_customers$cluster_id[i] <- 0
  } else {
    distances_to_hubs <- mapply(haversine, st_coordinates(gdf_hubs)[, 2], st_coordinates(gdf_hubs)[, 1], row$geometry[[2]], row$geometry[[1]])
    min_distance_hub <- which.min(distances_to_hubs)
    gdf_customers$cluster_id[i] <- min_distance_hub
  }
}

# Create a Leaflet map
m <- leaflet() %>%
  addTiles() %>%
  setView(lng = 77, lat = 20, zoom = 4)

# Add Angul location as a marker
m <- m %>% addCircleMarkers(lng = angul_lon, lat = angul_lat, color = 'blue', popup = 'Angul')

# Add hubs as markers
m <- m %>% addCircleMarkers(data = gdf_hubs, color = 'blue', radius = 5)

# Add lines connecting hubs to Angul in grey
for (i in 1:nrow(gdf_hubs)) {
  m <- m %>% addPolylines(lng = c(angul_lon, st_coordinates(gdf_hubs)[i, 1]), lat = c(angul_lat, st_coordinates(gdf_hubs)[i, 2]), color = 'grey', weight = 0.5)
}

# Add lines connecting standalone points to Angul in red
for (i in 1:nrow(gdf_customers)) {
  if (gdf_customers$cluster_id[i] == 0) {
    m <- m %>% addPolylines(lng = c(angul_lon, st_coordinates(gdf_customers)[i, 1]), lat = c(angul_lat, st_coordinates(gdf_customers)[i, 2]), color = 'red', weight = 2)
  }
}

# Add lines connecting hubs to their corresponding customers in green
for (i in 1:nrow(gdf_customers)) {
  if (gdf_customers$cluster_id[i] > 0) {
    hub <- gdf_hubs[gdf_customers$cluster_id[i], ]
    m <- m %>% addPolylines(lng = c(st_coordinates(hub)[1], st_coordinates(gdf_customers)[i, 1]), lat = c(st_coordinates(hub)[2], st_coordinates(gdf_customers)[i, 2]), color = 'green', weight = 2)
  }
}

# Add customers as CircleMarkers with different colors for each cluster
cluster_colors <- colorFactor(rainbow(nrow(gdf_hubs) + 1), domain = gdf_customers$cluster_id)
m <- m %>% addCircleMarkers(data = gdf_customers, color = ~cluster_colors(cluster_id), radius = 2, fill = TRUE)

# Save the map to an HTML file
saveWidget(m, 'plate_map.html', selfcontained = TRUE)
