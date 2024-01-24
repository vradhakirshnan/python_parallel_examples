import asyncio
import math
import os

import mysql.connector
import pandas as pd
import requests
from dotenv import load_dotenv
from utils import continue_program, pretty_print_dict

load_dotenv()


def connect_to_db(auto_commit=True, staging=False):
    try:
        load_dotenv()
        print(f'host:{os.getenv("DB_LIVE_HOST")}')
        print(f'host:{os.getenv("DB_LIVE_USER")}')
        print(f'host:{os.getenv("DB_LIVE_PASSWORD")}')
        continue_program()
        mydb = mysql.connector.connect(
            host=os.getenv('DB_LIVE_HOST'),
            user=os.getenv('DB_LIVE_USER'),
            password=os.getenv('DB_LIVE_PASSWORD')
        )
    except mysql.connector.Error as err:
        print('Error: ', err)
    else:
        mydb.autocommit = auto_commit
        return mydb


my_conn = connect_to_db()
print(my_conn)
my_cursor = my_conn.cursor(dictionary=True)

# host = 'http://localhost:8000/'
host = 'https://apipb.equentis.com/'
username = 'appsupport@researchandranking.com'
password = '1234'


async def login():
    token = requests.post(f'{host}user/login', headers={}, data={'username': username, 'password': password})
    return token.json()['access_token']


def find_fincode(sym: str):
    query = "SELECT fincode FROM ace_universe.rnr_v4_company_master " \
            "WHERE symbol = %s AND series = 'EQ' " \
            "LIMIT 1"
    my_cursor.execute(query, (sym,))
    result = my_cursor.fetchone()
    return result["fincode"]


def send(data, religion):
    params = {
        "product_id": "14",
        "risk_level_id": "",  # 2 for medium and 3 for high
        "religion": "",
        "data_stock_attributes": {},
        "data_sector_attributes": {},
        "data_market_cap_attributes": {}
    }

    stocks_raw_data = pd.read_excel(data, sheet_name='stocks')
    is_mandatory = stocks_raw_data['Is Mandatory'].tolist()

    symbols = stocks_raw_data['symbol'].tolist()
    risks = stocks_raw_data['risk'].tolist()
    min_allocation = stocks_raw_data[f'min allocation {religion.lower()}'].tolist()
    max_allocation = stocks_raw_data[f'max allocation {religion.lower()}'].tolist()
    params['religion'] = religion
    sector_attributes_raw_data = pd.read_excel(data, sheet_name=f'sector {religion.lower()}')
    sector_list = sector_attributes_raw_data['Sector'].tolist()
    sector_attributes = []
    for sector in sector_list:
        sector_attributes.append({
            'sector_id': sector_list.index(sector) + 1,
            'sector_name': sector,
            'min_stocks': sector_attributes_raw_data['Min Stocks'].tolist()[sector_list.index(sector)],
            'min_allocation': sector_attributes_raw_data['Min Allocation'].tolist()[sector_list.index(sector)],
            'max_stocks': sector_attributes_raw_data['Max Stocks'].tolist()[sector_list.index(sector)],
            'max_allocation': sector_attributes_raw_data['Max Allocation'].tolist()[sector_list.index(sector)],
        })
    params['data_sector_attributes'] = sector_attributes
    for risk in [2, 3]:
        params['risk_level_id'] = risk
        stock_data = []
        # print(len(symbols))
        for symbol in symbols:
            fincode = find_fincode(symbol)

            min_alo = min_allocation[symbols.index(symbol)]
            max_alo = max_allocation[symbols.index(symbol)]
            mandatory = is_mandatory[symbols.index(symbol)]
            risk_type = risks[symbols.index(symbol)]
            if risk_type == "High" and risk == 2:
                continue
            if risk_type == "Medium" and risk == 3:
                continue
            if max_alo == 0 or math.isnan(max_alo):
                continue
            else:
                stock_data.append({
                    "fincode": fincode,
                    "min_allocation": min_alo,
                    "max_allocation": max_alo,
                    "is_mandatory": mandatory,
                    "symbol": symbol
                })

        params['data_stock_attributes'] = stock_data

        # market cap attributes --begin
        if risk == 2:
            market_cap_sheet_name = f'marketcap allocation medium'
        else:
            market_cap_sheet_name = f'marketcap allocation high'
        market_cap_raw_data = pd.read_excel(data, sheet_name=market_cap_sheet_name)
        market_caps = market_cap_raw_data['Market Cap'].tolist()
        market_cap_min_allocation = market_cap_raw_data['Min Allocation'].tolist()
        market_cap_max_allocation = market_cap_raw_data['Max Allocation'].tolist()
        market_cap_attributes = []
        for market_cap in market_caps:
            market_cap_attributes.append({
                'market_cap': market_cap,
                'min_allocation': market_cap_min_allocation[market_caps.index(market_cap)],
                'max_allocation': market_cap_max_allocation[market_caps.index(market_cap)]
            })
        params['data_market_cap_attributes'] = market_cap_attributes
        # market cap attributes --end

        res = requests.post(
            f'{host}research_rules',
            headers={'Authorization': f'Bearer {token}'},
            json=params
        )
        print(res.text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    token = loop.run_until_complete(login())

    data = pd.ExcelFile('Data3.xlsx')

    # analyst rating push
    stocks = pd.read_excel(data, sheet_name='stocks')
    analyst_rating = stocks['analyst rating'].tolist()
    symbols = stocks['symbol'].tolist()
    fincode_to_rating = {}
    for symbol in symbols:
        fincode = find_fincode(symbol)
        fincode_to_rating[fincode] = analyst_rating[symbols.index(symbol)]

        print(fincode, analyst_rating[symbols.index(symbol)], symbol)

    for fincode, rating in fincode_to_rating.items():
        try:
            requests.post(f"{host}stock/analyst_rating", headers={'Authorization': f'Bearer {token}'}, json={
                "fincode": fincode,
                "analyst_rating": rating
            })
            print(fincode, rating, "done")
        except Exception as e:
            print(e)

    # sheet names =  ['sector na', 'sector shariah', 'sector jain', 'sector iskcon', 'stocks', 'marketcap allocation']

    send(data, 'NA')
    continue_program('send data')
    pretty_print_dict(data)
    # send(data, 'Shariah')
    # send(data, 'Jain')
    # send(data, 'Iskcon')
