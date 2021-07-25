""" Forecast calculation """

from decimal import Decimal

import pandas as pd

def compute_start_and_end(start_age: int, stop_age: int, start_year: int, start_month: int):
    start = start_year * 12 + (start_month - 1)
    stop = ((stop_age - start_age) * 12) + start
    return (start, stop)

def compute_forecast(configuration: dict, incomes: list, expenses: list):
    balance = configuration['start_balance']
    start_age = configuration['start_age']
    start, stop = compute_start_and_end(
        start_age,
        configuration['stop_age'],
        configuration['start_year'],
        configuration['start_month']
    )

    monthly_return_rate = configuration['returns'] / 12.0
    current_period = start
    current_age = start_age
    period_difference = 0
    transaction_log = []
    while current_period <= stop:
        precise_age = current_age + ((period_difference%12)/12.0)
        interest = balance * monthly_return_rate
        balance += interest
        transaction_log.append({
            'age': precise_age,
            'value': interest,
            'name': 'INTEREST',
            'type': 'Income',
        })


        for transaction_list in [incomes, expenses]:
            for transaction in transaction_list:
                transaction_value = transaction.get_value(
                    (current_period - start),
                    current_age
                )
                balance += transaction_value
                transaction_log.append({
                    'age': precise_age,
                    'value': transaction_value,
                    'name': transaction.name,
                    'type': transaction.transaction_type,
                })

        current_period += 1
        period_difference = current_period - start
        if (period_difference % 12) == 0:
            current_age += 1

    return Decimal(balance), pd.DataFrame(transaction_log)