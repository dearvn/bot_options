from __future__ import absolute_import
import os,json,logging,redis

from .worker import app

from .quote_stream_tda import run_quote_real_time
from .options_stream_tda import run_options_real_time
from .options_sub_tda import sub_options_real_time
from .options_unsub_tda import unsub_options_real_time
from .options_order_tda import get_order_options, create_order_options, cancel_order_options

from .tda_stock import post_quote, post_open, post_option_chain_ticker, post_expirations_ticker
logger = logging.getLogger(__name__)
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True)


@app.task(bind=True, name='post_options_stream_exe', default_retry_delay=10)
def post_options_stream_exe(self, ticker, symbols):
    try:
        run_options_real_time(ticker, symbols)
    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='post_suboptions_exe', default_retry_delay=10)
def post_suboptions_exe(self, id, datas):
    try:
        sub_options_real_time(id, datas)
    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='post_unsuboptions_exe', default_retry_delay=3)
def post_unsuboptions_exe(self, symbol):
    try:
        unsub_options_real_time(symbol)
    except Exception as exc:
        raise self.retry(exc=exc)



@app.task(bind=True, name='post_quote_stream_exe', default_retry_delay=10)
def post_quote_stream_exe(self, ticker):
    try:
        run_quote_real_time([ticker])
    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='reset_ticker_exe', default_retry_delay=10)
def reset_ticker_exe(self, tickers):
    try:
        redis_client.delete('tickers')
        redis_client.set('tickers', json.dumps(tickers))

    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='post_option_chain_exe', default_retry_delay=10)
def post_option_chain_exe(self, ticker, days=None, rule_id=None, proxy=None):
    try:
        print(">>>>>>>>>>>>>>>>go task")
        post_option_chain_ticker(ticker, days, rule_id, proxy)

    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='post_expirations_exe', default_retry_delay=10)
def post_expirations_exe(self, ticker):
    try:
        post_expirations_ticker(ticker)

    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='post_open_exe', default_retry_delay=10)
def post_open_exe(self, ticker):
    try:
        post_open(ticker)

    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='post_quote_exe', default_retry_delay=10)
def post_quote_exe(self, ticker):
    try:
        post_quote(ticker)

    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, name='post_setting_exe', default_retry_delay=10)
def post_setting_exe(self, key, value):
    try:
        if (key):
            value = json.dumps(value) if isinstance(value, list) else value
            redis_client.set(key, value)

    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='create_order_options_exe', default_retry_delay=3)
def create_order_options_exe(self, action, ticker, qty = 1, price = None, stop_price = None, uid = None, type=None):
    try:
        create_order_options(action, ticker, qty, price, stop_price, uid, type)

    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, name='get_order_options_exe', default_retry_delay=3)
def get_order_options_exe(self, order_id, uuid = None, type = None):
    try:
        get_order_options(order_id, uuid, type)

    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(bind=True, name='cancel_order_options_exe', default_retry_delay=3)
def cancel_order_options_exe(self, order_id, uuid = None, type = None):
    try:
        cancel_order_options(order_id, uuid, type)

    except Exception as exc:
        raise self.retry(exc=exc)

