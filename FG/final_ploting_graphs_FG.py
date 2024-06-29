import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
import pyodbc
import shap
from sklearn.preprocessing import LabelEncoder

# Load data from SQL Server database
server = 'SYNA'
database = 'FG_DATA'
username = 'testuser'
password = 'User123'

# grd = 'JA35IMOP01Di'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

cursor = cnxn.cursor()

query = f"""
    SELECT 
        QUANTITY, THICKNESS, LENGTH, WIDTH, DAYS, SUPPLY_CONDITION
    FROM 
        MASTER_DATA
    WHERE
    ROLLING_DATE IS NOT NULL;
"""

cursor.execute(query)
data = cursor.fetchall()

data_values = [list(row) for row in data]
df = pd.DataFrame(data_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH', 'WIDTH', 'DAYS', 'SUPPLY_CONDITION'])

# Convert SUPPLY_CONDITION to numerical using LabelEncoder
df = pd.get_dummies(df, columns=['SUPPLY_CONDITION'])

actual_timings = df['DAYS']
# Create a new column 'y' for values
df.rename(columns={'DAYS': 'y'}, inplace=True)

# Split data into features and target
X = df.drop('y', axis=1)
y = df['y']

# Create and train an XGBoost model
xgb_model = xgb.XGBRegressor(enable_categorical=True)
xgb_model.fit(X, y)

# Make predictions on the entire dataset
y_pred = xgb_model.predict(X)

q = f"""
        SELECT 
            QUANTITY, THICKNESS, LENGTH, WIDTH, SUPPLY_CONDITION
    FROM 
        MASTER_DATA
    WHERE
    ROLLING_DATE IS NOT NULL;
    """

cursor.execute(q)
data_f = cursor.fetchall()

dataf_values = [list(row) for row in data_f]
future_df = pd.DataFrame(dataf_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH' , 'WIDTH', 'SUPPLY_CONDITION'])
future_df = pd.get_dummies(future_df, columns=['SUPPLY_CONDITION'])

future_pred = xgb_model.predict(future_df)


# Plot actual vs predicted graph
plt.figure(figsize=(10, 6))
plt.scatter((actual_timings), (future_pred), label='Actual vs Predicted', color='green', alpha = 0.2)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title(f'Actual vs Predicted Values')
plt.legend()
plt.show()

# Plot SHAP values graph
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X)

shap_exp = shap.Explanation(values=shap_values, 
                            base_values=explainer.expected_value, 
                            data=X.values, 
                            feature_names=X.columns.tolist())

# Plot SHAP beeswarm plot
plt.figure(figsize=(10, 6))
shap.plots.beeswarm(shap_exp, show=False)
plt.show()