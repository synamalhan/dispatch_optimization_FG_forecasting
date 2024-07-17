import time
import FG_Forecasting_frontend as frontend
import FG_Forecasting_database as db
import FG_Forecasting_logic as logic
import FG_Forecasting_add_data as add_data
import streamlit as st

crs, conn = db.connect_to_database()
frontend.page_layout_train()
pm_operations, masterdata_goods, train= frontend.upload_files()

if train:
    with st.status(text="Uploading..."):
        st.write("Combinig Data...")
        df_train = add_data.combine_data(pm_operations, masterdata_goods)
        st.write("Cleaning & Preprocessing Data...")
        add_data.clean_data(df_train)
        add_data.push_data_into_temp(df_train, crs, conn)
        st.write("Uploading Data...")
        done = add_data.push_into_master_data(crs, conn)
    st.success('Data has been added to the database')
else:
    st.write("")