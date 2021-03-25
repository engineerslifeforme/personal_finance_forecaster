""" Plots for designer page """

import plotly.express as px
import plotly
import plotly.graph_objects as go
import pandas

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
    income_by_date = transaction_df[transaction_df['type'] == 'income']\
                     .groupby('age')\
                     .sum()\
                     .reset_index(drop=False)
    expenses = transaction_df[transaction_df['type'] == 'expense']
    fig = px.bar(
        expenses, 
        x='age', 
        y='value', 
        color='name',
        title='Expense Over Time',
        facet_row='type',
        range_x=range_x,
    )
    fig.add_trace(
        go.Scatter(
            x=income_by_date['age'].values,
            y=income_by_date['value'].values,
            name='Total Income',
        ))
    return fig

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