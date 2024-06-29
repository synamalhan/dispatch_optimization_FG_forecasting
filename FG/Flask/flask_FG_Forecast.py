from flask import Flask, request, render_template, jsonify
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pyodbc

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        slabID = request.form['slabID']
        length = float(request.form['length'])
        width = float(request.form['width'])
        thickness = float(request.form['thickness'])
        quantity = float(request.form['quantity'])
        supplyRoute = int(request.form['supplyRoute'])
        wipDate = request.form['wipDate']
        internalGrade = int(request.form['internalGrade'])

        # Create future dataframe
        future_df = pd.DataFrame({
            'QUANTITY': [quantity],
            'THICKNESS': [thickness],
            'LENGTH': [length],
            'WIDTH': [width],
            'SUPPLY_IND': [supplyRoute]
        })

        # Load data from SQL Server database
        server = 'SYNA'
        database = 'DISPATCH_DATA'
        username = 'testuser'
        password = 'User123'

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

        cursor = cnxn.cursor()

        query = f"""
            SELECT 
                QUANTITY, THICKNESS, LENGTH, WIDTH, LAST_BIN_IND, WIP_ENTRY, FG_ENTRY, TOTAL_TIME, SUPPLY_IND
            FROM 
                FINAL
            WHERE
            GRADE_IND = {internalGrade} AND TOTAL_TIME<10.28
        """

        cursor.execute(query)
        data = cursor.fetchall()

        data_values = [list(row) for row in data]
        df = pd.DataFrame(data_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH', 'WIDTH', 'LAST_BIN_IND', 'WIP_ENTRY', 'FG_ENTRY', 'TOTAL_TIME', 'SUPPLY_IND'])

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
        df.drop(['FG_ENTRY', 'TOTAL_TIME', 'WIP_ENTRY', 'LAST_BIN_IND'], axis=1, inplace=True)

        # Split data into training and testing sets
        X = df.drop('y', axis=1)
        y = df['y']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create and train an XGBoost model
        xgb_model = xgb.XGBRegressor()
        xgb_model.fit(X_train, y_train)

        # Make predictions on the future dataframe
        future_pred = xgb_model.predict(future_df)

        # Calculate predicted FG date
        predicted_fg_date = pd.to_datetime(wipDate) + pd.Timedelta(days=future_pred[0])

        return jsonify({'predictedFGDate': str(predicted_fg_date), 'productionDays': f"{future_pred[0]:.2f}"})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)