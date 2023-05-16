"""
Implementation of various trading strategies.

"""
import json, math, os, json, logging, pytz, redis, statistics, numpy, time
import requests, random
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import pandas_ta as ta
#from tda import auth, client
#from sklearn.cluster import KMeans
from .yfoption import Option
from tdameritrade.client import TDClient

log = logging.getLogger(__name__)
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True)


def get_data_ticker(ticker, interval):
    c = TDClient()
    period_type = 'day'
    period = 1
    frequency_type = 'minute'
    frequency = 1

    if (interval == '5m'):
        frequency = 5
        period = 2
    elif (interval == '10m'):
        frequency = 10
        period = 5
    elif (interval == '15m'):
        frequency = 15
        period = 7
    elif (interval == '30m'):
        frequency = 30
        period = 10
    elif (interval == '1h'):
        frequency = 30
        period = 2
    elif (interval == '1d'):
        period_type = 'month'
        period = 6
        frequency_type = 'daily'
        frequency = 1

    resp = c.history(symbol=ticker,
                               periodType=period_type,
                               period=period,
                               frequencyType=frequency_type,
                               frequency=frequency)

    if 'candles' not in resp:
        return None
    candles = resp['candles']

    if (interval == '1h'):
        datas = []
        for item in candles:
            date_time = datetime.fromtimestamp(item['datetime'] / 1000)
            m = date_time.minute
            if m == 0:
                datas.append(item)
    else:
        datas = candles

    now = datetime.now(pytz.timezone("America/Los_Angeles"))
    h = now.hour
    m = now.minute
    if interval != '1m' and (m >= 30 and h == 6 or h > 6 and h <= 19):
        quote = c.quote(ticker)
        if quote is not None and quote[ticker]:
            quote = quote[ticker]
            s = {"close": float(quote['lastPrice']), "open": float(quote['openPrice']),
                 "high": float(quote['highPrice']),
                 "low": float(quote['lowPrice']), "volume": int(quote['totalVolume']),
                 "datetime": int(quote['tradeTimeInLong'])}
            datas.append(s)

    return datas


def post_quote(ticker):
    try:
        c = TDClient()
        quote = c.quote(ticker)
        if quote is None or not quote[ticker]:
            return

        quote = quote[ticker]
        body = {ticker: quote}
        url = os.environ.get('OPTIONS_API_URI') + "/ticker/realtime-quote"
        headers = {'content-type': 'application/json',
                   'accept': 'application/json',
                   'authorization': os.environ.get('OPTIONS_API_KEY')}
        data = json.dumps(body, cls=NpEncoder)
        resp = requests.post(url=url, data=data, headers=headers)
        print("post-realtime-quote-ticker:", resp)

    except AssertionError as e:
        log.exception(e)
    except Exception as e:
        log.exception(e)


def post_open(ticker):
    try:
        datas = get_data_ticker(ticker, '1d')
        if len(datas) > 0:
            open = datas[-1]['close']
            last_open = datas[-2]['close']

            body = {ticker: {'open': open, 'last_open': last_open}}

            url = os.environ.get('OPTIONS_API_URI') + "/ticker/realtime-open"
            headers = {'content-type': 'application/json',
                       'accept': 'application/json',
                       'authorization': os.environ.get('OPTIONS_API_KEY')}
            data = json.dumps(body, cls=NpEncoder)
            resp = requests.post(url=url, data=data, headers=headers)
            print("post-realtime-quote-ticker:", resp)

    except AssertionError as e:
        log.exception(e)
    except Exception as e:
        log.exception(e)


