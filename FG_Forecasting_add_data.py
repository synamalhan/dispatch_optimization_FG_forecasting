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
    columns_to_keep = ['BATCH',  '  QUANTITY', 'POSTING DATE', 'DATE', 'Internal grade', 'Thickness_y', 'Width', 'Length',   'SO-V_SUPPLYCONDITION']

    # Select only the desired columns, but only if they exist
    df_merged = df_merged[[col for col in columns_to_keep if col in df_merged.columns]]

    df_merged = df_merged.rename(columns={'Thickness_y': 'THICKNESS', 'SO-V_SUPPLYCONDITION': 'SUPPLY_CONDITION',
                                               'DATE':'ROLLING_DATE', 'POSTING DATE':'FG_DATE', '  QUANTITY': 'QUANTITY',
                                               'Internal grade':'INTERNAL_GRADE', 'Width':'WIDTH','Length':'LENGTH'})



    df_merged = df_merged.replace({np.nan: None})

    # Replace infinity values with None
    df = df_merged.replace({np.inf: None, -np.inf: None})

    df = df.dropna(subset=['BATCH' ,'QUANTITY' ,'FG_DATE' ,'INTERNAL_GRADE' ,'THICKNESS' ,'WIDTH' ,'LENGTH' ,'SUPPLY_CONDITION', 'ROLLING_DATE'], how ='all')


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
            mask = df['SUPPLY_CONDITION'].str.contains('|'.join(values), na=False, case=False)
            df.loc[mask, 'SUPPLY_CONDITION'] = key
    uniform_supply_condition(df)

    df['ROLLING_DATE'] = pd.to_datetime(df['ROLLING_DATE'], dayfirst=True)
    df['FG_DATE'] = pd.to_datetime(df['FG_DATE'], dayfirst=True)

    # remove trailing characters and commas, and convert to float
    df['THICKNESS'] = df['THICKNESS'].str.replace('mm', '').str.replace(',', '').astype(float)
    df['WIDTH'] = df['WIDTH'].str.replace('mm', '').str.replace(',', '').astype(float)
    df['LENGTH'] = df['LENGTH'].str.replace('m', '').str.replace(',', '').astype(float)

    return df


def push_data_into_temp(df, cursor, conn):
    # Get the column names from the dataframe
    column_names = [str(column) for column in df.columns.tolist()]

    insert_data_query = "INSERT INTO temp_table ( {}) VALUES ({})".format(','.join(column_names), ','.join('?' for _ in column_names))
    for i, row in df.iterrows():
        cursor.execute(insert_data_query, tuple(row))
    conn.commit()

    cursor.execute("UPDATE TEMP_TABLE\
                        SET DAYS = DATEDIFF(DAY, ROLLING_DATE, FG_DATE)")
    conn.commit()

    cursor.execute("DELETE FROM TEMP_TABLE\
                   WHERE SUPPLY_CONDITION IS NULL OR THICKNESS IS NULL OR WIDTH IS NULL OR QUANTITY IS NULL OR LENGTH IS NULL OR INTERNAL_GRADE IS NULL OR DAYS IS NULL")


def push_into_master_data(cursor, conn):
    cursor.execute("INSERT INTO MASTER_DATA SELECT * FROM TEMP_TABLE")
    conn.commit()
    return True
   