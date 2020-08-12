import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import base64
import io

# Constants
project_title = 'Astronomer Dashboard (ADASH)'

# CSS Styles and colors:
colors = {
    'main_background': '#C2CAD0',  # 'black',
    'div_background': '#e1eef0',  # '#6B5B95',
    'table_header_background': 'silver',
    'test_color': 'red'
}
main_div_style = {
    'background': colors['div_background'],
    'color': 'black',
    'borderRadius': '5px',
    'margin': '20px',
    'width': '100%',
    'textAlign': 'center',
}
hidden_style = {
    'display': 'none'
}
tabs_style = {**main_div_style,
              **{
                  'marginTop': '0px',
                  'font-size': '15px',
              }}
tabs_selected_style = {
    'backgroundColor': colors['div_background'],
    'fontWeight': 'bold',
}

def build_top_banner():
    return html.Div(id='banner',
                    style={**main_div_style, **{'background': colors['main_background']}},
                    children=[
                        html.H5(project_title.upper()),
                    ])

### LC section #############################################################################

def lc_collapsible_div(my_div, title_div):
    return html.Div(
        style=main_div_style,
        children=[
            html.Br([]),
            dbc.Col(
                children=[
                    dbc.Button(
                        children=[
                            html.H5(
                                children=[title_div + ' + ']
                            )],
                        id="lc_collapse-button",
                        className="mb-3",
                        color="info",
                    )]),
            dbc.Collapse(id="lc_collapse",
                         children=[
                             my_div,
                         ]),
        ])


def lc_build_control_area():
    return dbc.Row(children=[
        dbc.Col(id='nav-bar-col1',
                style={**main_div_style,},
                children=[lc_build_upload_area(),
                    html.Br([]),
                    dbc.Row(
                        children=[html.Div(["Period: ",dcc.Input(id='my-input-period', value='1.0', type='number', style={'width': '20%', 'display': 'inline-block'})]),
                        html.Div(["T0: ",dcc.Input(id='my-input-t0', value='0.0', type='number',style={'width': '20%', 'display': 'inline-block'})]),
                        html.Div(["Best Period: ",dcc.Input(id='my-input-bf', value='0.0', type='number',style={'width': '20%', 'display': 'inline-block'})]),
                        html.Br([]),
                        ]
                    ),
                ]),
        dbc.Col(id='nav-bar-col2',
#                style={**main_div_style,},
                children=[html.Div(dcc.Graph(id='Mygraph')),
                html.Div(id='output-data-upload',),#style={'width': '33%', 'display': 'inline-block'}),
                ]),
        dbc.Col(id='nav-bar-col3',
#                style={**main_div_style,},
                children=[
                        html.Div(dcc.Graph(id='LombScargle')), 
                        html.Div(html.Div(id='my-output-bf')),#,style={'position': 'absolute','left': '45%','bottom': '50%'})),
                ]),
        dbc.Col(id='nav-bar-col4',
#                style={**main_div_style,},
                children=[
                        html.Div(dcc.Graph(id='Mygraph2')),
                        html.Div(id='output-data-phase-fold'),#style={'width': '33%', 'display': 'inline-block'}),
                ]),
    ])

def lc_build_upload_area():
    return dcc.Upload(id='lc_upload-data',
                        children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
                        style={
                            'width': '30%',
                            'height': '50px',
                            'lineHeight': '60px',
                            'borderWidth': '5px',
                            'borderStyle': 'dashed',
                            'borderRadius': '1px',
                            'textAlign': 'center',
                            },
                            # Allow multiple files to be uploaded
                            multiple=True)

############# End LC Section #####################################################
##################################################################
##################################################################
##################################################################
############# BS Section #####################################################

def bs_collapsible_div(my_div, title_div):
    return html.Div(
        style=main_div_style,
        children=[
            html.Br([]),
            dbc.Col(
                children=[
                    dbc.Button(
                        children=[
                            html.H5(
                                children=[title_div + ' + ']
                            )],
                        id="bs_collapse-button",
                        className="mb-3",
                        color="info",
                    )]),
            dbc.Collapse(id="bs_collapse",
                         children=[
                             my_div,
                         ]),
        ])


def bs_build_control_area():
    return dbc.Row(children=[
        dbc.Col(id='nav-bar-col5',
                style={**main_div_style,
                       },
                children=[
                    html.H5(["Upload Files"]),
                    bs_build_upload_area(),
                    html.Br([]),
                    dbc.Row(
                        children=[]
                    ),
                ]),
        dbc.Col(id='nav-bar-col6',
                style={**main_div_style, **{'marginLeft': 100}},
                children=[html.H5(["Hello"]),]),
    ])

