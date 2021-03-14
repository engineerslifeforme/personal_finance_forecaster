""" Business logic """
import yaml
import pandas
import plotly.express as px
import plotly
import json

def future_value(investment, rate, periods):
    return investment * (1 + (rate * periods))

def assessment_plot(config_content):
    df = assess(config_content)
    fig = px.bar(df, x='age', y='balance')
    return fig

def assess(config_content):

    config = yaml.load(config_content)
    
    start_age = config['start_age']
    current_age = start_age
    current_month = config['start_month']
    current_year = config['start_year']
    balance = config['start_balance']
    stop_age = config['stop_age']

    balance_list = []

    period_count = 0
    while current_age <= stop_age:
        while current_month <= 12:
            balance += (config['returns'] / 12.0) * balance
            for income in config['income']:
                income_stop_age = income.get('stop_age', stop_age + 1) # default never stop
                if current_age <= income_stop_age:
                    income_amount = future_value(
                        income['amount'],
                        config['inflation'] / 12.0,
                        period_count
                    )
                tax_factor = income.get('tax', 0.0)
                income_amount = income_amount - tax_factor * income_amount
                balance += income_amount
            for expense in config['expenses']:
                expense_stop_age = expense.get('stop_age', stop_age + 1) # default never stop
                expense_start_age = expense.get('start_age', start_age)
                if current_age <= expense_stop_age and current_age >= expense_start_age:
                    inflate = expense.get('inflate', True)
                    expense_amount = expense['amount']
                    if inflate:
                        expense_amount += future_value(
                            expense_amount,
                            config['inflation'] / 12.0,
                            period_count
                        )
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

    return pandas.DataFrame(balance_list)