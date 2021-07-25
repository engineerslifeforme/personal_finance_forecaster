""" Forecast Configuration """
from datetime import date

import streamlit as stl

def display_forecast_configuration(st: stl, defaults: dict = None) -> dict:
    if defaults is None:
        default_data = {}
    else:
        default_data = defaults
    
    left, right = st.beta_columns(2)
    
    inflation = left.number_input(
        'Inflation (%)',
        min_value=0.0,
        max_value=100.0,
        value=default_data.get('inflation', 0.02)*100.0,
        step=0.1,
        help='Inflation rate'
    )/100.0
    
    return_rate = right.number_input(
        'Returns Rate (%)',
        min_value=0.0,
        max_value=100.0,
        value=default_data.get('returns', 0.07) * 100.0,
        step=0.1,
        help='Returns rate'
    )/100.0

    start_age = left.number_input(
        'Start Age',
        min_value=0,
        max_value=125,
        value=default_data.get('start_age', 25),
        step=1,
        help='Starting age of the individual for forecast perspective'
    )
    stop_age = right.number_input(
        'End Age',
        min_value=1+start_age,
        max_value = start_age+125,
        value=default_data.get('stop_age', start_age+75),
        step=1,
        help='Ending age of the individual for foreast perspective'
    )
    today = date.today()
    start_year = left.number_input(
        'Start Year',
        min_value=1900,
        max_value=2100,
        value=default_data.get('start_year', today.year),
        step=1,
        help='Starting year of forecast'
    )
    start_month = right.number_input(
        'Start Month',
        min_value=1,
        max_value=12,
        value=default_data.get('start_month', today.month),
        step=1,
        help='Starting month of forecast, 1 = January'
    )
    start_balance = st.number_input(
        'Starting Balance ($)',
        value = default_data.get('start_balance', 0.0),
        step = 0.01,
        help='Starting Investment Balance ($)'
    )
    return {
        'inflation': inflation,
        'returns': return_rate,
        'start_age': start_age, 
        'stop_age': stop_age,
        'start_year': start_year,
        'start_month': start_month,
        'start_balance': start_balance,
    }