def get_option_chain_ticker(ticker, days=None, proxy=None):
    df = None
    try:
        c = TDClient()
        df = c.options(ticker, fromDate=time.strftime("%Y-%m-%d"))

    except AssertionError as e:
        print("error 1", e)
        log.exception(e)
    except Exception as e:
        print("error 2", e)
        log.exception(e)

    if df is None:
        return None
    interval = days if days is not None else 1
    date_to = datetime.now(pytz.timezone("America/Los_Angeles")) + timedelta(days=interval)
    date_to = date_to.strftime('%Y-%m-%d')

    put_exp = df['putExpDateMap']
    puts = {}
    for date, put in put_exp.items():
        dates = date.split(":")
        date_expiration = dates[0]

        if date_to < date_expiration:
            continue

        itemputs = {}
        for strike, itemstrikes in put.items():
            if strike[-2:] == '.0':
                strike = round(float(strike))
            itemstrike = itemstrikes[0]
            itemput = {
                'strike': strike,
                'put': {
                    'contractSymbol': itemstrike['symbol'],
                    'strike': strike,
                    'lastPrice': itemstrike['last'],
                    'change': itemstrike['netChange'],
                    'percentChange': itemstrike['percentChange'],
                    'volume': itemstrike['totalVolume'],
                    'openInterest': itemstrike['openInterest'],
                    'impliedVolatility': itemstrike['volatility'],
                    'open': itemstrike['openPrice'],
                    'high': itemstrike['highPrice'],
                    'low': itemstrike['lowPrice'],
                    'close': itemstrike['closePrice'],
                    'date': itemstrike['tradeTimeInLong'],
                    'bid': itemstrike['bid'],
                    'ask': itemstrike['ask']
                }
            }
            itemputs[strike] = itemput
        puts[date_expiration] = itemputs

    callExp = df['callExpDateMap']
    calls = {}
    for date, call in callExp.items():
        dates = date.split(":")
        date_expiration = dates[0]

        if date_to < date_expiration:
            continue

        put = puts[date_expiration] if date_expiration in puts else {}
        itemcalls = []
        for strike, itemstrikes in call.items():
            if strike[-2:] == '.0':
                strike = round(float(strike))
            itemstrike = itemstrikes[0]
            itemcall = {
                'strike': strike,
                'call': {
                    'contractSymbol': itemstrike['symbol'],
                    'strike': strike,
                    'lastPrice': itemstrike['last'],
                    'change': itemstrike['netChange'],
                    'percentChange': itemstrike['percentChange'],
                    'volume': itemstrike['totalVolume'],
                    'openInterest': itemstrike['openInterest'],
                    'impliedVolatility': itemstrike['volatility'],
                    'open': itemstrike['openPrice'],
                    'high': itemstrike['highPrice'],
                    'low': itemstrike['lowPrice'],
                    'close': itemstrike['closePrice'],
                    'date': itemstrike['tradeTimeInLong'],
                    'bid': itemstrike['bid'],
                    'ask': itemstrike['ask']
                },
                'put': put[strike]['put'] if strike in put else {}
            }
            itemcalls.append(itemcall)
        calls[date_expiration] = itemcalls

    return calls

def post_option_chain_ticker(ticker, days=None, rule_id=None, proxy=None):
    try:
        options = get_option_chain_ticker(ticker, days, proxy)
        if options == None:
            return

        i = 0
        for date, option in options.items():
            data = {'options': option, 'i': i}
            if rule_id:
                data['rule_id'] = rule_id
            body = {ticker + "-" + date: data}
            url = os.environ.get('OPTIONS_API_URI') + "/options/realtime-price"
            headers = {'content-type': 'application/json',
                       'accept': 'application/json',
                       'authorization': os.environ.get('OPTIONS_API_KEY')}
            data = json.dumps(body, cls=NpEncoder)
            resp = requests.post(url=url, data=data, headers=headers)
            print("post-realtime-option-chain:", ticker+"-"+date, resp)
            i = i + 1

    except AssertionError as e:
        log.exception(e)
    except Exception as e:
        log.exception(e)


def post_expirations_ticker(ticker):
    try:
        options = get_expirations_ticker(ticker)

        if options is None:
            return
        body = {ticker: options}
        url = os.environ.get('OPTIONS_API_URI') + "/options/realtime-expirations"
        headers = {'content-type': 'application/json',
                   'accept': 'application/json',
                   'authorization': os.environ.get('OPTIONS_API_KEY')}
        data = json.dumps(body, cls=NpEncoder)
        resp = requests.post(url=url, data=data, headers=headers)
        print("post-realtime-expirations-ticker:", resp)

    except AssertionError as e:
        log.exception(e)
    except Exception as e:
        log.exception(e)


def get_expirations_ticker(ticker):
    opt = Option(ticker)
    return opt.options


def retry_realtime(ticker, type = None):
    body = {}
    body[ticker] = {'type': type}
    url = os.environ.get('OPTIONS_API_URI') + "/api/option/realtime-retry"
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'authorization': os.environ.get('OPTIONS_API_KEY')}
    data = json.dumps(body)
    resp = requests.post(url=url, data=data, headers=headers)
    print("retry call:", ticker, body)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_)):
            return int(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)