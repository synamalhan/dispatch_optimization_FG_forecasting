import pyodbc
import pandas as pd


# Database 
def connect_to_database():
    server = ''
    database = ''
    username = ''
    password = ''

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    cursor = cnxn.cursor()
    return cursor, cnxn

# Function to fetch TOP 30 Internal Grades by number of entries 
def get_all_internal_grades(cursor):
    query = f"""
        SELECT TOP 30
            INTERNAL_GRADE
        FROM 
            MASTER_DATA
        GROUP BY 
            INTERNAL_GRADE
        ORDER BY 
            COUNT(*) DESC;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    data_values = [row[0] for row in data]
    return data_values;


# Function to fetch all supply condition from database
def get_all_supply_condition(cursor):
    query = f"""
        SELECT 
            DISTINCT(SUPPLY_CONDITION)
        FROM 
            MASTER_DATA;
     """

    cursor.execute(query)
    data = cursor.fetchall()

    data_values = [row[0] for row in data]
    return data_values;



def load_all_training_data(cursor, internalGrade):

    # SQL query to fetch data
    query = f"""
        SELECT 
            QUANTITY, THICKNESS, LENGTH, WIDTH, DAYS, SUPPLY_CONDITION
        FROM 
            MASTER_DATA
        WHERE
        ROLLING_DATE IS NOT NULL AND INTERNAL_GRADE = '{internalGrade}' AND DAYS<20;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    # Convert data to DataFrame
    data_values = [list(row) for row in data]
    df = pd.DataFrame(data_values, columns=['QUANTITY', 'THICKNESS', 'LENGTH', 'WIDTH', 'DAYS', 'SUPPLY_CONDITION'])

    # Convert SUPPLY_CONDITION to categorical
    df['SUPPLY_CONDITION'] = pd.Categorical(df['SUPPLY_CONDITION'])
    # Create a new column 'y' for values
    df.rename(columns={'DAYS': 'y'}, inplace=True)

    return df