def bs_build_upload_area():
    return dcc.Upload(id='bs_upload-data', multiple=True,
                      style={
                          'width': '100%',
                          'lineHeight': '60px',
                          'borderWidth': '1px',
                          'borderStyle': 'dashed',
                          'borderRadius': '5px',
                          'textAlign': 'center',
                      },
                      children=html.Div([
                          'Drag and Drop or ',
                          html.A('Select Files')
                      ])
                      )




############# End BS Section #####################################################

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


def lc_build_download_button():
    return dbc.Button(id="lc_download-button", color="danger",
                      children=[
                          html.H5(
                              children=[
                                  html.A(
                                      # TODO: add icon here
                                      'Download CSV',
                                      id='my-link',
                                      download="candidateList.csv",
                                      href="",
                                  ),
                              ])
                      ], )

def lc_build_scrape_option():
    return dcc.Checklist(
        id='lc_scrape-option',
        options=[{'label': " Find Additional Data Online", 'value': 'scrape'}],
        value=[],
        style={'display': 'block', 'textAlign': 'left', }
    )


def lc_build_input_area():
    return html.Div(
        children=[
            dbc.Row(
                children=[
                    dbc.Col([html.H6("System: ")], style={'textAlign': 'right', }),
                    dbc.Col([dcc.Input(id="lc_system_name",
                                       placeholder="Add System", )]),
                    dbc.Col([html.H6("")], style={'textAlign': 'right', }),
                ]),
            html.Br([]),
            dbc.Row(
                children=[
                    dbc.Col([html.H6("Program: ")], style={'textAlign': 'right', }),
                    dbc.Col([dcc.Input(id="lc_program_name",
                                       placeholder="Add Program", )]),
                    dbc.Col([html.H6("")], style={'textAlign': 'right', }),
                ]),
            html.Br([]),
            dbc.Row(
                children=[
                    dbc.Col([html.H6("Box: ")], style={'textAlign': 'right', }),
                    dbc.Col([dcc.Input(id="lc_box_name",
                                       placeholder="Add Box", )]),
                    dbc.Col([html.H6("")], style={'textAlign': 'right', }),
                ]),
            html.Br([]),
            dbc.Row(
                children=[
                    dbc.Col([html.H6("Board: ")], style={'textAlign': 'right', }),
                    dbc.Col([dcc.Input(id="lc_board_name",
                                       placeholder="Add Board", )]),
                    dbc.Col([html.H6("")], style={'textAlign': 'right', }),
                ]),
            html.Br([]),
        ])

def lc_build_filter_parts():
    return dcc.Checklist(
        id='lc_filter-option',
        options=[{'label': " Remove Mechanical Parts", 'value': 'filter'}],
        value=[],
        style={'display': 'block', 'textAlign': 'left', }
    )


def lc_build_filter_descriptions():
    return dcc.Checklist(
        id='lc_filter-description',
        options=[{'label': " Remove Parts Without Item Description", 'value': 'filter-description'}],
        value=[],
        style={'display': 'block', 'textAlign': 'left', }
    )


def lc_build_filter_manpn():
    return dcc.Checklist(
        id='lc_filter-manpn',
        options=[{'label': " Remove Parts Without Manufacturer PN", 'value': 'filter-manpn'}],
        value=[],
        style={'display': 'block', 'textAlign': 'left', }
    )


def lc_build_bom_area():
    return dbc.Col(id='lc_bom-content',
                   style=tabs_style,
                   children=[
                       html.Br([]),
                       html.H5(["Bill of Material"]),
                       html.Div(id='lc_table-area', children=[]),
                       html.Br([]),
                       html.Br([]),
                   ])


# TODO: complete Metrics section
def build_metrics_area():
    return dbc.Col(id='metrics-area',
                   style=tabs_style,
                   children=[
                       html.Br([]),
                       html.H5(["Performance Metrics"]),
                       html.Br([]),
                       dbc.Row(
                           children=[
                               build_metrics_left_area(),
                               build_metrics_center_area(),
                               build_metrics_right_area(),
                           ]),
                       html.Br([]),
                       html.Br([]),
                   ])


def build_metrics_left_area():
    return dbc.Col(id='metrics-area-left',
                   children=[
                       dbc.Row(
                           children=[
                               dbc.Col([html.H6("Total Files Uploaded: ")], style={'textAlign': 'right', }),
                               dbc.Col([html.H6(id='files_detected_output')], style={'textAlign': 'left', }),
                           ]),
                       html.Br([]),
                       dbc.Row(
                           children=[
                               dbc.Col([html.H6("Files Successfully Processed: ")], style={'textAlign': 'right', }),
                               dbc.Col([html.H6(id='files_processed_output')], style={'textAlign': 'left', }),
                           ]),
                       html.Br([]),
                       dbc.Row(
                           children=[
                               dbc.Col([html.H6("Files Not Currently Supported: ")], style={'textAlign': 'right', }),
                               dbc.Col([html.H6(id='files_unsupported_output')], style={'textAlign': 'left', }),
                           ]),
                   ])


