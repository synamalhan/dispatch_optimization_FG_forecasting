import xgboost as xgb
from sklearn.model_selection import train_test_split
import pandas as pd

def train_model(df, future_df):
    # Split data into training and testing sets
    X = df.drop('y', axis=1)
    y = df['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train an XGBoost model
    xgb_model = xgb.XGBRegressor(enable_categorical=True)
    xgb_model.fit(X_train, y_train)

    # Make predictions on the future dataframe
    future_pred = xgb_model.predict(future_df)
    predicted_days = future_pred[0]

    return predicted_days



def added_logics(predicted_days, supply_condition, tpip, thickness, buffer_cutting, buffer_htc):
    # Determine supply route condition
    if(supply_condition in ['AR','NR','TMCP']):
        supply_route = 'NON HTC'
    else:
        supply_route = 'HTC'

    # Adjust predicted days based on user inputs
    if tpip == 'Yes':
        predicted_days += 7

    if thickness < 32:
        predicted_days += (buffer_cutting / 2000)
    else:
        predicted_days += (buffer_cutting / 1400)

    if supply_route == 'HTC':
        predicted_days += (buffer_htc / 350)

    return predicted_days


