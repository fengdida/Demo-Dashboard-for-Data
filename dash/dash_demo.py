# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 14:50:05 2020

@author: fengdida
"""

import os
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_table
import plotly.graph_objs as go


import pandas as pd
import numpy as np

from datetime import datetime

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.config["suppress_callback_exceptions"] = True


df=pd.read_csv('datatable.csv',index_col=0)

list_ISIN=list(set(df['ISIN']))
options_ISIN=[{'label': i, 'value': i} for i in list_ISIN]



def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("DEMO FOR DATA PLATEFORM"),
                    html.H6("Dashboard by Dida"),
                ],
            ),
        ],
    )

        
def Table_chart(isin_value):
    df_table=df[df['ISIN']==isin_value]
    return html.Div(style={'backgroundColor': '#1e2130'}, children=[
        html.H6(''),
        dash_table.DataTable(
        id='datatable-row-ids',
        columns=[
            {'name': i, 'id': i, 'deletable': False} for i in df_table.columns
            # omit the id column
        ],
                
        css=[ {"selector": ".dash-spreadsheet-inner table", "rule": '--text-color: "white"'} ],
        
        fixed_rows={ 'headers': True, 'data': 0 },
                
        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                      'fontWeight': 'bold',
                      
                      },
        style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'textAlign': 'right',
        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        
        },
        style_filter={
        'color': 'white',
        'backgroundColor': 'rgb(70, 70, 70)'        
        },
        data=df_table.to_dict('records'),
        style_table={
        'maxHeight': '300px',
        #'overflowY': 'scroll'
        },
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode='multi',
        #row_selectable='multi',
        row_deletable=False,
        selected_rows=[0,1],
        page_action='none',
        style_as_list_view=True
    ),
])
        
        
app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                        style={'width': '50%'},
                 children=[  
                        dcc.Dropdown(
                        id='dropdown',
                   options=options_ISIN,
                   multi=False,
                   searchable=True,
                   value=options_ISIN[0]['value']
                   ),] ), 
                html.Div(id="table-content"),
                #Table_chart(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),

        #dcc.Store(id="value-setter-store", data=init_value_setter_store()),
        #dcc.Store(id="n-interval-stage", data=50),
        #generate_modal()
    ],
)

@app.callback(
    [Output('app-content', 'children'),
     Output('table-content','children'),
     ],
    [Input('dropdown', 'value'),]
    )            
def update_graph(isin_value):
    titlename=isin_value


    #colors = ['#FF69B4' if id == active_row_id
     #         else '#7FDBFF' if id in selected_id_set
    #          else '#0074D9'
     #         for id in row_ids]
    fig=go.Figure()
    #for i in isin_value:
    #    fig.add_trace(go.Scatter(x=APP.hours, y=df.iloc[i,2], mode='lines', name=df.index[i]))
    #    titlename=titlename+ i +'  '
    x_data=df[df['ISIN']==isin_value].apply(lambda x: datetime.strptime(x[0], '%d-%b-%Y'),axis=1)
    y_data=df[df['ISIN']==isin_value].iloc[:,3]
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines', name=isin_value))
    
    fig.update_layout(dict(
            xaxis={
                'title': titlename,
                'color': 'white'
                #'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': 'Indicative Value',
                'color': 'white'
                #'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            plot_bgcolor= '#1e2130',
            paper_bgcolor= '#1e2130',
            hovermode='closest',
            legend=dict(font={'color':'white'})
        ),
            xaxis_rangeslider_visible=True)

    return [
        dcc.Graph(
            id='line_chart',
            figure=fig
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        ], Table_chart(isin_value)



        
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
