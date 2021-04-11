# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 12:36:41 2021
@author: Romen Samuel Wabina
"""
import dash
import json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import analytics.analytics as analytics
from ta import add_all_ta_features
from ta.utils import dropna
from sklearn import preprocessing 
from datetime import datetime, timedelta

from data_handler.data_handler import DataHandler

from ui.custom_dash_components import *

###################### DataHandler ######################

dh = DataHandler()

###################### Layout ###########################

app.layout = html.Div(style = {'backgroundColor': colors['background'], 
                                'marginTop' : 0, 
                                'marginBottom' : 0,
                                'paddingTop' : 0,
                                'paddingBottom': 0},
                      children = [minute_interval, layer_1, tabs, layer_3, selection_tabs,
                                ohlc_graph,day_interval, title_indicators, gauge_indicator, 
                                techindicator_summary, bullet_graph, 
                                toppers_table,market_summary_table, 
                                market_summary_icon, market_summary_graph, storage_div ])

@app.callback(
    Output('ohlc', 'figure'),
    Output('storage', 'children'),
    Input('graph_tab','value'),
    Input('time_tabs', 'value'),
    Input('coin-tabs', 'value'),
    Input('macdmarket','value'),
    )
def update_graph(graph_name, time_tabs_name, coin_tab_name, stat_name):
    df_ohlc = dh.get_data(coin_tab_name, time_tabs_name, limit = 1200)
    df_ohlc = df_ohlc.sort_values(by=['timestamp'])

    date_range = json.dumps({"start":df_ohlc.iloc[0].name.strftime('%Y-%m-%d %H:%M:%S'),"end":df_ohlc.iloc[-1].name.strftime('%Y-%m-%d %H:%M:%S')})

    return create_ohlc(df_ohlc, graph_name, time_tabs_name, coin_tab_name, stat_name),date_range

#@app.callback(
#    Output('ohlc', 'prependData'),
#    [
#        Input('coin-tabs','value'),
#        Input('time_tabs', 'value'),
#        Input('interval-component','n_intervals'),
#        Input('ohlc','relayoutData'),
#        Input('graph_tab','value'),
#        Input('storage', 'children')
#    ],
#    State('ohlc', 'figure'),
#)
#def update_graph2(symbol, timeframe, n_intervals, relayout_data, graph_type, date_range, state):
#    x_range = state['layout']['xaxis']['range']
#    date_range = json.loads(date_range)
#    print(x_range)
#    print(date_range)
#    
#    if x_range[0] <= 10:
#        print('inside')
#        new_data = dh.get_data(symbol, timeframe, range=[None,date_range['start']], limit = 100)
#        print(new_data)
#
#        if graph_type == 'Candlestick':
#
#            return_data = (dict(x = [new_data.index.strftime("%H:%M")],
#                            open = [new_data['open']], 
#                            high = [new_data['high']], 
#                            low = [new_data['low']], 
#                            close = [new_data['close']]),
#                [0]
#            )
#            return return_data
#        elif graph_type == 'Line Plot':
#            pass
#    else:
#        return None


@app.callback(Output('num-indicator', 'figure'),
              [Input('interval-component', 'n_intervals'),
              Input('coin-tabs', 'value')])
def update_data(n, symbol):
    df = dh.get_data(symbol,'1m', limit = 3)
    return create_market_change_indicator(df)

@app.callback(Output('Topper','data'),
              [Input('d-interval-component','n_intervals')])
def update_topper(n):
    df = dh
    return topper_rank(df)

@app.callback(Output('market_summary','data'),
              [Input('d-interval-component','n_intervals')])
def update_market_summary(n):
    df = dh
    return market_summary(df)

@app.callback(Output('market_icon','children'),
              [Input('d-interval-component','n_intervals')])
def update_market_summary_icon(n):
    df = dh
    return market_summary_icons(df)

@app.callback(Output('market_graph','figure'),
              [Input('d-interval-component','n_intervals')])
def update_market_summary_figure(n):
    df = dh
    return market_summary_figure(df)

@app.callback(Output('coin-name-title', 'children'),
               Input('coin-tabs', 'value'))
def update_coin_name(symbol):
    return coin_names[symbol]

@app.callback(Output('coin-logo-title', 'src'),
               Input('coin-tabs', 'value'))
def update_coin_logo(symbol):
    return app.get_asset_url(f'img/{coin_imgs[symbol]}')

@app.callback([Output('rsi-gauge', 'figure'),
               Output('bullet-indicator', 'figure')],
             [Input('interval-component', 'n_intervals'),
              Input('coin-tabs', 'value')])
              
def update_technical_indicators(time_tabs_name, coin_tab_name):
    df = dh.get_data(coin_tab_name, '1d', limit = 100).iloc[1:,:] #starting from 1 because the lastest data point's volume isn't the final volume
    df = add_all_ta_features(df.reindex(index=df.index[::-1]), open="open", high = "high", low = "low", close = "close", 
                                volume = "volume", fillna = True)
    df = df.reindex(index=df.index[::-1])
    #norm_df = analytics.normalize_indicator(df)
    #df = df[['close', 'open', 'high', 'low', 'momentum_kama', 'momentum_rsi', 'trend_cci', 'trend_sma_fast', 'trend_ema_fast']]  
    return create_gauge_rsi_indicator(df), create_bullet_graph(df)

@app.callback(Output('indicators-table', 'data'),
             [Input('interval-component', 'n_intervals'),
              Input('coin-tabs', 'value')])

def update_indicator_table(n, coin_tab_name):
    df = dh.get_data(coin_tab_name, '1d', limit = 1000)
    df = add_all_ta_features(df.reindex(index=df.index[::-1]), open = "open", high = "high", low = "low", close = "close", volume = "volume", fillna = True)
    df = df.reindex(index=df.index[::-1])
    return indicators_table(df)

if __name__ == '__main__':
    app.run_server(debug=True)