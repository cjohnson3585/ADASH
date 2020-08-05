import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf
from astropy.timeseries import LombScargle
import astropy.units as u
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
    html.H1(children='Astronomer Dashboard (ADASH)',style={
            'textAlign': 'center',
        }),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '20%',
            'height': '50px',
            'lineHeight': '60px',
            'borderWidth': '10px',
            'borderStyle': 'dashed',
            'borderRadius': '1px',
            'textAlign': 'center',
            'margin': '5px',
            'display': 'inline-block'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(["Period: ",dcc.Input(id='my-input-period', value='1.0', type='number', style={'width': '30%', 'display': 'inline-block'})]),
    html.Div(["T0: ",dcc.Input(id='my-input-t0', value='0.0', type='number',style={'width': '25%', 'display': 'inline-block'})]),
    html.Div(["Best Period: ",dcc.Input(id='my-input-bf', value='0.0', type='number',style={'width': '25%', 'display': 'inline-block'})]),
#    html.Div(id='my-output-period',style={'display': 'none'}),
    html.Div(id='my-output-t0',style={'display': 'none'}),
    html.Div(id='my-output-period',style={'display': 'none'}),
    html.Div(id='hidden-value', style={'display': 'none'}),
    html.Hr(),
    html.Hr(),
    html.Div(dcc.Graph(id='Mygraph'),style={'width': '33%', 'display': 'inline-block'}),
    html.Div(dcc.Graph(id='LombScargle'),style={'width': '33%', 'display': 'inline-block'}),
    html.Div(dcc.Graph(id='Mygraph2'),style={'width': '33%', 'display': 'inline-block'}),
    html.Div(html.Div(id='my-output-bf',style={'position': 'absolute','left': '45%','bottom': '50%'})),
    html.Hr(),
    html.Hr(),
    html.Div(id='output-data-upload',style={'width': '33%', 'display': 'inline-block'}),
    html.Div(id='output-data-phase-fold',style={'width': '33%', 'display': 'inline-block'}),
])

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df


###Callbacks
@app.callback(
    Output(component_id='my-output-period', component_property='children'),
    [Input(component_id='my-input-period', component_property='value')]
)
def update_output_div(input_value):
    if input_value == None:
        input_value = 1.0
    return 'Output: {}'.format(input_value)

@app.callback(
    Output(component_id='my-output-t0', component_property='children'),
    [Input(component_id='my-input-t0', component_property='value')]
)
def update_output_div(input_value):
    if input_value == None:
        input_value = 0.0
    return 'Output: {}'.format(input_value)



###Graph Callbacks
@app.callback(Output('Mygraph', 'figure'),#Light Curve
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
            ])
def update_graph(contents, filename):
    x    = [];y    = [];xx=[];yy=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        x    = df[df.columns[0]]
        y    = df[df.columns[1]]
        yerr = df[df.columns[2]]
        x = np.asarray(x);y = np.asarray(y);yerr = np.asarray(yerr)
        ind = np.argsort(x)
        xx=x[ind];yy=y[ind];yyerr = yerr[ind]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=xx, 
                y=yy, 
                mode='lines+markers',
                marker=dict(color=[1]),
                line=dict(color='black')
                ),
            ],
        layout=go.Layout(
            title="Light Curve",
            xaxis=dict(title="DATE"),
            yaxis=dict(title="MAG") 
                        ) 
                    )
    fig['layout']['yaxis']['autorange'] = "reversed"
    return fig


@app.callback(Output('LombScargle', 'figure'),#Lomb-Scargle Plot
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('my-input-t0', 'value'),
                Input('my-input-period', 'value'),
            ])
def update_graph(contents, filename, tnot, period):
    x = [];y = [];frequency=[];power=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        x    = df[df.columns[0]]
        x = np.asarray(x)
        y    = df[df.columns[1]]
        y = np.asarray(y)
        yerr = df[df.columns[2]]
        yerr = np.asarray(yerr)
        t_days = x * u.day
        y_mags = y * u.mag
        dy_mags = yerr * u.mag
        frequency, power = LombScargle(t_days, y_mags, dy_mags).autopower(nyquist_factor=10)
        bf = 1.0/frequency[np.argmax(power)]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=frequency, 
                y=power, 
                mode='lines+markers',
                marker=dict(color=[1])
                ),
            ],
        layout=go.Layout(
            title="Lomb-Scargle Periodogram",
            xaxis=dict(title="FREQUENCY"),
            yaxis=dict(title="POWER") 
                        ) 
                    )
    return fig


