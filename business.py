""" Business logic """
import yaml
import pandas
import plotly.express as px
import plotly
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

def assessment_plot(balance_df):
    # TODO: Change this to use transaction_df
    return px.bar(
        balance_df, 
        x='age', 
        y='balance',
        title='Balance Over Time',
    )

def income_plot(transaction_df):
    income = transaction_df[transaction_df['type'] == 'income']
    return px.bar(
        income, 
        x='age', 
        y='value', 
        color='name',
        title='Income Over Time'
    )

def expense_plot(transaction_df, range_x):
    # Plot the expense as positive
    return px.bar(
        transaction_df[transaction_df['type'] == 'expense'], 
        x='age', 
        y='value', 
        color='name',
        title='Expense Over Time',
        facet_row='type',
        range_x=range_x,
    )

def lifetime_expense(transaction_df):
    expense = transaction_df[transaction_df['type'] == 'expense']
    gb = expense.groupby('name')
    sum_by_type = pandas.DataFrame(gb.sum()['value']).reset_index(drop=False)
    return px.pie(
        sum_by_type, 
        names='name', 
        values='value',
        title='Life Expense Totals',
    )

def lifetime_income(transaction_df):
    income = transaction_df[transaction_df['type'] == 'income']
    gb = income.groupby('name')
    sum_by_type = pandas.DataFrame(gb.sum()['value']).reset_index(drop=False)
    return px.pie(
        sum_by_type, 
        names='name', 
        values='value',
        title='Lifetime Income Totals',
    )

def create_transaction(amount, meta_list=None):
    item = {'value': amount}
    for meta in meta_list:
        for key in meta:
            item[key] = meta[key]
    return item

def assess(config_content):
    """ Run forecast over time according to config

    :param config_content: YAML configuration
    :type config_content: str
    :return: forecast dataframe
    :rtype: pandas dataframe
    """

    config = yaml.load(config_content, Loader=yaml.SafeLoader)
    
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
            for income in config['income']:
                income_stop_age = income.get('stop_age', stop_age + 1) # default never stop
                if current_age <= income_stop_age:
                    income_amount = future_value(
                        income['amount'],
                        config['inflation'] / 12.0,
                        period_count
                    )
                    transaction_list.append(create_transaction(income_amount, [
                        time_meta,
                        {'name': income['name'], 'type': 'income'}
                    ]))
                    tax = income.get('tax', 0.0) * income_amount
                    transaction_list.append(create_transaction(tax, [
                        time_meta,
                        {'name': income['name']+'_tax', 'type': 'expense'}
                    ]))
                    income_amount = income_amount - tax
                    balance += income_amount
            for expense in config['expenses']:
                expense_stop_age = expense.get('stop_age', stop_age + 1) # default never stop
                expense_start_age = expense.get('start_age', start_age)
                if current_age <= expense_stop_age and current_age >= expense_start_age:
                    inflate = expense.get('inflate', True)
                    expense_amount = expense['amount']
                    if inflate:
                        expense_amount = future_value(
                            expense_amount,
                            config['inflation'] / 12.0,
                            period_count
                        )
                    transaction_list.append(create_transaction(expense_amount, [
                        time_meta,
                        {'name': expense['name'], 'type': 'expense'}
                    ]))
                    balance -= expense_amount
            balance_list.append({
                'balance': balance,
                'date': '{}-{}'.format(current_year, current_month),
                'age': current_age + (current_month - 1) / 12.0,
            })
            current_month += 1
            period_count += 1
        current_month = 1
        current_age += 1
        current_year += 1

    return pandas.DataFrame(balance_list), pandas.DataFrame(transaction_list), config