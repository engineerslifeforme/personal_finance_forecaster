""" Plots for comparison page """

import plotly.express as px

def balance_comparison_plot(balance_df):
    fig = px.line(
        balance_df,
        x='age',
        y='balance',
        color='source',
        title='Balance Comparison Over Time',
    )
    return fig

def income_comparison_plot(transaction_df):
    income = transaction_df[transaction_df['type'] == 'income']
    total_income = income[['age', 'value', 'source']].groupby(['age', 'source']).sum()
    return px.line(
        total_income.reset_index(drop=False), 
        x='age', 
        y='value', 
        color='source',
        title='Income Over Time',
    )

def expense_comparison_plot(transaction_df):
    expenses = transaction_df[transaction_df['type'] == 'expense']
    total_expenses = expenses[['age', 'value', 'source']].groupby(['age', 'source']).sum()
    return px.line(
        total_expenses.reset_index(drop=False), 
        x='age', 
        y='value', 
        color='source',
        title='Expenses Over Time',
    )