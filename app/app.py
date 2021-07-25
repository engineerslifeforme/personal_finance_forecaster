""" Streamlit app for personal finance forecast """

from enum import Enum
from io import StringIO
import base64

import streamlit as st
import plotly.express as px
import pandas as pd
import yaml

from forecast_configuration_page import display_forecast_configuration
from transaction_configuration import display_transaction_configuration
from transactions import Income, Expense
from forecast import compute_forecast
from yaml_editor import yaml_configuration, load_yaml_file
from streamlit_support import df_to_csv_download

class EditMode(Enum):
    GUI = 0
    YAML = 1

st.set_page_config(layout='wide')

st.sidebar.markdown("""# Instructions

1. Configure over all parameters in `Forecast Configuration`
2. Configure income sources in `Income Configuration`
3. Configure expense sources in `Expense Configuration`
""")
edit_modes = [
    'GUI',
    'YAML (Advanced)'
]
edit_mode_str = st.sidebar.radio(
    'Mode',
    edit_modes,
)
edit_mode = EditMode(edit_modes.index(edit_mode_str))
uploaded_files = st.file_uploader(
    'Configurations to Compare Upload', 
    type=['yaml', 'yml', 'txt'],
    help='Upload saved configurations (.yaml, .yml, and .txt allowed)',
    accept_multiple_files=True,
)
default_configuration_content = None
for uploaded_file in uploaded_files:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    default_configuration_content = stringio.read()
    

if edit_mode == EditMode.GUI:
    try:
        default_configuration = load_yaml_file(default_configuration_content)
    # None will have no read, AttributeError
    except AttributeError:
        default_configuration = {}
    forecast_configuration = st.beta_expander(label='Forecast Configuration')
    with forecast_configuration:
        configuration = display_forecast_configuration(st, defaults=default_configuration)

    age_range = [
        configuration['start_age'],
        configuration['stop_age'],
    ]
    inflation_rate = configuration['inflation']

    income_configuration = st.beta_expander(label='Income Configuration')
    with income_configuration:
        income_list = display_transaction_configuration(
            st, 
            age_range, 
            Income, 
            inflation_rate,
            defaults=default_configuration,
        )

    expense_configuration = st.beta_expander(label='Expense Configuration')
    with expense_configuration:
        expense_list = display_transaction_configuration(
            st, 
            age_range, 
            Expense,
            inflation_rate,
            defaults=default_configuration,
        )

    configuration['income'] = [income.output_as_dict() for income in income_list]
    configuration['expenses'] = [expense.output_as_dict() for expense in expense_list]
    configuration_str = yaml.safe_dump(configuration)

elif edit_mode == EditMode.YAML:
    configuration, income_list, expense_list, configuration_str = yaml_configuration(
        st,
        default_configuration_content=default_configuration_content,
    )

st.write(f'{len(income_list)} Incomes Defined')
st.write(f'{len(expense_list)} Expenses Defined')

final_balance, transaction_log = compute_forecast(
    configuration,
    income_list,
    expense_list,
)
transaction_log['cumsum'] = transaction_log['value'].cumsum()
st.write('Final Balance: ${:,.2f}'.format(final_balance))

#https://raw.githubusercontent.com/MarcSkovMadsen/awesome-streamlit/master/gallery/file_download/file_download.py
b64 = base64.b64encode(configuration_str.encode()).decode()  # some strings <-> bytes conversions necessary here
href = f'<a href="data:file/yaml;base64,{b64}">Download Forecast File</a> (right-click and save as &lt;configuration&gt;.yaml)'
st.markdown(href, unsafe_allow_html=True)

href = df_to_csv_download(transaction_log, 'Download Transaction Data (CSV)')
st.markdown(href, unsafe_allow_html=True)

plots = st.beta_expander(label='Plots')
with plots:
    st.markdown('# Plots')
    balance_df = pd.DataFrame(transaction_log.groupby(['age'], sort=False)['cumsum'].max()).reset_index()
    st.plotly_chart(
        px.bar(balance_df, x='age', y='cumsum', title='Balance')
    )
    st.plotly_chart(
        px.bar(transaction_log, x='age', y='value', color='type', title='Income vs Expense')
    )
    st.plotly_chart(
        px.bar(
            transaction_log[transaction_log['type'] == 'Income'], 
            x='age', 
            y='value', 
            color='name',
            title='Income Breakdown'
        )
    )
    st.plotly_chart(
        px.bar(
            transaction_log[transaction_log['type'] == 'Expense'], 
            x='age', 
            y='value', 
            color='name',
            title='Expense Breakdown'
        )
    )