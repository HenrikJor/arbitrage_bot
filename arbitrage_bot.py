# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 00:59:41 2023

@author: Henrik
"""

# -*- coding: utf-8 -*
import requests
import json
import pandas as pd
import os

# Read API key from environment variable
api_key = os.environ.get("API_KEY")

market = "h2h"

region = "eu"

sport_key = "soccer_epl"

url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/'

params = {
    'apiKey': api_key,
    'regions': region,
    'markets': market
    }

odds_response = requests.get(url, params=params) 

odds_data = json.loads(odds_response.text)


# --- Arbitrage finder --- 

#Initalize an empty list to store data rows
rows_list  = []

if all(isinstance(item,dict) for item in odds_data):
    for game in odds_data:
        for bookmaker in game['bookmakers']: 
            for market_ in bookmaker['markets']:
                for outcome in market_['outcomes']:
                    row = {
                        'game_id': game['id'],
                        'sport_key': game['sport_key'],
                        'sport_title': game['sport_title'],
                        'home_team': game['home_team'],
                        'away_team': game['away_team'],
                        'commence_time': game['commence_time'],
                        'bookmaker_key': bookmaker['title'],
                        'bookmaker_title': bookmaker['title'],
                        'bookmaker_last_update' : bookmaker['last_update'],
                        'market_key' : market_['key'],
                        'market_last_update' : market_['last_update'],
                        'outcome_name' : outcome['name'],
                        'outcome_price': outcome['price']
                        
                 }
                    rows_list.append(row)
                
            
df= pd.DataFrame(rows_list)

if not df.empty and 'bookmaker_key' in df.columns:
    df['outcome_price'] = df['outcome_price'].astype(float)
    df= df[~df['bookmaker_key'].isin(['betfair_ex_eu', 'matchbook'])]
    idx = df.groupby(['game_id', 'outcome_name'])['outcome_price'].idxmax()
    df_arbitrage = df.loc[idx].copy()
    df_arbitrage['implied_probability']= 1 /df_arbitrage['outcome_price']
    df_arbitrage['sum_implied_prob'] = df_arbitrage.groupby('game_id')['implied_probability'].transform('sum')
    df_arbitrage = df_arbitrage[df_arbitrage['sum_implied_prob']<1]
    total_stake = 1000
    df_arbitrage ['stake']=(total_stake / df_arbitrage['sum_implied_prob']) * df_arbitrage['implied_probability']


#--- Value odds finder ---
pinnacle = 'pinnacle'
unibet = 'unibet_eu'

df_pinnacle = df_arbitrage[df_arbitrage['bookmaker_key'] == pinnacle]
df_unibet = df_arbitrage[df_arbitrage['bookmaker_key'] == unibet]

merged_df = pd.merge(df_pinnacle, df_unibet, on=['game_id', 'outcome_name', 'bookmaker_key'], suffixes=('_pinnacle', '_unibet'))

merged_df['odds_difference'] = merged_df['outcome_price_pinnacle'] - merged_df['outcome_price_unibet']








    
                        