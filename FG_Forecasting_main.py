
import time
import FG_Forecasting_frontend as frontend
import FG_Forecasting_database as db
import FG_Forecasting_logic as logic
import FG_Forecasting_add_data as add_data
import streamlit as st

def main():

    page = frontend.page_configuration()
    crs, conn = db.connect_to_database()

    
    if page =='Predict':

        internal_grade_map = db.get_all_internal_grades(crs)
        supply_condition_map = db.get_all_supply_condition(crs)
        result = frontend.page_layout(internal_grade_map, supply_condition_map)


        if result:
            predict, internal_grade, supply_condition, tpip, thickness, buffer_cutting, buffer_htc, future_df = result

            df = db.load_all_training_data(crs, internal_grade)

            model_predicted_days = logic.train_model(df, future_df)
            predicted_days = logic.added_logics(model_predicted_days, supply_condition, tpip, thickness, buffer_cutting, buffer_htc)

            frontend.display_output(predicted_days)
        else:
            pass



    elif page == 'Train':
        pm_operations, masterdata_goods, train= frontend.upload_files()

        

        if train:
            with st.spinner(text="Uploading..."):
                df_train = add_data.combine_data(pm_operations, masterdata_goods)
                add_data.clean_data(df_train)
                add_data.push_data_into_temp(df_train, crs, conn)
                done = add_data.push_into_master_data(crs, conn)
            st.success('Data has been added to the database')
        else:
            st.write("Upload Files")





if __name__ == "__main__":
    main()