""" Business logic """
import yaml
import pandas
import json

def future_value(investment, rate, periods):
    """ Compute future value

    :param investment: base amount
    :type investment: decimal
    :param rate: rate of change per period
    :type rate: decimal
    :param periods: number of periods into future
    :type periods: int
    :return: new future value
    :rtype: decimal

    https://www.investopedia.com/terms/f/futurevalue.asp#:~:text=Future%20value%20(FV)%20is%20the,be%20worth%20in%20the%20future.
    """
    return investment * (1 + (rate * periods))

def create_transaction(amount, meta_list=None):
    item = {'value': amount}
    for meta in meta_list:
        for key in meta:
            item[key] = meta[key]
    return item

def assess(config):
    """ Run forecast over time according to config

    :param config_content: YAML configuration
    :type config_content: str
    :return: forecast dataframe
    :rtype: pandas dataframe
    """

    #config = yaml.load(config_content, Loader=yaml.SafeLoader)
    
    start_age = config['start_age']
    current_age = start_age
    current_month = config['start_month']
    current_year = config['start_year']
    balance = config['start_balance']
    stop_age = config['stop_age']

    balance_list = []
    transaction_list = []

    period_count = 0
    while current_age <= stop_age:
        while current_month <= 12:
            precise_age = current_age + (current_month - 1) / 12.0
            time_meta = {
                'age': current_age + (current_month - 1) / 12.0,
                'year': current_year,
                'month': current_month,
                'period': period_count,
            }
            appreciation = (config['returns'] / 12.0) * balance
            transaction_list.append(create_transaction(appreciation, [
                time_meta,
                {'name': 'balance_appreciation', 'type': 'income'}
            ]))
            balance += appreciation
            if 'income' in config:
                for income_name in config['income']:
                    income = config['income'][income_name]
                    income_stop_age = income.get('stop_age', stop_age + 1) # default never stop
                    if current_age <= income_stop_age:
                        income_amount = future_value(
                            income['amount'],
                            config['inflation'] / 12.0,
                            period_count
                        )
                        transaction_list.append(create_transaction(income_amount, [
                            time_meta,
                            {'name': income_name, 'type': 'income'}
                        ]))
                        tax = income.get('tax', 0.0) * income_amount
                        if tax > 0.0:
                            transaction_list.append(create_transaction(tax, [
                                time_meta,
                                {'name': income_name+'_tax', 'type': 'expense'}
                            ]))
                            income_amount = income_amount - tax
                        balance += income_amount
            if 'expenses' in config:
                for expense_name in config['expenses']:
                    expense = config['expenses'][expense_name]
                    expense_stop_age = expense.get('stop_age', stop_age + 1) # default never stop
                    expense_start_age = expense.get('start_age', start_age)
                    record_transaction = True
                    if 'one_time' in expense:
                        if expense['one_time'] != precise_age:
                            record_transaction = False        
                    else:
                        if current_age <= expense_stop_age and current_age >= expense_start_age:
                            pass
                        else:
                            record_transaction = False
                    inflate = expense.get('inflate', True)
                    expense_amount = expense['amount']
                    if inflate:
                        expense_amount = future_value(
                            expense_amount,
                            config['inflation'] / 12.0,
                            period_count
                        )
                    if record_transaction:
                        transaction_list.append(create_transaction(expense_amount, [
                            time_meta,
                            {'name': expense_name, 'type': 'expense'}
                        ]))
                        balance -= expense_amount
            if 'assets' in config:
                pass
            balance_list.append({
                'balance': balance,
                'date': '{}-{}'.format(current_year, current_month),
                'age': precise_age,
            })
            current_month += 1
            period_count += 1
        current_month = 1
        current_age += 1
        current_year += 1

    return pandas.DataFrame(balance_list), pandas.DataFrame(transaction_list), config