import base64
import os
import urllib
import warnings
import dash
import time
import pandas as pd
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf
from astropy.timeseries import LombScargle
import astropy.units as u
import numpy as np
import dash_core_components as dcc
import dash_table
import json
import app_builders as ab

warnings.filterwarnings("ignore")


FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    style={
        'background': ab.colors['main_background'],
        'width': '100%',
    },
    children=[
        dbc.Col([
            html.Br([]),
            ab.build_top_banner(),

            # Main Control Area
            ab.lc_collapsible_div(ab.lc_build_control_area(), "Light Curve Generator"),
            ab.bs_collapsible_div(ab.bs_build_control_area(), "Brigh Star Catalogue Generator"),

            # Main Display Area
            #ab.build_main_content_page(),
            html.Br([]),

            # Hidden Divs - used to store things without showing them
            html.Div(id='current-directory-path', style=ab.hidden_style, ),
            html.Div(id='my-output-t0',style=ab.hidden_style),
            html.Div(id='my-output-period',style=ab.hidden_style),
            html.Div(id='hidden-value', style=ab.hidden_style),

#            html.Div(id='upload-status', style=ab.hidden_style, ),
#            html.Div(id='process-status', style=ab.hidden_style, ),
#            html.Div(id='scraped-status', style=ab.hidden_style, ),

#            html.Div(id='total-files-detected', style=ab.hidden_style, ),
#            html.Div(id='total-files-successful', style=ab.hidden_style, ),

#            html.Div(id='updated-table-input', style=ab.hidden_style, ),
#            html.Div(id='updated-table-scraped', style=ab.hidden_style, ),
#            html.Div(id='scraped-copy', style=ab.hidden_style, ),
        ])
    ])


#
# ------------- Callbacks: -------------
#
# ------------ PROGRESS OUTPUT SECTION ------------
'''
@app.callback(
    Output('upload-status', "children"),
    [Input('current-directory-path', "children")],
)
def update_upload_status(file_path):
    if file_path is not None:
        return 'Uploaded'


@app.callback(
    Output('process-status', "children"),
    [Input('current-table', "children")],
)
def update_process_status(df_table):
    if df_table is not None:
        return 'Processed'


@app.callback(
    Output('upload-progress-message', "children"),
    [Input("lc_upload-data", "contents"),
     Input('current-directory-path', "children")]
)
def update_upload_progress_message(list_of_contents, file_path):
    return_text = "STEP 1 - Data Upload:"
    if list_of_contents is None:
        return f"{return_text} Pending"
    elif list_of_contents is not None and file_path is not None:
        return f"{return_text} Completed"
    else:
        return f"{return_text} In Progress"


@app.callback(
    Output('process-progress-message', "children"),
    [Input('process-status', "children"),
     Input('upload-status', "children")],
)
def update_process_progress_message(process_status, upload_status):
    return_text = "STEP 2 - Data Processing:"
    if process_status is None and upload_status is None:
        return f"{return_text} Pending/Processing"
    elif process_status is not None and upload_status is not None:
        return f"{return_text} Completed"
    else:
        return f"{return_text} Processing"
'''

#
# ------------ MAIN OUTPUT SECTION ------------
#
@app.callback(
    Output(component_id='my-output-period', component_property='children'),
    [Input(component_id='my-input-period', component_property='value')])

def update_output_div(input_value):
    if input_value == None:
        input_value = 1.0
    return 'Output: {}'.format(input_value)

@app.callback(
    Output(component_id='my-output-t0', component_property='children'),
    [Input(component_id='my-input-t0', component_property='value')])

def update_output_div(input_value):
    if input_value == None:
        input_value = 0.0
    return 'Output: {}'.format(input_value)

@app.callback(Output('Mygraph', 'figure'),#Light Curve
            [
                Input('lc_upload-data', 'contents'),
                Input('lc_upload-data', 'filename'),
            ])

def update_graph(contents, filename):
    x    = [];y    = [];xx=[];yy=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = ab.parse_data(contents, filename)
        x    = df[df.columns[0]]
        y    = df[df.columns[1]]
        yerr = df[df.columns[2]]
        x = np.asarray(x);y = np.asarray(y);yerr = np.asarray(yerr)
        ind = np.argsort(x)
        xx=x[ind];yy=y[ind];yyerr = yerr[ind]
    else:
        xx = [1,2];yy=[1,2]
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
            yaxis=dict(title="MAG"),
            height=500,
            width=500 
                        ) 
                    )
    fig['layout']['yaxis']['autorange'] = "reversed"
    return fig


@app.callback(Output('LombScargle', 'figure'),#Lomb-Scargle Plot
            [
                Input('lc_upload-data', 'contents'),
                Input('lc_upload-data', 'filename'),
                Input('my-input-t0', 'value'),
                Input('my-input-period', 'value'),
            ])
def update_graph(contents, filename, tnot, period):
    x = [];y = [];frequency=[];power=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = ab.parse_data(contents, filename)
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
    else:
        frequency=[1,2];power=[1,2]
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
            yaxis=dict(title="POWER"),
            height=500,
            width=500  
                        ) 
                    )
    return fig


@app.callback(Output('Mygraph2', 'figure'),#Phase-Folded Light Curve
            [
                Input('lc_upload-data', 'contents'),
                Input('lc_upload-data', 'filename'),
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
        df = ab.parse_data(contents, filename)
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
    else:
        xstack=[1,2];ystack=[1,2]
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
            yaxis=dict(title="MAG"),
            height=500,
            width=500  
                        ) 
                    )
    fig['layout']['yaxis']['autorange'] = "reversed"
    return fig


@app.callback([
                Output('hidden-value', 'children'),
                Output('my-output-bf', 'children'),
            ],
            [
                Input('lc_upload-data', 'contents'),
                Input('lc_upload-data', 'filename'),
            ])
def update_hidden(contents, filename):
    x = [];y = [];xx = [];yy = [];xxx = [];yyy = [];frequency=[];power=[];bf=1.0
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = ab.parse_data(contents, filename)
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
                Input('lc_upload-data', 'contents'),
                Input('lc_upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = ab.parse_data(contents, filename)
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
                Input('lc_upload-data', 'contents'),
                Input('lc_upload-data', 'filename'),
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
        df = ab.parse_data(contents, filename)
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

# Building collapsible div
@app.callback(
    Output("lc_collapse", "is_open"),
    [Input("lc_collapse-button", "n_clicks")],
    [State("lc_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("bs_collapse", "is_open"),
    [Input("bs_collapse-button", "n_clicks")],
    [State("bs_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)
