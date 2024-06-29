import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pyodbc

# Load data from SQL Server database
server = 'SYNA'
database = 'DISPATCH_DATA'
username = 'testuser'
password = 'User123'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

cursor = cnxn.cursor()

cursor.execute('''SELECT COUNT(*), GRADE_IND FROM FINAL
GROUP BY GRADE_IND
HAVING COUNT(*)>1000''')
ran = cursor.fetchall()
grade_values = [i[1] for i in ran]


 
for k in grade_values:
    
    query = f"""
        SELECT 
            QUANTITY, THICKNESS, LENGTH, WIDTH, LAST_BIN_IND, WIP_ENTRY, FG_ENTRY, TOTAL_TIME, SUPPLY_IND
        FROM 
            FINAL
        WHERE
        GRADE_IND = {k} AND TOTAL_TIME<10.28
    """

    cursor.execute(query)
    data = cursor.fetchall()

    data_values = [list(row) for row in data]
    df = pd.DataFrame(data_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH' , 'WIDTH', 'LAST_BIN_IND', 'WIP_ENTRY', 'FG_ENTRY', 'TOTAL_TIME', 'SUPPLY_IND'])

    # Convert PRD and FG columns to datetime format
    df['WIP_ENTRY'] = pd.to_datetime(df['WIP_ENTRY'])
    df['FG_ENTRY'] = pd.to_datetime(df['FG_ENTRY'])

    # Calculate days between PRD and FG
    df['days'] = (df['FG_ENTRY'] - df['WIP_ENTRY']).dt.days

    # Create a new column 'y' for values
    df.rename(columns={'days': 'y'}, inplace=True)

    # Create additional regressor columns
    dummies = pd.get_dummies(df['SUPPLY_IND'])
    if dummies.shape[1] > 0:
        df['SUPPLY_IND'] = dummies.iloc[:, 0]
    else:
    # handle the case where there's only one unique value in df['SUPPLY_IND']
        df['SUPPLY_IND'] = 0  # or some other default value

    actual_timings = df['TOTAL_TIME'].tolist()


    # Drop unnecessary columns
    df.drop(['FG_ENTRY', 'TOTAL_TIME', 'WIP_ENTRY'], axis=1, inplace=True)

    # Split data into training and testing sets
    X = df.drop('y', axis=1)
    y = df['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train an XGBoost model
    xgb_model = xgb.XGBRegressor()
    xgb_model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = xgb_model.predict(X_test)

    # Evaluate the model
    mse = xgb_model.score(X_test, y_test)
    print(f'MSE: {mse}')

    # Create a future dataframe for the next 30 days

    q = f"""
        SELECT 
            QUANTITY, THICKNESS, LENGTH, WIDTH, LAST_BIN_IND, SUPPLY_IND
        FROM 
            FINAL
        WHERE
        GRADE_IND = {k} AND TOTAL_TIME<10.28
    """

    cursor.execute(q)
    data_f = cursor.fetchall()

    dataf_values = [list(row) for row in data_f]
    future_df = pd.DataFrame(dataf_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH' , 'WIDTH', 'LAST_BIN_IND', 'SUPPLY_IND'])

    # future_df = pd.DataFrame({
    #     'QUANTITY': [7.871, 0.78, 2.826, 8.754, 4.115, 1.884, 7.871, 8.478, 8.614, 2.286],
    #     'THICKNESS': [40, 10, 15, 30, 14, 20, 40, 30, 36, 16],
    #     'LENGTH': [10894, 6300, 12000, 10560, 12910, 6000, 10894, 12000, 12000, 12050],
    #     'WIDTH': [2301, 1500, 2000, 3520, 2900, 2000, 2301, 3000, 2500, 1500],
    #     'LAST_BIN_IND': [7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
    #     'SUPPLY_IND': [7, 1, 7, 7, 14, 7, 7, 7, 7, 7]
    # })

    # Actual timings for the future dataframe

    # Make predictions on the future dataframe
    future_pred = xgb_model.predict(future_df)

    # Print predicted values with actual values
    for i, (pred, actual) in enumerate(zip(future_pred, actual_timings)):
        print(f'Predicted value for {i}: {pred}, Actual value: {actual}')


    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.text(0.5, 0.9, f'MSE: {mse:.2f}', ha='center', va='center', transform=plt.gca().transAxes)




    plt.scatter((actual_timings), (future_pred), label='Actual vs Predicted', color='blue', s=5)
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title(f'Actual vs Predicted Values for {k}')
    plt.legend()
    plt.show(block=False)

    # plt.text(0.5, 0.9, f'MSE: {mse:.2f}', ha='center', va='center', transform=plt.gca().transAxes)

    # plt.scatter(range(len(actual_timings)), sorted(actual_timings), label='Actual', color='blue')
    # plt.scatter(range(len(future_pred)), sorted(future_pred), label='Predicted', color='red')

    # plt.xlabel('Actual')
    # plt.ylabel('Predicted')
    # plt.title(f'Actual vs Predicted Values for{k}')
    # plt.legend()
    # plt.show()

    # importance = xgb_model.feature_importances_
    # print(importance)
    # import matplotlib.pyplot as plt

    # feature_names = X.columns.tolist()
    # importance = xgb_model.feature_importances_
    # plt.bar(range(len(importance)), importance)
    # plt.xticks(range(len(importance)), feature_names, rotation=90)
    # plt.xlabel('Feature')
    # plt.ylabel('Feature Importance')
    # plt.show()

    # import shap

    # explainer = shap.TreeExplainer(xgb_model)
    # shap_values = explainer.shap_values(X_test)

    # shap.summary_plot(shap_values, X_test, plot_type="bar")
    
plt.show(block=True) 