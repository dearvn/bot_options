from tda.auth import easy_client
from tda.orders.options import *
from tda.utils import Utils, httpx
import json, logging, requests, os, asyncio, redis
import numpy as np
from tda.orders.common import OrderType

log = logging.getLogger(__name__)

client = easy_client(
        api_key=os.environ.get("TDAMERITRADE_CLIENT_ID"),
        redirect_uri=os.environ.get("REDIRECT_URI"),
        token_path=os.environ.get("TOKEN_PATH"))

redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True)

def get_order_options(order_id, uuid = None, type = None):
    account_id = os.environ.get("TDAMERITRADE_ACCOUNT_ID")

    resp = client.get_order(order_id, account_id)
    if resp is None:
        return

    order = resp.json()

    body = {}
    datas = {}
    datas['order'] = order
    if type is not None:
        datas['type'] = type

    body[order_id] = datas

    url = os.environ.get('OPTIONS_API_URI') + "/api/option/"+uuid+"/update-order-options"
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'authorization': os.environ.get('OPTIONS_API_KEY')}
    data = json.dumps(body, cls=NpEncoder)
    resp = requests.post(url=url, data=data, headers=headers)
    print("get order options:", order_id, body)


def cancel_order_options(order_id, uuid = None, type = None):
    account_id = os.environ.get("TDAMERITRADE_ACCOUNT_ID")

    order = client.cancel_order(order_id, account_id)

    print("============order cancel:", order.json())

    body = {}
    datas = {}
    if type is not None:
        datas['type'] = type
    datas['status'] = True
    body[uuid] = datas

    url = os.environ.get('OPTIONS_API_URI') + "/api/option/"+uuid+"/cancel-order-options"
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'authorization': os.environ.get('OPTIONS_API_KEY')}
    data = json.dumps(body, cls=NpEncoder)
    resp = requests.post(url=url, data=data, headers=headers)
    print("cancel order options:", order_id, body)


