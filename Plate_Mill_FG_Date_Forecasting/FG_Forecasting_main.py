
import time
import FG_Forecasting_frontend as frontend
import FG_Forecasting_database as db
import FG_Forecasting_logic as logic
import FG_Forecasting_add_data as add_data
import streamlit as st


frontend.page_configuration()

pg = st.navigation([st.Page("pages/home.py"),st.Page("pages/predict.py"), st.Page("pages/multi_predict.py"), st.Page("pages/train.py")],position="hidden")

pg.run()