def build_metrics_center_area():
    return dbc.Col(id='metrics-area-center',
                   children=[
                       dbc.Row(
                           children=[
                               dbc.Col([html.H6("Total Parts Extracted: ")], style={'textAlign': 'right', }),
                               dbc.Col([html.H6(id='parts_extracted_output')], style={'textAlign': 'left', }),
                           ]),
                       html.Br([]),
                       dbc.Row(
                           children=[
                               dbc.Col([html.H6("Total Mechanical Parts: ")], style={'textAlign': 'right', }),
                               dbc.Col([html.H6(id='parts_filtered_output')], style={'textAlign': 'left', }),
                           ]),

                   ])


def build_metrics_right_area():
    return dbc.Col(id='metrics-area-right',
                   children=[

                   ])


def build_progress_area():
    return dbc.Col(id='progress-area',
                   style=tabs_style,
                   children=[
                       html.Br([]),
                       html.H5(["Upload and Extraction Progress"]),
                       html.Br([]),
                       html.Br([]),
                       dbc.Col(
                           children=[
                               html.H6(id="upload-progress-message"),
                               html.Br([]),
                               html.Br([]),
                               html.H6(id='process-progress-message'),
                               dbc.Spinner(html.Div(id='current-table', style=hidden_style), color="info"),
                               html.Br([]),
                               html.Br([]),
                           ],
                           style={'textAlign': 'center', }
                       ),
                   ])


def build_main_content_page():
    return dcc.Tabs(
        parent_className='custom-tabs',
        style={**main_div_style,
               **{'height': '100hv', 'marginBottom': '0px'}},
        children=[
            dcc.Tab(label='Progress'.upper(),
                    selected_style=tabs_selected_style,
                    children=[
                        build_progress_area(),
                    ]),
            dcc.Tab(label='Parts List'.upper(),
                    selected_style=tabs_selected_style,
                    children=[
                        build_bom_area(),
                    ]),
            dcc.Tab(label='Performance Metrics'.upper(),
                    selected_style=tabs_selected_style,
                    children=[
                        build_metrics_area(),
                    ]),
        ])


def build_table_area(df_table, filter_val_bool, filter_desc_bool, filter_manpn_bool):
    if df_table is None:
        df_table = pd.DataFrame(None, columns=bom_attributes, index=[x for x in range(10)])
    elif isinstance(df_table, str):
        df_table = pd.read_json(df_table, orient='split')
        df_table = df_table[bom_attributes]

    # filtering rows according to descriptions, using `filter_rows(bom_table, remove_list=[], find_list=[])`
    if filter_val_bool:
        df_table = filter_rows(df_table, remove_list=['fasteners'])
        df_table = row_filter_csv(df_table, remove_list=['HW'])
    if filter_desc_bool:
        df_table = filter_empty_description(df_table)
    if filter_manpn_bool:
        df_table = filter_empty_pn(df_table, pn_column='ManufacturersPN')

    # Converting df to dictionary as required by DataTable's 'data' values
    table_data = df_table.to_dict('records')

    # filtering columns depending on user specification
    display_columns = [{"name": friendly_names[i], "id": i, "hideable": True} for i in df_table.columns]

    return html.Div(id='table_main',
                    style={
                        'color': 'black',
                        'fontSize': '12px',
                        'marginRight': '30px',
                        'marginLeft': '10px'
                    },
                    children=[
                        dash_table.DataTable(
                            id='bom_table',
                            columns=display_columns,
                            data=table_data,
                            css=[
                                {"selector": ".column-header--delete svg", "rule": 'display: "none"'},
                            ],
                            style_table={
                                'overflowX': 'scroll',
                                'overflowY': 'scroll',
                                'padding': '30px',
                            },

                            # Filtering and sorting
                            filter_action="native",
                            sort_action='native',

                            # Pages:
                            page_action="native",
                            page_current=0,
                            page_size=15,

                            style_data={
                                'whiteSpace': 'normal',
                            },
                            style_header={
                                'backgroundColor': colors['table_header_background'],
                                'fontWeight': 'bold',
                                'font-size': '15px',
                                'textOverflow': 'ellipsis',
                                'textAlign': 'center',
                            },
                            style_cell={
                                'textAlign': 'center',
                                'minWidth': '100px',
                                'maxWidth': '350px',
                                'textOverflow': 'ellipsis',
                            },

                        )
                    ])