def create_order_options(action, symbol, quantity, price = None, stop_price = None, uid = None, type=None):
    account_id = os.environ.get("TDAMERITRADE_ACCOUNT_ID")

    print("params - action:", action, ", symbol :", symbol, " ,quantity:", quantity, " ,price: ", price, " ,stop_price:", stop_price, " ,uid:", uid, 'type:', type)
    order_one = None
    type = ''

    entry_order_uuid = None
    exit_order_uuid = None
    if uid is not None:
        entry_order_uuid = redis_client.get("entry_order_"+uid)
        if entry_order_uuid:
            print("Exist entry "+str(entry_order_uuid))

        exit_order_uuid = redis_client.get("exit_order_" + uid)
        if exit_order_uuid:
            print("Exist exit " + str(exit_order_uuid))


    if action == 'option_buy_to_open_market' and entry_order_uuid is None:
        if stop_price is None:
            type = 'buy'
            print("buy option_buy_to_open_market")
            order_one = client.place_order(account_id, option_buy_to_open_market(symbol, quantity))
        else:
            type = 'buy'
            print("stop option_buy_to_open_market")
            if type == OrderType.STOP:
                order_one = client.place_order(account_id, option_buy_to_open_market(symbol, quantity).set_order_type(OrderType.STOP).set_stop_price(stop_price).build())
            elif type == OrderType.TRAILING_STOP:
                order_one = client.place_order(account_id, option_buy_to_open_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price(stop_price).build())

    elif action == 'option_buy_to_open_limit' and entry_order_uuid is None:
        if stop_price is None:
            type = 'buy'
            print("buy option_buy_to_open_limit")
            order_one = client.place_order(account_id, option_buy_to_open_limit(symbol, quantity, price))
        else:
            type = 'buy'
            print("buy stop option_buy_to_open_limit")
            if type == OrderType.STOP_LIMIT:
                order_one = client.place_order(account_id, option_buy_to_open_limit(symbol, quantity, price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stop_price).build())
            elif type == OrderType.TRAILING_STOP_LIMIT:
                order_one = client.place_order(account_id,option_buy_to_open_limit(symbol, quantity, price).set_order_type(OrderType.TRAILING_STOP_LIMIT).set_stop_price(stop_price).build())

    elif action == 'option_sell_to_open_market' and exit_order_uuid is None:
        type = 'sell'
        print("sell option_sell_to_open_market")
        order_one = client.place_order(account_id, option_sell_to_open_market(symbol, quantity))
    elif action == 'option_sell_to_open_limit' and exit_order_uuid is None:
        type = 'sell'
        print("sell option_sell_to_open_limit")
        order_one = client.place_order(account_id, option_sell_to_open_limit(symbol, quantity, price))
    elif action == 'option_buy_to_close_market' and entry_order_uuid is None:
        if stop_price is None:
            type = 'buy'
            print("buy option_buy_to_close_market")
            order_one = client.place_order(account_id, option_buy_to_close_market(symbol, quantity))
        else:
            type = 'buy'
            print("buy option_buy_to_close_market")
            if type == OrderType.STOP:
                order_one = client.place_order(account_id, option_buy_to_close_market(symbol, quantity).set_order_type(OrderType.STOP).set_stop_price(stop_price).build())
            elif type == OrderType.TRAILING_STOP:
                order_one = client.place_order(account_id, option_buy_to_close_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price(stop_price).build())

    elif action == 'option_buy_to_close_limit' and entry_order_uuid is None:
        if stop_price is None:
            type = 'buy'
            print("buy option_buy_to_close_limit")
            order_one = client.place_order(account_id, option_buy_to_close_limit(symbol, quantity, price))
        else:
            type = 'buy'
            print("buy stop option_buy_to_close_limit")
            if type == OrderType.STOP_LIMIT:
                order_one = client.place_order(account_id, option_buy_to_close_limit(symbol, quantity, price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stop_price).build())
            elif type == OrderType.TRAILING_STOP_LIMIT:
                order_one = client.place_order(account_id,option_buy_to_close_limit(symbol, quantity, price).set_order_type(OrderType.TRAILING_STOP_LIMIT).set_stop_price(stop_price).build())
    elif action == 'option_sell_to_close_market' and exit_order_uuid is None:
        type = 'sell'
        print("sell option_sell_to_close_market")
        order_one = client.place_order(account_id, option_sell_to_close_market(symbol, quantity))
    elif action == 'option_sell_to_close_limit' and exit_order_uuid is None:
        type = 'sell'
        print("sell option_sell_to_close_limit")
        order_one = client.place_order(account_id, option_sell_to_close_limit(symbol, quantity, price))

    if order_one is None or order_one.status_code != httpx.codes.CREATED:
        print("can not create order")
        return

    order_id = Utils(client, account_id).extract_order_id(order_one)

    if order_id is None:
        return

    body = {}
    datas = {}

    #order = client.get_order(order_id, account_id)
    #if order is not None:
    #    print("========order:", order.json())
    #    datas['order'] = order.json()

    if type == 'buy':
        datas['entry_order_id'] = order_id

    elif type == 'stop':
        datas['stop_order_id'] = order_id
    else:
        datas['exit_order_id'] = order_id


    if uid is not None:
        datas['uid'] = uid

        if type == 'buy':
            redis_client.set("entry_order_" + uid, order_id)
        elif type == 'sell':
            redis_client.delete("entry_order_" + uid)
            redis_client.set("exit_order_" + uid, order_id)

    body[symbol] = datas

    url = os.environ.get('OPTIONS_API_URI') + "/api/option/option-order-live"
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'authorization': os.environ.get('OPTIONS_API_KEY')}
    data = json.dumps(body, cls=NpEncoder)
    resp = requests.post(url=url, data=data, headers=headers)
    print("place options order live:", symbol, body)

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


