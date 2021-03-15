import datetime
import io
import base64

import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_html_components as html
import dash_core_components as dcc

from business import (
    assessment_plot, 
    assess,
    income_plot,
    expense_plot,
    lifetime_expense,
    lifetime_income,
)

app = dash.Dash(__name__)

server = app.server

with open('default.yaml', 'r') as fh:
    configuration_content = fh.read()

balance_df, transaction_df, config = assess(configuration_content)

app.layout = html.Div([
    html.H1(
        children='Personal Finance Forcaster',
        style={'textAlign': 'center'}
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Saved Config File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.A(
        children='Documentation',
        href='https://personal-finance-forecaster.readthedocs.io/en/latest/'
    ),
    html.Div(id='output-data-upload'),
    dcc.Textarea(
        id='textarea-example',
        value=configuration_content,
        style={'width': '100%', 'height': 300},
    ),
    html.Button('Update Graph', id='my-button-events-example'),
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'}),
    dcc.Graph(
        id='graph',
        figure=assessment_plot(balance_df),
    ),
    dcc.Graph(
        id='income_graph',
        figure=income_plot(transaction_df)
    ),
    dcc.Graph(
        id='expense_graph',
        figure=expense_plot(transaction_df, [
            transaction_df['age'].min(),
            transaction_df['age'].max(),
        ])
    ),
    dcc.Graph(
        id='lifetime_expenses',
        figure=lifetime_expense(transaction_df)
    ),
    dcc.Graph(
        id='lifetime_income',
        figure=lifetime_income(transaction_df),
    )
])

@app.callback(
    [
        Output('graph', 'figure'),
        Output('income_graph', 'figure'),
        Output('expense_graph', 'figure'),
        Output('lifetime_expenses', 'figure'),
        Output('lifetime_income', 'figure'),
    ],
    [Input('my-button-events-example', 'n_clicks')],
    [State('textarea-example', 'value')]
)
def update_output(n_clicks, value):
    """ Update plots when update graph is clicked

    :param n_clicks: number of times update has been clicked
    :type n_clicks: int
    :param value: configuration contents
    :type value: str
    :return: new plot
    :rtype: plotly figure
    """
    balance_df, transaction_df, config = assess(value)
    #transaction_df.to_csv('transaction.csv')
    plots = (
        assessment_plot(balance_df), 
        income_plot(transaction_df),
        expense_plot(transaction_df, [
            transaction_df['age'].min(),
            transaction_df['age'].max(),
        ]),
        lifetime_expense(transaction_df),
        lifetime_income(transaction_df),
    )
    return plots

def parse_contents(contents):
    """ Parse textarea contents

    :param contents: contents of text area, base64 encoded
    :type contents: str
    :return: decoded string
    :rtype: str

    https://dash.plotly.com/dash-core-components/upload
    """
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    return decoded.decode('utf-8')

@app.callback(
    Output('textarea-example', 'value'),
    [Input('upload-data', 'contents')],
)
def update_upload_output(contents):
    """ Replace configuration with uploaded content

    :param contents: base64 encoded content from textarea
    :type contents: str
    :return: New config content
    :rtype: str
    """
    if contents is not None:
        children = parse_contents(contents)
        return children

if __name__ == '__main__':
    app.run_server(debug=True)