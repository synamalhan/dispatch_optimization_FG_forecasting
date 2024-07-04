import datetime
import pandas as pd
import numpy as np


def combine_data(pm, master_good):
    # Extract data from Excel files
    df1 = pd.read_excel(pm, sheet_name='RECONCILE')
    df2 = pd.read_excel(master_good, sheet_name=0)


    # Extract the first 8 digits of the batch column in File2
    df2['batch_8digits'] = df2['BATCH'].str[:8]

    # Merge the data using the salb_id and batch_8digits columns
    df_merged = pd.merge(df1, df2, left_on='SLAB_ID', right_on='batch_8digits')

    # Drop the batch_8digits column
    df_merged = df_merged.drop('batch_8digits', axis=1)

    # Select only the desired columns
    columns_to_keep = ['DATE', 'Internal grade', 'Thickness_y', 'Width', 'Length', 'Customer', 'SO', 'BATCH', '  QUANTITY', 'POSTING DATE', 'SO-V_SUPPLYCONDITION']

    # Select only the desired columns, but only if they exist
    df_merged = df_merged[[col for col in columns_to_keep if col in df_merged.columns]]

    df_merged = df_merged.rename(columns={'Thickness_y': 'Thickness', 'SO-V_SUPPLYCONDITION': 'Supply_Condition', 'DATE':'Rolling_date', 'POSTING DATE':'FG_date'})


    df_merged = df_merged.replace({np.nan: None})

    # Replace infinity values with None
    df = df_merged.replace({np.inf: None, -np.inf: None})

    df = df.dropna(subset=['ROLLING_DATE', 'Internal grade','Thickness','Width', 'Length', 'Customer', 'SO','BATCH', 'Quantity', 'FG_DATE', 'Supply_Condition'], how ='all')


    return df

def clean_data(df):

    def uniform_supply_condition(df):
        patterns = {'NR':['NORMALIZING ROLLING', 'NORMALISED ROLLING', 'NORMALIZIMG ROLLING', 'NORMALISING ROLLING'],
                    'FN':['FURNACE NORMALIZING','NORMALIZED', 'NORMALISED', 'NORMALIEZD', 'HTCN', 'ONLINE NORMALIZING'],
                    'QT':['HTCQT', 'QUENCHED & TEMPERED','QUENCHED/QUENCHED AND TEMPERED','QUENCHED/QUENCHED & TEMPERED','QUENCHED AND TEMPERED'],
                    'AR':['AS ROLLED', 'AS ROLLLED'], 
                    'TMCP':['THERMO MECHANICAL ROLLE','TMCP(TMC+ACC)'],
                    'Q':['HTCQ','QUENCHED'],
                    'NT':['NORMALIZED & TEMPERED','HTCNT'],
                    'NRSR':['N AND SR','NR + SR']}
        
        for key, values in patterns.items():
            mask = df['Supply_Condition'].str.contains('|'.join(values), na=False, case=False)
            df.loc[mask, 'Supply_Condition'] = key
    uniform_supply_condition(df)

    df['ROLLING_DATE'] = pd.to_datetime(df['ROLLING_DATE'], dayfirst=True)
    df['FG_DATE'] = pd.to_datetime(df['FG_DATE'], dayfirst=True)

    # remove trailing characters and commas, and convert to float
    df['Thickness'] = df['Thickness'].str.replace('mm', '').str.replace(',', '').astype(float)
    df['Width'] = df['Width'].str.replace('mm', '').str.replace(',', '').astype(float)
    df['Length'] = df['Length'].str.replace('m', '').str.replace(',', '').astype(float)

    return df


def push_data(df, cursor, conn):
    # Get the column names from the dataframe
    column_names = [str(column) for column in df.columns.tolist()]

    # Create a dynamic SQL query to create the table
    create_table_query = f"CREATE TABLE dynamic_table ({', '.join([f'[{column}] varchar(max)' if column == 'Customer' else f'[{column}] varchar(1000)' for column in column_names])})"
    cursor.execute(create_table_query)
    conn.commit()

    # Insert the data into the table
    insert_data_query = f"INSERT INTO dynamic_table ({', '.join([f'[{column}]' for column in column_names])}) VALUES ({', '.join(['?' for _ in column_names])})"
    for index, row in df.iterrows():
        cursor.execute(insert_data_query, tuple([str(value) if isinstance(value, datetime.datetime) else value for value in row]))
    conn.commit()