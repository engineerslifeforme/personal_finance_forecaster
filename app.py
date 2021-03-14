import datetime
import io
import base64

import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_html_components as html
import dash_core_components as dcc

from business import assessment_plot

app = dash.Dash(__name__)

server = app.server

with open('default.yaml', 'r') as fh:
    configuration_content = fh.read()

app.layout = html.Div([
    html.H1(
        children='Personal Finance Forcaster',
        style={'textAlign': 'center'}
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
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
        figure=assessment_plot(configuration_content),
    )
])

@app.callback(
    Output('graph', 'figure'),
    [Input('my-button-events-example', 'n_clicks')],
    state=[State('textarea-example', 'value')]
)
def update_output(n_clicks, value):
    return assessment_plot(value)

def parse_contents(contents):
    """
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
    if contents is not None:
        children = parse_contents(contents)
        return children

if __name__ == '__main__':
    app.run_server(debug=True)