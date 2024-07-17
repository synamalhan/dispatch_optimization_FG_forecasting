
import time
import FG_Forecasting_frontend as frontend
import FG_Forecasting_database as db
import FG_Forecasting_logic as logic
import FG_Forecasting_add_data as add_data
import streamlit as st



crs, conn = db.connect_to_database()



internal_grade_map = db.get_all_internal_grades(crs)
supply_condition_map = db.get_all_supply_condition(crs)
result = frontend.page_layout_single(internal_grade_map, supply_condition_map)


if result:
    predict, internal_grade, supply_condition, tpip, thickness, buffer_cutting, buffer_htc, future_df, container, start_date= result

    df = db.load_all_training_data(crs, internal_grade)

    xgb_model = logic.train_model(df)
    model_predicted_days = logic.predict_days(xgb_model, future_df)
    predicted_days, approximate_completion_date = logic.added_logics(model_predicted_days, supply_condition, tpip, thickness, buffer_cutting, buffer_htc, start_date)

    frontend.display_output_single(predicted_days, container, approximate_completion_date)
else:
    pass