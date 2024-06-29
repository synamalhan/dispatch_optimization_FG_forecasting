import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QCalendarWidget, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pyodbc

class PlateFGForecasting(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Plate FG Forecasting")
        self.setGeometry(300, 300, 600, 400)

        layout = QGridLayout()

        # Add a title
        title = QLabel("Plate FG Forecasting")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 2)

        # Slab ID
        slabIDLabel = QLabel("Slab ID:")
        self.slabIDEdit = QLineEdit()
        layout.addWidget(slabIDLabel, 1, 0)
        layout.addWidget(self.slabIDEdit, 1, 1)

        # Length
        lengthLabel = QLabel("Length:")
        self.lengthEdit = QLineEdit()
        self.lengthEdit.setValidator(QDoubleValidator())
        layout.addWidget(lengthLabel, 2, 0)
        layout.addWidget(self.lengthEdit, 2, 1)

        # Width
        widthLabel = QLabel("Width:")
        self.widthEdit = QLineEdit()
        self.widthEdit.setValidator(QDoubleValidator())
        layout.addWidget(widthLabel, 3, 0)
        layout.addWidget(self.widthEdit, 3, 1)

        # Thickness
        thicknessLabel = QLabel("Thickness:")
        self.thicknessEdit = QLineEdit()
        self.thicknessEdit.setValidator(QDoubleValidator())
        layout.addWidget(thicknessLabel, 4, 0)
        layout.addWidget(self.thicknessEdit, 4, 1)

        # Quantity
        quantityLabel = QLabel("Quantity:")
        self.quantityEdit = QLineEdit()
        self.quantityEdit.setValidator(QDoubleValidator())
        layout.addWidget(quantityLabel, 5, 0)
        layout.addWidget(self.quantityEdit, 5, 1)

        # Supply Route
        supplyRouteLabel = QLabel("Supply Route:")
        self.supplyRouteCombo = QComboBox()
        self.supplyRouteCombo.addItem("NR+SR", 8)
        self.supplyRouteCombo.addItem("TMCP(TMC+ACC)")
        self.supplyRouteCombo.addItem("N AND SR", 5)
        self.supplyRouteCombo.addItem("Q&T", 11)
        self.supplyRouteCombo.addItem("Q/Q&T", 12)
        self.supplyRouteCombo.addItem("Q", 10)
        self.supplyRouteCombo.addItem("N&T", 6)
        self.supplyRouteCombo.addItem("AR", 1)
        self.supplyRouteCombo.addItem("ONLINE NORMALIZING", 9)
        self.supplyRouteCombo.addItem("ASTM A-578 L-B", 2)
        self.supplyRouteCombo.addItem("NR", 7)
        self.supplyRouteCombo.addItem("THERMO MECHANICAL ROLLE", 13)
        self.supplyRouteCombo.addItem("TMCP", 14)
        self.supplyRouteCombo.addItem("N", 4)
        self.supplyRouteCombo.addItem("FN", 3)
        layout.addWidget(supplyRouteLabel, 6, 0)
        layout.addWidget(self.supplyRouteCombo, 6, 1)

        # WIP Date
        wipDateLabel = QLabel("WIP Date:")
        self.wipDateCalendar = QCalendarWidget()
        layout.addWidget(wipDateLabel, 7, 0)
        layout.addWidget(self.wipDateCalendar, 7, 1)

        # Internal Grade
        internalGradeLabel = QLabel("Internal Grade:")
        self.internalGradeCombo = QComboBox()
        self.internalGradeCombo.addItem("288", 288)
        self.internalGradeCombo.addItem("385", 385)
        self.internalGradeCombo.addItem("262", 262)
        self.internalGradeCombo.addItem("225", 225)
        self.internalGradeCombo.addItem("240", 240)
        self.internalGradeCombo.addItem("226", 226)
        self.internalGradeCombo.addItem("80", 80)
        self.internalGradeCombo.addItem("249", 249)
        layout.addWidget(internalGradeLabel, 8, 0)
        layout.addWidget(self.internalGradeCombo, 8, 1)

        # Predict Button
        predictButton = QPushButton("Predict")
        predictButton.clicked.connect(self.predictFG)
        layout.addWidget(predictButton, 9, 0, 1, 2)

        # Output Text Edit
        self.outputTextEdit = QTextEdit()
        layout.addWidget(self.outputTextEdit, 10, 0, 1, 2)

        self.setLayout(layout)

    def predictFG(self):
        # Get user input values
        slabID = self.slabIDEdit.text()
        length = float(self.lengthEdit.text())
        width = float(self.widthEdit.text())
        thickness = float(self.thicknessEdit.text())
        quantity = float(self.quantityEdit.text())
        supplyRoute = self.supplyRouteCombo.currentData()
        wipDate = self.wipDateCalendar.selectedDate().toPyDate()
        internalGrade = self.internalGradeCombo.currentData()

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
        predicted_fg_date = wipDate + pd.Timedelta(days=future_pred[0])

        # Output result
        self.outputTextEdit.setText(f"The predicted FG date is: {predicted_fg_date}\nThe production is predicted to take {future_pred[0]:.2f} days")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlateFGForecasting()
    window.show()
    sys.exit(app.exec_())