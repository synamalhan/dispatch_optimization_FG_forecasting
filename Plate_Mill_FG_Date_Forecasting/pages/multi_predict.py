from datetime import date, timedelta
import time
import FG_Forecasting_frontend as frontend
import FG_Forecasting_database as db
import FG_Forecasting_logic as logic
import FG_Forecasting_add_data as add_data
import streamlit as st
import pandas as pd

# Connect to the database
crs, conn = db.connect_to_database()

# Retrieve internal grades and supply conditions from the database
internal_grade_map = db.get_all_internal_grades(crs)
supply_condition_map = db.get_all_supply_condition(crs)

result = frontend.page_layout_multi(internal_grade_map, supply_condition_map)

predicted_df=[]
if result:
    result, edited_data, container = result
    entered_data_df = pd.DataFrame(edited_data)

    grades = entered_data_df['int_grade'].unique()

    for grade in grades:
        df = db.load_all_training_data(crs, grade)
        filtered_entries = entered_data_df[entered_data_df['int_grade'] == grade]
        xgb_model = logic.train_model(df)

        for _, row in filtered_entries.iterrows():
            future_df = pd.DataFrame({
                'QUANTITY': [row['quantity']],
                'THICKNESS': [row['thickness']],
                'LENGTH': [row['length']],
                'WIDTH': [row['width']],
                'SUPPLY_CONDITION': [row['supply_condition']]
            })

            future_df['SUPPLY_CONDITION'] = pd.Categorical(future_df['SUPPLY_CONDITION'])

            # Prepare the row for prediction
            days = logic.predict_days(xgb_model, future_df)
            tpip = 'Yes' if row['tpip'] else 'No'
            days, completion_date = logic.added_logics(days, row['supply_condition'], tpip, row['thickness'], row['buffer'], row['htc_buffer'], row['start_date'])


            # Append the prediction to the predicted_df
            predicted_row = {
                "order_num": row["order_num"],
                "PREDICTED_DAYS": days,  # predict_days returns a float
                "Approximate Completion Date": completion_date
            }
            predicted_df.append(predicted_row)

    frontend.display_output_multi(predicted_df, container)
else:
    pass

    