@app.callback(Output('Mygraph2', 'figure'),#Phase-Folded Light Curve
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('my-input-t0', 'value'),
                Input('my-input-period', 'value'),
                Input('my-output-bf', 'children')
            ])
def update_graph(contents, filename, tnot, period, bf):
    xstack=[];ystack=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        bbf = bf.split(' ')
        per = float(bbf[2])
        try:
            period   = float(per)
        except:
            period   = 1.0
        try:
            tnot     = float(tnot)
        except:
            tnot     = 0.0
        df = parse_data(contents, filename)
        tt    = np.asarray(df[df.columns[0]])
        x    = ((tt-tnot)/period)%1
        y    = df[df.columns[1]]
        yerr = df[df.columns[2]]
        x = np.asarray(x);y = np.asarray(y);yerr = np.asarray(yerr)
        ind = np.argsort(x)
        xx=x[ind];yy=y[ind];yyerr = yerr[ind]
        xxx = xx + 1.0
        xstack = np.hstack((xx,xxx))
        ystack = np.hstack((yy,yy))
    fig = go.Figure(
        data=[
            go.Scatter(
                x=xstack, 
                y=ystack, 
                mode='lines+markers',
                marker=dict(color=[1])
                ),
            ],
        layout=go.Layout(
            title="Phase-Folded Light Curve",
            xaxis=dict(title="PHASE"),
            yaxis=dict(title="MAG") 
                        ) 
                    )
    fig['layout']['yaxis']['autorange'] = "reversed"
    return fig


@app.callback([
                Output('hidden-value', 'children'),
                Output('my-output-bf', 'children'),
            ],
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
            ])
def update_hidden(contents, filename):
    x = [];y = [];xx = [];yy = [];xxx = [];yyy = [];frequency=[];power=[];bf=1.0
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        x    = df[df.columns[0]]
        x = np.asarray(x)
        y    = df[df.columns[1]]
        y = np.asarray(y)
        yerr = df[df.columns[2]]
        yerr = np.asarray(yerr)
        t_days = x * u.day
        y_mags = y * u.mag
        dy_mags = yerr * u.mag
        frequency, power = LombScargle(t_days, y_mags, dy_mags).autopower(nyquist_factor=10)
        bf = 1.0/frequency[np.argmax(power)]
    return "Best Period: "+str(bf),"Best Period: "+str(bf)


###Table Callbacks
@app.callback(Output('output-data-upload', 'children'),#Uploaded File Table
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                style_table={'height': 500,'overflowY': 'scroll','width': 500},
                style_header={'backgroundColor': 'white','fontWeight': 'bold'},
                style_cell_conditional=[
                    {'if': {'column_id': 'TIME'},
                        'width': '1%','textAlign':'left'},
                    {'if': {'column_id': 'MAG'},
                        'width': '1%','textAlign':'left'},
                    {'if': {'column_id': 'MERR'},
                        'width': '1%','textAlign':'left'},
                                        ]
            ),
        ])

    return table

@app.callback(Output('output-data-phase-fold', 'children'),#Phase-Folded Data Table
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('my-input-t0', 'value'),
                Input('my-input-period', 'value')
            ])
def update_table(contents, filename, tnot, period):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        period = period
        tnot = tnot
        try:
            period   = float(period)
        except:
            period   = 1.0
        try:
            tnot     = float(tnot)
        except:
            tnot     = 0.0
        df = parse_data(contents, filename)
        x    = ((df[df.columns[0]]-tnot)/period)%1
        xx   = x + 1.0
        y    = df[df.columns[1]]
        yy   = y
        yerr = df[df.columns[2]]
        x = np.asarray(x);y = np.asarray(y);yerr = np.asarray(yerr)
        d = {'PHASE': x, 'MAG': y, 'MERR':yerr}
        df_phase = pd.DataFrame(data=d,index=None)
        table = html.Div([
            html.H5(filename + ' Phase-Fold'),
            dash_table.DataTable(
                data=df_phase.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df_phase.columns],
                style_table={'height': 500,'overflowY': 'scroll','width': 500},
                style_header={'backgroundColor': 'white','fontWeight': 'bold'},
                style_cell_conditional=[
                    {'if': {'column_id': 'PHASE'},
                        'width': '1%','textAlign':'left'},
                    {'if': {'column_id': 'MAG'},
                        'width': '1%','textAlign':'left'},
                    {'if': {'column_id': 'MERR'},
                        'width': '1%','textAlign':'left'},
                                        ]
            ),
        ])

    return table




if __name__ == '__main__':
    app.run_server(debug=True)