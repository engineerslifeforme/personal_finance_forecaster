""" Transaction configuration page """

import itertools

import streamlit as stl

from transactions import Transaction, TransactionEnum

def display_transaction_configuration(st: stl, age_range: list, transaction: Transaction, appreciation_rate: float, defaults: dict = None) -> list:
    if defaults is None:
        default_data = {}
    else:
        default_data = defaults
    
    if transaction.transaction_enum == TransactionEnum.INCOME:
        transaction_label = 'Income'
    elif transaction.transaction_enum == TransactionEnum.EXPENSE:
        transaction_label = 'Expense'
    default_list = default_data.get(transaction.dict_label, [])
    list_length = len(default_list)
    if list_length > 0:
        default_entries = list_length
    else:
        default_entries = 1
    transaction_entries = st.number_input(
        f'{transaction_label} Entries',
        min_value=0,
        value=default_entries,
        help=f"Number of {transaction_label} entries"
    )
    
    transaction_list = []
    for index in range(transaction_entries):
        transaction_instance = transaction(index + 1, appreciation_rate, age_range)
        transaction_list.append(transaction_instance)
        
        try:
            transaction_instance.ingest_dict(default_list[index], age_range)
        # If no defaults, nothing to set
        except IndexError:
            pass
        
        transaction_instance.create_input(st, age_range)

    return transaction_list

        