# -*- coding: utf-8 -*-
import requests
import json
import pandas as pd
import os

# Read API key from environment variable
api_key = os.environ.get("API_KEY")
market = "h2h"
region = "eu"
sport_key = "soccer_epl"

filtered_rows = []  # Initialize list to store filtered data

url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/'

params = {
    'apiKey': api_key,
    'regions': region,
    'markets': market
    }

odds_response = requests.get(url, params=params)
odds_data = json.loads(odds_response.text)

# Initialize lists to store data
filtered_rows = []

if all(isinstance(item, dict) for item in odds_data):
    for game in odds_data:
        pinnacle_odds = {}  # To store Pinnacle odds
        unibet_odds = []    # To store Unibet odds
        for bookmaker in game['bookmakers']:
            if bookmaker['title'] == 'Pinnacle':
                for market_ in bookmaker['markets']:
                    for outcome in market_['outcomes']:
                        pinnacle_odds[outcome['name']] = outcome['price']
            elif bookmaker['title'] == 'Unibet':
                for market_ in bookmaker['markets']:
                    for outcome in market_['outcomes']:
                        unibet_odds.append({
                            'outcome_name': outcome['name'],
                            'outcome_price': outcome['price']
                        })
        # Compare Unibet odds with Pinnacle odds and filter
        for unibet_outcome in unibet_odds:
            unibet_price = unibet_outcome['outcome_price']
            pinnacle_price = pinnacle_odds.get(unibet_outcome['outcome_name'])
            if pinnacle_price:
                price_difference = (unibet_price - pinnacle_price) / pinnacle_price
                if price_difference >= 0.1:  # 10% or more difference
                    row = {
                        'game_id': game['id'],
                        'sport_key': game['sport_key'],
                        'sport_title': game['sport_title'],
                        'home_team': game['home_team'],
                        'away_team': game['away_team'],
                        'commence_time': game['commence_time'],
                        'bookmaker_key': 'Unibet',
                        'bookmaker_title': 'Unibet',
                        'outcome_name': unibet_outcome['outcome_name'],
                        'unibet_odds': unibet_price,
                        'pinnacle_odds': pinnacle_price,
                        'price_difference': price_difference
                    }
                    filtered_rows.append(row)

# Create a DataFrame from the filtered data
filtered_odds_df = pd.DataFrame(filtered_rows)



