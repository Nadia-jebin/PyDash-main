# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 16:06:31 2022

@author: nadiajebin
"""

#import openpyxl
#from openpyxl import Workbook, load_workbook
import pandas as pd
import csv

import time
from time import mktime
from datetime import datetime
# from datetime import date

import sys
import numpy as np

import matplotlib.pyplot as plt
import plotly
import chart_studio.plotly as py
import seaborn as sns
from plotly import graph_objs as go
import plotly.express as px
#import datatable as dt

import dash
import dash_table
from datetime import date
from dash import Dash, dcc, html
from dash.dependencies import Input, State, Output
# import dash_core_components as dcc
# import dash_html_components as html
import dash_bootstrap_components as dbc
# from dash.dependencies import Input, Output

# from jupyter_dash import JupyterDash  # pip install dash==1.19.0 or higher
from dash import callback_context

raw_file = pd.read_excel("QMES_Birichina1_Feb01_06.xlsx")
raw_file1 = raw_file.copy()
raw_file1["EntryDate"] = raw_file1['EntryDate'].dt.strftime('%m/%d/%Y')

editfile = raw_file1.copy()
editfile = editfile.drop(
    ['EntryTime', 'BatchQty', 'PoNumber', 'BuyerName', 'ProductType', 'OperatorId', 'MachineId', 'UserID',
     'DefectPos', 'SMV', 'Size', 'TabId', 'StyleCat', 'DefectID', 'ModuleName', 'Shift'], axis=1)
editfile = editfile.rename(
    columns={'BusinessUnit': 'Unit', 'LineNumber': 'Line', 'StyleSubCat': 'Style', 'EntryDate': 'Date',
             'Color': 'BPO Color'})

df = pd.DataFrame(editfile)
df['Total Production'] = df['GarmentsNumber'].map(df['GarmentsNumber'].value_counts())
df1 = df.groupby(['Date', 'Unit', 'Line', 'Style', 'BPO Color', 'DefectName']).agg(
    {'GarmentsNumber': 'nunique', 'Total Production': 'sum', 'DefectCount': 'sum'}).reset_index()

mew = df1.copy()
denominator = mew['Total Production'] / 4
mew['DHU%'] = (mew['DefectCount'] * 100) / denominator

mew2 = mew.copy()
mew3 = df.groupby(['Date', 'Unit', 'Line', 'Style', 'BPO Color']).agg(
    {'GarmentsNumber': 'nunique', 'Total Production': 'sum', 'DefectCount': 'sum'}).reset_index()
mew3 = mew3.rename(columns={'Total_Unique_GarmentsNumber': 'Total Unique GarmentsNumber', 'DefectCount': 'TotalDefect'})

mew2 = mew2.rename(columns={'GarmentsNumber': 'DefectName wise Unique GarmentsNumber',
                            'Total Production': 'DefectName wise Total Production',
                            'DefectCount': 'DefectName wise DefectCount'})

defect_name = mew2.copy()
total_defect = mew3.copy()

merge_file = pd.merge(defect_name, total_defect, on=['Date', 'Unit', 'Line', 'Style', 'BPO Color'])
del merge_file['DHU%']
merge_file['DHU%'] = (merge_file['DefectName wise Unique GarmentsNumber'] * 100) / (merge_file['GarmentsNumber'] / 4)
merge_file = merge_file[merge_file['DefectName wise DefectCount'] > 0]

dashboard_data = merge_file.copy()
dashboard_data = dashboard_data.rename(
    columns={'DefectName wise Unique GarmentsNumber': 'Defective GMNT', 'GarmentsNumber': 'Check QTY'})
del dashboard_data['DefectName wise Total Production']
del dashboard_data['DefectName wise DefectCount']
del dashboard_data['Total Production']

ind = dashboard_data[
    ['Date', 'Unit', 'Line', 'Style', 'BPO Color', 'Defective GMNT', 'Check QTY', 'TotalDefect', 'DefectName']].copy()
ind_twice = ind.pivot_table('Defective GMNT',
                            ['Date', 'Unit', 'Line', 'Style', 'BPO Color', 'Check QTY', 'TotalDefect'],
                            'DefectName').reset_index()
ind_twice['Line'] = ind_twice['Line'].str.replace(r'\D', '')
ind_twice['Line'] = ind_twice['Line'].astype(str).str.zfill(2)
ind_twice = ind_twice.sort_values(by=['Date', 'Unit', 'Line'])
ind_twice['Unique Defect Count'] = ind_twice.iloc[:, 7:-1].sum(axis=1).astype(int)
ind_twice["DHU%"] = (ind_twice["Unique Defect Count"] * 100) / ind_twice['Check QTY']
ind_twice["Defect%"] = (ind_twice['TotalDefect'] * 100) / ind_twice['Check QTY']
ind_twice["Total defect type"] = 72 - (ind_twice.isnull().sum(axis=1))
ind_new_sorted = ind_twice[['Date', 'Unit', 'Line', 'Style', 'BPO Color', 'Check QTY',
                            'TotalDefect', 'Unique Defect Count', 'Total defect type', 'DHU%', 'Defect%',
                            ' Fabric Reject', ' Join Stitch', ' Pleat', ' Pointy',
                            'Bar Tack Defect', 'Bobbling', 'Bow Defect ', 'Broken STC ',
                            'Crack STC', 'Crack STC ', 'Dirty Spot', 'Down STC', 'Down STC ',
                            'Fabric Defect ', 'Fabric Fault ', 'Fabric Reject', 'Hi low',
                            'High Low', 'Join Stitch ', 'Label Defect ', 'Label Mistake',
                            'Lace Defect ', 'MTS Deviation', 'MTS Division ', 'Needle Defect',
                            'Needle Defect ', 'Needle damage', 'Non Inclusion ', 'Nosing',
                            'Oil Spot', 'Open  STC', 'Open Seam', 'Other Defect',
                            'Out of Tolerance', 'Out of Tolerance ', 'Out of tolarence',
                            'Outer Looseness', 'Pleat ', 'Pointy ', 'Poor Shape', 'Poor Tension',
                            'Puckering', 'Puckering ', 'Pull Yarn', 'Raw Edge', 'Raw Edge ',
                            'Reverse Defect ', 'Roping', 'Roping ', 'SPI problem', 'Sewing Reject',
                            'Shading', 'Shading ', 'Sharing Defect ', 'Sharpe Edge ', 'Shiring',
                            'Single STC ', 'Size Mistake', 'Skip Stitch', 'Skip Stitch ', 'Steps ',
                            'Stretch Out', 'Tension Tight & Loose', 'Thread Mistake',
                            'Thread Mistake ', 'Twisting', 'Un cut Thread', 'Un cut Thread ',
                            'Uneven', 'Up Down', 'Wavy', 'Width Uneven']].copy()

ind_new_sorted['DHU%'] = round(ind_new_sorted['DHU%'], 2)
ind_new_sorted['Defect%'] = round(ind_new_sorted['Defect%'], 2)

output_excel = ind_new_sorted.to_excel("Defect.xlsx")
tao = pd.read_excel("Defect.xlsx")
tao1 = tao.copy()
tao2 = pd.DataFrame(tao1)

# DashBoard Line and Unit wise
pew = tao2[['Date', 'Unit', 'Line', 'Style', 'BPO Color', 'Check QTY', 'TotalDefect', 'Unique Defect Count']].copy()
pew = pew.groupby(['Date', 'Unit', 'Line']).agg(
    {'Check QTY': 'sum', 'TotalDefect': 'sum', 'Unique Defect Count': 'sum'}).reset_index()

dwgc = df.copy()
dwgc = dwgc.groupby(['Date', 'Unit', 'Line']).agg({'GarmentsNumber': 'nunique', 'DefectCount': 'sum'}).reset_index()

# Defect postion data

raw_file1['LineNumber'] = raw_file1['LineNumber'].str.replace(r'\D', '')
raw_file1['LineNumber'] = raw_file1['LineNumber'].astype(str).str.zfill(2)

defectpost = raw_file1.copy()
defectpost = defectpost.drop(
    ['EntryTime', 'BatchQty', 'PoNumber', 'BuyerName', 'ProductType', 'OperatorId', 'MachineId', 'UserID',
     'SMV', 'Size', 'TabId', 'StyleCat', 'DefectID', 'ModuleName', 'Shift'], axis=1)
defectpost = defectpost.rename(
    columns={'BusinessUnit': 'Unit', 'LineNumber': 'Line', 'StyleSubCat': 'Style', 'EntryDate': 'Date',
             'Color': 'BPO Color'})
defectpost = defectpost.groupby(['Date', 'Unit', 'Line', 'Style', 'BPO Color', 'DefectName', 'DefectPos']).agg(
    {'GarmentsNumber': 'nunique', 'DefectCount': 'sum'}).reset_index()
filt_defect = defectpost.copy()
filt_defectname = defectpost.copy()
filt_defect = filt_defect.groupby(['Date', 'Unit', 'Line', 'DefectPos']).agg({'DefectCount': 'sum'}).reset_index()
filt_defectname = filt_defectname.groupby(['Date', 'Unit', 'Line', 'DefectName']).agg(
    {'GarmentsNumber': 'sum'}).reset_index()
filt_defect = filt_defect[filt_defect['DefectCount'] > 0]
filt_defectname = filt_defectname[filt_defectname['DefectName'] != 'na']

# Plot
plt_hour = raw_file1.copy()
plt_hour['EntryTime'] = plt_hour['EntryTime'].apply(lambda t: t.strftime('%H'))
plt_hour['EntryTime'] = plt_hour['EntryTime'].astype(str)
plt_hour['EntryTime'] = plt_hour['EntryTime'] + ":00"
plt_hour = plt_hour.groupby(['EntryDate', 'BusinessUnit', 'LineNumber', 'EntryTime']).agg(
    {'GarmentsNumber': 'nunique', 'DefectCount': 'sum'}).reset_index()
plt_hour = plt_hour.rename(columns={'EntryDate': 'Date'})
plt_hour = plt_hour.sort_values(['Date', 'BusinessUnit', 'LineNumber', 'EntryTime', 'GarmentsNumber'], ascending=True)

plt_hour_f = plt_hour.copy()
plt_hour_f = plt_hour_f.groupby(['EntryTime']).agg({'GarmentsNumber': 'sum'}).reset_index()
plt_hour_f = plt_hour_f.sort_values(['EntryTime', 'GarmentsNumber'], ascending=True)

# App Start
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
server=app.server

date = tao2.Date.unique().tolist()
unit = tao2.Unit.unique().tolist()
line = tao2.Line.unique().tolist()
style = tao2.Style.unique().tolist()

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Page 1: Filter Table', href='/page-1'),
    html.Br(),
    dcc.Link('Page 2: Summary Table', href='/page-2'),
    html.Br(),
    dcc.Link('Dash', href='/page-29'),
])
'''######################################### Page 1 ###############################'''

page_1_layout = html.Div([
    html.H1('Page 1: Filter Data'),
    ###########################
    html.Div(

        children=[
            html.Div('Filtered Dash Board',
                     style={
                         'height': '50px',
                         'font-size': '25px',
                         'font-family': 'Georgia',
                         'text-align': "left",
                         'display': 'block',
                         'width': '22%',
                     }
                     ),
            dcc.Dropdown(
                id='Date_dropdown',
                options=[{'label': st, 'value': st} for st in date],
                value="Date",
                placeholder="Date",
                style={'color': "Black", 'background-color': 'darkcyan', 'font-size': '25px', 'display': 'inline-block',
                       'width': '50%'}
            ),  # 'border-radius':'4px'

            dcc.Dropdown(
                id='Unit_dropdown',
                options=[{'label': un, 'value': un} for un in unit],
                value="Unit",
                placeholder="Unit",
                style={'color': "Black", 'background-color': 'darkcyan', 'font-size': '25px', 'display': 'inline-block',
                       'width': '50%'}
            ),

            dcc.Dropdown(
                id='Style_dropdown',
                options=[{'label': sty, 'value': sty} for sty in style],
                value="Style",
                placeholder="Style",
                style={'color': "Black", 'background-color': 'darkcyan', 'font-size': '25px', 'display': 'inline-block',
                       'width': '50%'}
            ),

            dcc.Dropdown(
                id='Line_dropdown',
                options=[{'label': ln, 'value': ln} for ln in line],
                value="Line",
                placeholder="Line",
                style={'color': "Black", 'background-color': 'darkcyan', 'font-size': '25px', 'display': 'inline-block',
                       'width': '50%'}
            ),

            dash_table.DataTable(
                id='table-container',
                columns=[
                    {"id": c, "name": c, "deletable": False, "selectable": False} for c in tao2.columns.values
                ],
                data=tao2.to_dict('records'),
                editable=False,
                row_selectable="multi",
                row_deletable=False,
                selected_rows=[],
                page_action="native",

                style_cell_conditional=[
                    {
                        'color': "Black",
                        'font-size': '20px',
                        'text-align': "center",
                        'background-color': 'darkcyan',
                        'border-style': 'solid',
                    }
                ],
            )
        ],

    ),

    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
])

'''######################################### Page 2 ###############################'''
page_2_layout = html.Div([
    html.H1('Page 2: Summary Table'),
    html.Div('Dash Board',
             style={
                 'color': "White",
                 'height': '50px',
                 'font-size': '30px',
                 'font-family': 'Georgia',
                 'text-align': "center",
                 'background-color': 'Black',
                 'border-style': 'Double',
                 'border-color': 'Grey',
                 'display': 'block',
                 'width': '20%',
             }
             ),
    html.Div(

        html.Div([
            dash_table.DataTable(
                id='datatable_id',
                data=tao2.to_dict('records'),
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": False} for i in tao2.columns
                ],
                editable=False,
                filter_action='native',
                sort_action="native",
                sort_mode="multi",
                row_selectable="multi",
                row_deletable=False,
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=20,

                style_cell_conditional=[
                    {
                        'color': "white",
                        'font-size': '20px',
                        'text-align': "center",
                        'background-color': 'black',
                        'border-style': 'double',
                        # 'display':'inline-block',
                    }
                ],
            ),
        ], className='row'), ),
    ###################################################
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Filter Page', href='/page-1'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.Br(),
    dcc.Link('Go to Dash', href='/page-29'),
    html.Br(),
])

# defectpost['LineNumber']=defectpost['LineNumber'].astype(int)
plt_hour['LineNumber'] = plt_hour['LineNumber'].astype(int)
filt_defect['Line'] = filt_defect['Line'].astype(int)
filt_defectname['Line'] = filt_defectname['Line'].astype(int)

'''######################################### Page 29 ###############################'''

page_29_layout = html.Div([
    html.H1('Defect Report: '),
    ###################################################
    # Your Code

    ###########################
    dbc.Container([

        dbc.Row([

        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Insert Values"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Input(id='input1', value='Start Date', type='text',
                                                  style={'display': 'inline-block'}), ]),
                                    dbc.Col([
                                        dbc.Input(id='input2', value='End date', type='text',
                                                  style={'display': 'inline-block'}), ]), ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Input(id='unit_input', value='Unit', type='text', style={"width": '1'}), ]),
                                    dbc.Col([
                                        dbc.Input(id='line_input', value='Line', type='number',
                                                  style={'display': 'inline-block'}), ]), ]),
                                dbc.Button(id='submit-button1', type='submit', children='Submit', size="sm"),

                                #                             html.H6("Select Buy $ Sell Dates:"),

                            ])
                        ])
                    ], width=12),
                ]),

                dbc.Row(
                    dbc.Col(html.Hr(style={'border': "3px solid gray"}), width=12)
                ),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H6("Total Production"),
                            html.H4(id="totalProduction", style={'fontWeight': 'bold'}),
                        ])
                    ]), width=12)
                    , ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Defects"),
                                html.H4(id="totaldefect", style={'fontWeight': 'bold'}),

                            ])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Defective Garments"),
                                html.H4(id="UniqueDefectCount", style={'fontWeight': 'bold'}),
                            ])
                        ])
                    ], width=6),

                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("DHU%"),
                                html.H4(id="dhu", style={'fontWeight': 'bold'}),

                            ])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Defect%"),
                                #                             html.H2(id="profit_pct", children="", style={'fontWeight':'bold'})
                                html.H4(id='output_div', style={'fontWeight': 'bold'}),
                            ])
                        ])
                    ], width=6),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Link('Home', href='/'),
                                dcc.Link('Data Table', href='/page-2', style={"margin-left": "10px"}),
                                dcc.Link('Filter ', href='/page-1', style={"margin-left": "10px"}),

                            ])
                        ])
                    ], width=12), ]),

            ], width=4),

            dbc.Col([
                dbc.Row([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("No of Unique Garment by Hour"),
                            dcc.Graph(id="bar-chart", config={'displayModeBar': True},
                                      figure=px.bar(plt_hour_f, x='EntryTime', y='GarmentsNumber',
                                                    text="GarmentsNumber").
                                      update_layout(autosize=False, width=700, height=250),
                                      )
                        ])
                    ])
                ]),
                dbc.Row(
                    dbc.Col(html.Hr(style={'border': "3px solid gray"}), width=12)
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3(id='Datatablewithtable',
                                        children=html.Div([
                                            dash_table.DataTable(
                                                id='table-dropdown',
                                                data=filt_defectname.to_dict('records'),
                                                page_current=0,
                                                page_size=3,
                                                editable=False,
                                                columns=[{"name": i, "id": i, "deletable": True} for i in
                                                         filt_defectname.iloc[:, 3:]],
                                                style_cell_conditional=[
                                                    {
                                                        'font-size': '15px',
                                                        'color': 'White',
                                                        'background-color': 'Black'
                                                    }
                                                ],

                                            ),
                                        ], style={'fontWeight': 'bold', 'textAlign': 'center', 'color': 'white'})
                                        ),
                            ]), ]), ], width=6, md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3(id='Datatablewithtable2',
                                        children=html.Div([
                                            dash_table.DataTable(
                                                id='table-dropdown2',
                                                data=filt_defect.to_dict('records'),
                                                page_current=0,
                                                page_size=3,
                                                editable=False,
                                                columns=[{"name": i, "id": i, "deletable": True} for i in
                                                         filt_defect.iloc[:, 3:]],
                                                style_cell_conditional=[
                                                    {
                                                        'font-size': '15px',
                                                        'color': 'White',
                                                        'background-color': 'Black'
                                                    }
                                                ],

                                            ),
                                        ], style={'fontWeight': 'bold', 'textAlign': 'center', 'color': 'white'}),
                                        )  #

                            ])
                        ]), ], width=6, md=6),
                ])
            ], width=7)
        ], className="mt-3")
    ], fluid=True, style={'backgroundColor': 'lightgrey'}),
    ###################################################
    html.Div(id='page-29-content'),
])


######################### Function ################################
@app.callback(
    Output("dhu", "children"),
    Output("totaldefect", "children"),
    Output("totalProduction", "children"),
    Output('UniqueDefectCount', "children"),
    Output('output_div', 'children'),
    Output('bar-chart', 'figure'),
    Output('table-dropdown', 'data'),
    Output('table-dropdown2', 'data'),
    [Input('submit-button1', 'n_clicks')],
    [State('input1', 'value')],
    [State('input2', 'value')],
    [State('unit_input', 'value')],
    [State('line_input', 'value')],
)
def update_o(clicks, input1, input2, unit_input, line_input):
    # Static Output
    new2 = pew.loc[
        (pew['Unit'] == unit_input) & (pew["Line"] == line_input), ['Date', 'Unit', 'Line', 'Check QTY', 'TotalDefect',
                                                                    'Unique Defect Count']]
    start_date = new2.index[(new2["Date"] == input1)][0]
    end_date = new2.index[(new2["Date"] == input2)][0]

    # Bar Output
    newplt = plt_hour.loc[
        (plt_hour['BusinessUnit'] == unit_input) & (plt_hour["LineNumber"] == line_input), ['Date', 'BusinessUnit',
                                                                                            'LineNumber', 'EntryTime',
                                                                                            'GarmentsNumber',
                                                                                            'DefectCount']]
    start_date1 = newplt.index[(newplt["Date"] == input1)].min()
    end_date1 = newplt.index[(newplt["Date"] == input2)].max()
    dff = newplt.loc[start_date1:end_date1, :]

    # Table
    testu = filt_defectname.loc[(filt_defectname['Unit'] == unit_input) & (filt_defectname["Line"] == line_input),
                                ['Date', 'Unit', 'Line', 'DefectName', 'GarmentsNumber']]
    testu1 = testu.index[(testu["Date"] == input1)].min()
    testu2 = testu.index[(testu["Date"] == input2)].max()
    testudff = testu.loc[testu1:testu2, 'DefectName':]
    data = testudff.to_dict('records')
    columns = [{"name": i, "id": i, } for i in (testudff.columns)]

    # Table2
    testu_dp = filt_defect.loc[(filt_defect['Unit'] == unit_input) & (filt_defect["Line"] == line_input),
                               ['Date', 'Unit', 'Line', 'DefectPos', 'DefectCount']]
    testu_st = testu_dp.index[(testu_dp["Date"] == input1)].min()
    testu_ed = testu_dp.index[(testu_dp["Date"] == input2)].max()
    testud_defp = testu_dp.loc[testu_st:testu_ed, 'DefectPos':]
    #         filt_defect.iloc[:,'DefectPos':]
    data2 = testud_defp.to_dict('records')
    columns = [{"name": i, "id": i, } for i in (testud_defp.columns)]

    if clicks is not None:
        GarmentsNumber = new2.loc[start_date:end_date, 'Check QTY'].sum()
        DefectCount = new2.loc[start_date:end_date, 'TotalDefect'].sum()
        UniqueDefectCount = new2.loc[start_date:end_date, 'Unique Defect Count'].sum()
        DHU = (DefectCount * 100) / GarmentsNumber
        DHU_format = round(DHU, 2)
        DefectPercent = (UniqueDefectCount * 100) / GarmentsNumber
        DefectPercent_format = round(DefectPercent, 2)
        figure = px.bar(dff, x='EntryTime', y='GarmentsNumber', text='GarmentsNumber', color='Date')

        return DHU_format, DefectCount, GarmentsNumber, UniqueDefectCount, DefectPercent_format, figure, data, data2


@app.callback(
    Output('table-container', 'data'),
    [Input('Date_dropdown', 'value')],
    [Input('Unit_dropdown', 'value')],
    [Input('Line_dropdown', 'value')],
    [Input('Style_dropdown', 'value')],
)
def display_table(date, unit, line, style):
    df1 = tao2[tao2.Date == date]
    df2 = df1[df1.Unit == unit]
    df3 = df2[df2.Line == line]
    df4 = df3[df3.Style == style]
    return df4.to_dict('records')


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    #     elif pathname == '/page-3':
    #         return page_3_layout
    elif pathname == '/page-29':
        return page_29_layout
    #     elif pathname == '/page-30':
    #         return page_30_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=False)