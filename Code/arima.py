import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# Example data: Monthly ice cream sales (in thousands)
data = {
    'Month': pd.date_range(start='2020-01-01', periods=24, freq='M'),
    'Sales': [10, 12, 15, 13, 17, 20, 18, 21, 25, 23, 27, 29, 
              30, 32, 35, 34, 38, 40, 20, 15, 10, 8, 5, 2]
}
df = pd.DataFrame(data)
df.set_index('Month', inplace=True)

# Plotting the data
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Sales'], marker='o')
plt.title('Monthly Ice Cream Sales')
plt.xlabel('Month')
plt.ylabel('Sales (in thousands)')
plt.grid(True)
plt.show()

# Create ARIMA model
model = ARIMA(df['Sales'], order=(2, 1, 2))
fitted_model = model.fit()

# Make predictions for the next 6 months
forecast = fitted_model.forecast(steps=6)
forecast_index = pd.date_range(start='2022-01-01', periods=6, freq='M')
forecast_series = pd.Series(forecast, index=forecast_index)

# Plot the predictions
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Sales'], marker='o', label='Actual Sales')
plt.plot(forecast_series.index, forecast_series, marker='o', color='red', linestyle='--', label='Forecasted Sales')
plt.title('Monthly Ice Cream Sales and Forecast')
plt.xlabel('Month')
plt.ylabel('Sales (in thousands)')
plt.legend()
plt.grid(True)
plt.show()
