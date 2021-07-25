""" Editor for YAML mode """

import streamlit as stl
import yaml
from jinja2 import Environment

from transactions import Income, Expense

def load_yaml_file(yaml_content:str) -> dict:
    split_content = yaml_content.split('---')
    if len(split_content) > 1:
        constants = yaml.safe_load(split_content[0])
        configuration = yaml.safe_load(Environment().from_string(split_content[1]).render(**constants))
    else:
        configuration = yaml.safe_load(yaml_content)
    return configuration

def yaml_configuration(st: stl, default_configuration_content: str = None):
    st.markdown('**Note:** Switching between GUI and YAML will erase changes in YAML editor.')
    st.markdown('To transition a forecast from GUI to YAML, download the forecast and upload it in YAML mode.')
    if default_configuration_content is None:
        with open('example.yml', 'r') as fh:
            default_configuration_content = fh.read()
    yaml_content = st.text_area(
        'YAML Editing',
        value = default_configuration_content,
        height=200,
    )
    configuration = load_yaml_file(yaml_content)

    income_list = []
    expense_list = []
    for transaction_class, transaction_list in [
        (Income, income_list), 
        (Expense, expense_list),
        ]:
        for index, transaction in enumerate(configuration[transaction_class.dict_label]):
            age_range = [configuration['start_age'], configuration['stop_age']]
            new_transaction = transaction_class(index, configuration['inflation'], age_range)
            new_transaction.ingest_dict(
                transaction,
                age_range,
            )
            transaction_list.append(new_transaction)    

    return configuration, income_list, expense_list, yaml_content