from io import StringIO
import locale
import base64

import streamlit as st
import numpy as np
import pandas as pd
import yaml

from business import (
    assessment_plot, 
    assess,
    income_plot,
    expense_plot,
    lifetime_expense,
    lifetime_income,
)
from streamlit_support import df_to_csv_download
import SessionState

locale.setlocale(locale.LC_ALL, '')

session_state = SessionState.get(expenses=[])

with open('default.yaml', 'r') as fh:
    configuration_content = fh.read()
    config = yaml.load(configuration_content, Loader=yaml.SafeLoader)

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
    height=300,
)
if st.button(
    'Download Configuration',
    help='Save the current configuration locally',
):
    #https://raw.githubusercontent.com/MarcSkovMadsen/awesome-streamlit/master/gallery/file_download/file_download.py
    b64 = base64.b64encode(configuration_edit.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/yaml;base64,{b64}">Download YAML File</a> (right-click and save as &lt;configuration&gt;.yaml)'
    st.markdown(href, unsafe_allow_html=True)

st.write(session_state.expenses)

st.subheader('Income Sources')
expense_name = st.text_input('Name')
expense_amount = st.number_input('Amount ($/month)')
if st.checkbox('Expense End Date'):


if st.button('Add'):
    session_state.expenses.append('two')

if st.checkbox('GUI Configuration'):
    st.slider(
        'Age Range (Years)', 
        min_value=0,
        max_value=125,
        value=(20,100),
        step=1,
    )
    st.slider(
        'Inflation (%)',
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
    )
    st.slider(
        'Appreciation (%)',
        min_value=0.0,
        max_value=20.0,
        value=7.0,
        step=0.1,
    )
    st.slider(
        'Start Year',
        min_value=2021,
        max_value=2121,
        step=1,
        value=2021,
    )
    st.slider(
        'Start Month',
        min_value=1,
        max_value=12,
        value=1,
        step=1,
    )
    st.number_input(
        'Starting Balance',
        value=config['start_balance']
    )

if st.button(
    'Analyze Forecast',
    help='Forecast above will be analyzed to produce metrics and graphs'
    ):
    balance_df, transaction_df, configuration = assess(configuration_edit)
    
    #balance_df.to_csv('balance.csv')

    st.markdown('Download Balanace Data (CSV)')
    href = df_to_csv_download(balance_df)
    st.markdown(href, unsafe_allow_html=True)

    st.markdown('Download Income and Expenses Data (CSV)')
    href = df_to_csv_download(transaction_df)
    st.markdown(href, unsafe_allow_html=True)
    
    st.subheader('RESULTS')

    ending_balance = balance_df['balance'].values[-1]
    ending_balance_str = locale.currency(
        ending_balance,
        grouping=True,
    )
    st.write(f"Ending Balance: {ending_balance_str}")
    if ending_balance < 0:
        funds_extinguished_age = balance_df[balance_df['balance'].abs() == balance_df['balance'].abs().min()]['age'].values[0]
        st.write(f'Funds extinguished at age {funds_extinguished_age}')
    else:
        st.write(f"Funds will support through age {configuration['stop_age']}")

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

""" Version 0.2 """