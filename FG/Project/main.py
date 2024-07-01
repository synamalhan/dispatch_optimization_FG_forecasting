import frontend as frontend
import database as db
import logic as logic

def main():
    frontend.page_configuration()

    crs = db.connect_to_database()

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


if __name__ == "__main__":
    main()