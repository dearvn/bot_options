from tda.auth import easy_client
from tda.streaming import StreamClient
import json, logging, requests, os, asyncio, redis
import numpy as np
from .tda_stock import retry_realtime
from websockets import exceptions

log = logging.getLogger(__name__)


redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True)

client = easy_client(
        api_key=os.environ.get("TDAMERITRADE_CLIENT_ID"),
        redirect_uri=os.environ.get("REDIRECT_URI"),
        token_path=os.environ.get("TOKEN_PATH"))
stream_client = StreamClient(client, account_id=os.environ.get("TDAMERITRADE_ACCOUNT_ID"))


def unsub_options_real_time(symbol):
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    task = loop.create_task(read_stream(symbol))
    try:
        loop.run_until_complete(task)
    except SystemExit:
        print("caught SystemExit!")
        task.exception()
        raise
    finally:
        loop.close()


async def read_stream(symbol):
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    def print_message(message):
        try:
            print("unsub")
        except AssertionError as e:
            log.exception(e)
        except Exception as e:
            log.exception(e)



    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    stream_client.add_level_one_option_handler(print_message)
    await stream_client.level_one_option_unsubs([symbol])
    error = False
    try:
        while True:
            await stream_client.handle_message()
    except asyncio.TimeoutError:
        print("=========TimeoutError")
        error = True
    except TimeoutError as e:
        print("=========TimeoutError")
        error = True
    except ConnectionRefusedError as e:
        print("=========ConnectionRefusedError")
        error = True
    except ConnectionResetError as e:
        print("=========ConnectionResetError")
        error = True
    except exceptions.ConnectionClosedOK as e:
        print("=========ConnectionClosedOK")
        error = True
    except exceptions.ConnectionClosedError as e:
        print("=========ConnectionClosedError")
        error = True
    except exceptions.InvalidMessage as e:
        print("=========InvalidMessage")
        error = True
    except OSError as e:
        print("=========OSError")
        error = True

    if error is True:
        retry_realtime(id, datas)

def retry_realtime(id, datas):
    body = {}
    body[id] = datas
    url = os.environ.get('OPTIONS_API_URI') + "/api/option/order-retry"
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'authorization': os.environ.get('OPTIONS_API_KEY')}
    data = json.dumps(body)
    resp = requests.post(url=url, data=data, headers=headers)
    print("retry order:", id, body)

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


