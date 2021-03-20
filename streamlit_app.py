import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from io import StringIO
from streamlit_ace import st_ace

from business import (
    assessment_plot, 
    assess,
    income_plot,
    expense_plot,
    lifetime_expense,
    lifetime_income,
)

with open('default.yaml', 'r') as fh:
    configuration_content = fh.read()

st.set_page_config(layout='wide')

"""# Personal Finance Forecaster"""
previous_config = st.checkbox('Upload a previously saved configuration')
if previous_config:
    uploaded_file = st.file_uploader(
        '[OPTIONAL] Configuration Upload', 
        type=['yaml', 'yml', 'txt'],
        help='Upload a saved configuration (.yaml, .yml, and .txt allowed)')

    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        configuration_content = stringio.read()

"""[Documentation](https://personal-finance-forecaster.readthedocs.io/en/latest/)"""
configuration_edit = st.text_area(
    'Configuration Editor',
    value=configuration_content,
    height=200,
)

content = st_ace(
    placeholder=configuration_content,
    language='yaml',
    theme='pastel_on_dark',
    keybinding='vscode',
)
content

if st.button(
    'Update Graphs',
    help='Graphs will be generated from the configuration information above.'
    ):
    balance_df, transaction_df, configuration = assess(configuration_edit)
    st.plotly_chart(assessment_plot(balance_df), use_container_width=True)
    st.plotly_chart(expense_plot(
        transaction_df, [
            transaction_df['age'].min(),
            transaction_df['age'].max(),
        ]),
        use_container_width=True
    )
    st.plotly_chart(lifetime_expense(transaction_df), use_container_width=True)
    st.plotly_chart(lifetime_income(transaction_df), use_container_width=True)

""" Version 0.1 """