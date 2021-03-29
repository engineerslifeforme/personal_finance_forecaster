""" Forecast Designer Page """

import base64
from io import StringIO
import copy

import pandas as pd
import yaml
import babel.numbers

from business import (
    assess,
)
from designer_plots import (
    income_plot,
    expense_plot,
    lifetime_expense,
    lifetime_income,
    assessment_plot,
)
from streamlit_support import df_to_csv_download
from constants import AGE_RANGE
from income_editor import income_editor_dialog

def load_forecast_designer(st, session_state, config, configuration_content):
    operation_mode = st.sidebar.radio('Live or Upload', ['Live', 'Upload Previously Saved Forecast'])

    if operation_mode == 'Upload Previously Saved Forecast':
        st.markdown("""**Note**: Switch back to `Live` mode once the upload has completed to edit the forecast.
Changes will be ignored in `Upload` mode.""")
        uploaded_file = st.file_uploader(
            '[OPTIONAL] Configuration Upload', 
            type=['yaml', 'yml', 'txt'],
            help='Upload a saved configuration (.yaml, .yml, and .txt allowed)')

        if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            configuration_content = stringio.read()
            session_state.expenses = yaml.safe_load(configuration_content)

    with st.beta_expander('Personal Notes'):
        st.markdown('You can capture notes on your forecast here.')
        if 'notes' in session_state.expenses:
            default_notes = session_state.expenses['notes']
        else:
            default_notes = ''
        personal_notes = st.text_area(
            'Personal Notes',
            value=default_notes,
        )
        session_state.expenses['notes'] = personal_notes

    view_modes = ['Forecast Configuration', 'Income', 'Expenses', 'Results', '[Advanced] YAML Editor']
    view_mode = st.sidebar.radio(
        'View Mode',
        options=view_modes
    )

    configuration_edit = None
    balance_df = None
    transaction_df = None
    if view_mode == view_modes[4]:
        """[Documentation](https://personal-finance-forecaster.readthedocs.io/en/latest/)"""

        configuration_edit = st.text_area(
            'Configuration Editor',
            value=configuration_content,
            height=300,
        )
        session_state.expenses = yaml.safe_load(configuration_edit)

    elif view_mode == view_modes[0]:
        selected_age_range = st.slider(
            'Age Range (Years)', 
            min_value=AGE_RANGE[0],
            max_value=AGE_RANGE[1],
            value=(session_state.expenses['start_age'],session_state.expenses['stop_age']),
            step=1,
        )
        session_state.expenses['start_age'] = int(selected_age_range[0])
        session_state.expenses['stop_age'] = int(selected_age_range[1])
        session_state.expenses['inflation'] = (st.slider(
            'Inflation (%)',
            min_value=0.0,
            max_value=10.0,
            value=session_state.expenses['inflation']*100.0,
            step=0.1,
        ))/100.0
        session_state.expenses['returns'] = (st.slider(
            'Appreciation (%)',
            min_value=0.0,
            max_value=20.0,
            value=session_state.expenses['returns']*100.0,
            step=0.1,
        ))/100.0
        session_state.expenses['start_year'] = st.slider(
            'Start Year',
            min_value=2021,
            max_value=2121,
            step=1,
            value=session_state.expenses['start_year'],
        )
        session_state.expenses['start_month'] = st.slider(
            'Start Month',
            min_value=1,
            max_value=12,
            value=session_state.expenses['start_month'],
            step=1,
        )
        session_state.expenses['start_balance'] = st.number_input(
            'Starting Balance',
            value=session_state.expenses['start_balance']
        )

    elif view_mode == view_modes[1]:
        st.markdown('## Income Sources')
        st.markdown('Use the `New Income` input and `Add New Income` button in the sidbar to add another Income.')
        if st.checkbox('Delete An Income Source?'):
            left, right, = st.beta_columns((3,1))
            delete_income_name = left.selectbox('Income Name', options=list(session_state.expenses['income'].keys()))
            if right.button('Delete', key='delete_income'):
                session_state.expenses['income'].pop(delete_income_name, None)
        st.markdown('### Income List')
        income_dict = copy.deepcopy(session_state.expenses['income'])
        session_state.expenses['income'].clear()
        for index, item_key in enumerate(income_dict):
            item = income_dict[item_key]
            include, name, new_item = income_editor_dialog(
                st, 
                index,
                item_key, 
                item,
                session_state.expenses['start_age'],
            )
            if include:
                session_state.expenses['income'][name] = new_item
            
        new_name = st.sidebar.text_input('New Income', value='Income Name')
        if st.sidebar.button('Add New Income'):
            include, name, new_item = income_editor_dialog(
                st, 
                index+1,
                new_name, 
                {
                    'amount': 0.0
                },
                session_state.expenses['start_age'],
                new=True,
            )
            if include:
                session_state.expenses['income'][name] = new_item

    elif view_mode == view_modes[2]:  
        st.markdown('## Expense Sources')  
        st.markdown('Use the `New Expense` input and `Add New Expenses` button in the sidbar to add another Expense.')
        if st.checkbox('Delete An Expense Source?'):
            left, right, = st.beta_columns((3,1))
            delete_income_name = left.selectbox('Expense Name', options=list(session_state.expenses['expenses'].keys()))
            if right.button('Delete', key='delete_expense'):
                session_state.expenses['expenses'].pop(delete_income_name, None)
        st.markdown('### Expense List')
        expenses_dict = copy.deepcopy(session_state.expenses['expenses'])
        session_state.expenses['expenses'].clear()
        for index, item_key in enumerate(expenses_dict):
            item = expenses_dict[item_key]
            include, name, new_item = income_editor_dialog(
                st, 
                index,
                item_key, 
                item,
                session_state.expenses['start_age'],
                i_or_e='Expense',
                tax=False,
                inflate=True,
            )
            if include:
                session_state.expenses['expenses'][name] = new_item
            
        new_name = st.sidebar.text_input('New Expense', value='Expense Name')
        if st.sidebar.button('Add New Expenses'):
            include, name, new_item = income_editor_dialog(
                st, 
                index+1,
                new_name, 
                {
                    'amount': 0.0
                },
                session_state.expenses['start_age'],
                i_or_e='Expense',
                new=True,
                tax=False,
                inflate=True,
            )
            if include:
                session_state.expenses['expenses'][name] = new_item

    elif view_mode == view_modes[3]:
        temp_ss = copy.deepcopy(session_state.expenses)

        with st.beta_expander('Adjust Fields'):
            st.markdown("""These fields will allow working through possibilities, but
they are not captured in the forecast that is saved.  Any changes you wish to be
captured in the saved forecast must be made above.  Changes here will result in
changes in the charts below and the summary at the top.""")
            adjust_quantity = st.number_input('Adjustment Fields', value=1)
            for adjustment_index in range(adjust_quantity):
                left, middle_left, middle_right, right = st.beta_columns(4)
                income_or_expense = left.radio(
                    'Type', 
                    options=['income', 'expenses'],
                    key=f'adjustment_type_{adjustment_index}'
                )
                item_name_options = [item_name for item_name in temp_ss[income_or_expense]]
                item_names = middle_left.multiselect(
                    'Item Name', 
                    options=item_name_options,
                    key=f'items_{adjustment_index}'
                )
                field_name = middle_right.selectbox(
                    'Value', 
                    options=['stop_age', 'start_age', 'amount'],
                    key=f'adjustment_value_{adjustment_index}'
                )
                if len(item_names) > 0:
                    # Default to first selected item
                    try:
                        default_adjust_value = temp_ss[income_or_expense][item_names[0]][field_name]
                    except KeyError:
                        default_adjust_value = 0    
                else:
                    default_adjust_value = 0
                new_value = right.number_input(
                    field_name, 
                    value=default_adjust_value,
                    key=f'new_adjustment_value_{adjustment_index}'
                )
                for item_name in item_names:
                    temp_ss[income_or_expense][item_name][field_name] = new_value
            
        
        """ # Results """
        st.sidebar.markdown('Results')
        balance_df, transaction_df, configuration = assess(temp_ss)
        st.markdown('### Key Statistics')
        ending_balance = balance_df['balance'].values[-1]
        ending_balance_str = babel.numbers.format_currency(ending_balance, 'USD', locale='en_US')
        st.markdown(f"Ending Balance: {ending_balance_str}")
        if st.checkbox('Display Plots (Slower)'):
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

    if balance_df is None:
        balance_df, transaction_df, config = assess(session_state.expenses)

    ending_balance = balance_df['balance'].values[-1]
    ending_balance_str = babel.numbers.format_currency(ending_balance, 'USD', locale='en_US')

    st.sidebar.write(f"Ending Balance: {ending_balance_str}")
    
    if configuration_edit is None:
        configuration_edit = yaml.safe_dump(session_state.expenses)
    #https://raw.githubusercontent.com/MarcSkovMadsen/awesome-streamlit/master/gallery/file_download/file_download.py
    b64 = base64.b64encode(configuration_edit.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/yaml;base64,{b64}">Download Forecast File</a> (right-click and save as &lt;configuration&gt;.yaml)'
    st.sidebar.markdown(href, unsafe_allow_html=True)    

    href = df_to_csv_download(balance_df, 'Download Balance Data (CSV)')
    st.sidebar.markdown(href, unsafe_allow_html=True)

    href = df_to_csv_download(transaction_df, 'Download Income and Expenses Data (CSV)')
    st.sidebar.markdown(href, unsafe_allow_html=True)
