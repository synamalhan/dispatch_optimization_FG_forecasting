import FG_Forecasting_frontend as frontend
import FG_Forecasting_database as db
import FG_Forecasting_logic as logic
import FG_Forecasting_training as train

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
        frontend.upload_files()
        # pm_operations, masterdata_goods, training= frontend.upload_files()
        # if training:
        #     df_train = train.combine_data(pm_operations, masterdata_goods)
        #     train.push_data(df_train, crs, conn)





if __name__ == "__main__":
    main()