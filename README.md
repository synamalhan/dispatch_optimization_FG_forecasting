# FG Forecasting and Last Point Distribution Optimizer

## Overview

This project involves two main components:
1. **FG Forecasting:** Utilizes Python 3.12.4, Streamlit, MS SQL Server 2022, and XGBoost to forecast future FG values.
2. **Last Point Distribution:** Uses Python 3.12.4, Folium, Streamlit, and OSRM to optimize the distribution of stockyards.

## FG Forecasting

### Overview

The FG Forecasting module predicts future FG values using machine learning techniques. This module uses Streamlit for the user interface, XGBoost for the prediction model, and MS SQL Server 2022 for data storage. It provides insights and an ideal date for FG completion, which can be used to plan and allocate resources efficiently.

### Features

- **Home Page:** Explains the general process of plate production and the importance of FG forecasting.
- **Predict Page:** Uses XGBoost and various metrics to create a grade-wise trend to predict an approximate FG completion date.
- **Multi-Predict Page:** Allows users to view and make multiple predictions at a time.
- **Train Page:** Enables users to add new data for further training the model.

### Technologies

- **Python 3.12.4**
- **Streamlit**
- **MS SQL Server 2022**
- **XGBoost**

### Usage

1. **Installation:**
   ```bash
   pip install streamlit xgboost pyodbc
   ```
2. **Running the App:**

```bash
streamlit run FG_Forecasting_main.py
```
3. **Database Setup:**

- Ensure MS SQL Server 2022 is installed and properly configured.
- Create necessary tables and load your data.

### Pages
1. **pages/home.py:** Provides an overview of the plate production process and the significance of the project.
2. **pages/preict.py:** Offers a user-friendly interface to predict FG completion dates using various metrics.
3. **pages/multi_predict.py:** Enables batch processing of predictions.
4. **pages/train.py:** Allows for the inclusion of new data to enhance the prediction model.
5. **FG_Forecasting_frontend.py:** Contains all the frontend programming for the pages
6. **FG_Forecasting_database.py:** Establishes connection to the database and fetches the data (To change database edit configuration here)
7. **FG_Forecasting_logic.py:** Carries out training of model, predicting of output, and any additional hard coded logics
8. **FG_Forecasting_add_data.py:** Takes care of new data addition, including data cleaning, combining, processing, and uploading
9. **FG_Forecasting_main.py:** Executes the main function of the project and calls all the required pages and methods

## Last Point Distribution
### Overview
The Last Point Distribution module optimizes the distribution of stockyards using geospatial data. This module uses Folium for interactive mapping, OSRM for route optimization, and MS SQL Server 2022 for data storage. It helps identify the most cost-effective routes for distributing goods from stockyards to customers.

## Features
1. **Existing Stockyard Map:** Displays current customers and their nearest stockyards.
2. **Existing Stockyard Cost Calculator:** Calculates the actual distance and cost between two points.
3. **Adding a new Stockyard:** Allows adding new stockyards and visualizing their potential impact.
4. **New Stockyard Cost Analysis:** Performs a cost analysis between new and old stockyards to identify better service options.

### Technologies
- **Python 3.12.4**
- **Folium**
- **Streamlit**
- **OSRM**

### Usage
1. **Installation:**
```bash
pip install streamlit folium osrm-py streamlit-folium
```
2. **Running the App:**
```bash
streamlit run LP_main.py
```
3. **Database Setup:**
- Ensure both the csv files ```database.csv``` and ```archive.csv``` are installed and placed in approproate repositories

### Pages
1. **pages/home.py:** Shows an overview of the project and provides links to all relevant pages
2. **pages/exist_map.py:** Shows an overview of current stockyards and their corresponding customers.
3. **pages/exist_cost_calc.py:** Provides a tool to calculate distances and costs between given points.
4. **pages/new_map.py:** Offers functionality to add new stockyards and assess their impact.
5. **pages/new_cost_analysis.py:** Conducts cost analysis to compare new and existing stockyards for optimal distribution.
6. **LP_main.py:** Executes the main function of the project
