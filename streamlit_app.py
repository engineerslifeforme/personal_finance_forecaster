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

AGE_RANGE = [0, 125]

locale.setlocale(locale.LC_ALL, '')

session_state = SessionState.get(expenses=None)

if session_state.expenses is None:
    with open('default.yaml', 'r') as fh:
        configuration_content = fh.read()
        config = yaml.load(configuration_content, Loader=yaml.SafeLoader)
        session_state.expenses = config
else:
    config = session_state.expenses
    configuration_content = yaml.safe_dump(config)


st.set_page_config(layout='wide')

mode = st.sidebar.radio(
    'Control Type',
    ['GUI', 'YAML Configuration File']
)

"""# Personal Finance Forecaster"""
previous_config = st.checkbox('Upload a previously saved configuration [OPTIONAL]')
"""## Forecast Configuration"""
if previous_config:
    uploaded_file = st.file_uploader(
        '[OPTIONAL] Configuration Upload', 
        type=['yaml', 'yml', 'txt'],
        help='Upload a saved configuration (.yaml, .yml, and .txt allowed)')

    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        configuration_content = stringio.read()
        session_state.expenses = yaml.safe_load(configuration_content)

        
if mode != 'GUI':
    """[Documentation](https://personal-finance-forecaster.readthedocs.io/en/latest/)"""

    configuration_edit = st.text_area(
        'Configuration Editor',
        value=configuration_content,
        height=300,
    )
    session_state.expenses = yaml.safe_load(configuration_edit)

else: # GUI Configuration
    selected_age_range = st.slider(
        'Age Range (Years)', 
        min_value=AGE_RANGE[0],
        max_value=AGE_RANGE[1],
        value=(20,100),
        step=1,
    )
    session_state.expenses['start_age'] = int(selected_age_range[0])
    session_state.expenses['stop_age'] = int(selected_age_range[1])
    session_state.expenses['inflation'] = (st.slider(
        'Inflation (%)',
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
    ))/100.0
    session_state.expenses['returns'] = (st.slider(
        'Appreciation (%)',
        min_value=0.0,
        max_value=20.0,
        value=7.0,
        step=0.1,
    ))/100.0
    session_state.expenses['start_year'] = st.slider(
        'Start Year',
        min_value=2021,
        max_value=2121,
        step=1,
        value=2021,
    )
    session_state.expenses['start_month'] = st.slider(
        'Start Month',
        min_value=1,
        max_value=12,
        value=1,
        step=1,
    )
    session_state.expenses['start_balance'] = st.number_input(
        'Starting Balance',
        value=config['start_balance']
    )

"""## Income Sources"""
income_table = st.empty()
if mode == 'GUI':
    if st.checkbox('Modify Income'):
        if st.checkbox('Add Additional Income'):
            income_name = st.text_input('Income Source Name')
            income_amount = st.number_input('Income Source Amount ($/month)')
            use_income_end_age = st.checkbox('Income End Age [OPTIONAL]')
            if use_income_end_age:
                income_end_age = st.slider(
                    'Income End Age',
                    min_value=selected_age_range[0],
                    max_value=selected_age_range[1],
                    step=1,
                )
            include_income_tax = st.checkbox('Income Tax [OPTIONAL]')
            if include_income_tax:
                income_tax = st.slider(
                    'Income Tax Rate (%)',
                    min_value=0,
                    max_value=100,
                    step=1,
                )
            if st.button('Add Income Source'):
                income_item = {
                    'name': income_name,
                    'amount': income_amount,
                }
                if include_income_tax:
                    income_item['tax'] = float(income_tax)/100.0
                if use_income_end_age:
                    income_item['stop_age'] = income_end_age
                session_state.expenses['income'].append(income_item)
        if st.checkbox('Delete Income Item'):
            delete_row = st.number_input(
                'Row Number to Delete',
                value=0,
                min_value=0,
                max_value = len(session_state.expenses['income']),
                step=1,
            )
            if st.button('Delete Row'):
                del session_state.expenses['income'][delete_row]
income_table.table(pd.DataFrame(session_state.expenses['income']).fillna(''))

"""## Expenses Sources"""
expense_table = st.empty()
if mode == 'GUI':
    if st.checkbox('Modify Expenses'):
        add_expense_col, del_expense_col = st.beta_columns(2)
        add_expense_col.subheader('Add Expense')
        expense_name = add_expense_col.text_input('Expense Source Name')
        expense_amount = add_expense_col.number_input(
            'Expense Source Amount ($/month)',
            step=0.01
        )
        use_expense_end_age = add_expense_col.checkbox('Expense End Age [OPTIONAL]')
        inflate = not add_expense_col.checkbox('Do Not Apply Inflation')
        if use_expense_end_age:
            expense_end_age = add_expense_col.slider(
                'Expense End Age',
                min_value=selected_age_range[0],
                max_value=selected_age_range[1],
                step=1,
            )
        if add_expense_col.button('Add Expense Source'):
            expense_item = {
                'name': expense_name,
                'amount': expense_amount,
            }
            if use_expense_end_age:
                expense_item['stop_age'] = expense_end_age
            session_state.expenses['expenses'].append(expense_item)
        
        del_expense_col.subheader('Delete Expense')
        delete_row = del_expense_col.number_input(
            'Row Number to Delete',
            value=0,
            min_value=0,
            max_value = len(session_state.expenses['expenses']),
            step=1,
        )
        if del_expense_col.button('Delete Row'):
            del session_state.expenses['expenses'][delete_row]

expense_table.table(pd.DataFrame(session_state.expenses['expenses']).fillna(''))

""" # Results """

if st.button(
    'Download Forecast Configuration',
    help='Save the current configuration locally',
):
    #https://raw.githubusercontent.com/MarcSkovMadsen/awesome-streamlit/master/gallery/file_download/file_download.py
    b64 = base64.b64encode(configuration_edit.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/yaml;base64,{b64}">Download YAML File</a> (right-click and save as &lt;configuration&gt;.yaml)'
    st.markdown(href, unsafe_allow_html=True)

balance_df, transaction_df, configuration = assess(session_state.expenses)

#balance_df.to_csv('balance.csv')

href = df_to_csv_download(balance_df, 'Download Balance Data (CSV)')
st.markdown(href, unsafe_allow_html=True)

href = df_to_csv_download(transaction_df, 'Download Income and Expenses Data (CSV)')
st.markdown(href, unsafe_allow_html=True)

"""### Key Statistics"""

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

"""### Plots"""

st.plotly_chart(assessment_plot(balance_df), use_container_width=True)
st.plotly_chart(
    income_plot(transaction_df),
    use_container_width=True
)
st.plotly_chart(
    expense_plot(
        transaction_df, [
            transaction_df['age'].min(),
            transaction_df['age'].max(),
        ]),
    use_container_width=True
)

left, right = st.beta_columns(2)
left.plotly_chart(lifetime_expense(transaction_df), use_container_width=True)
right.plotly_chart(lifetime_income(transaction_df), use_container_width=True)

""" Version 0.2 """