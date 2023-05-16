from tda.auth import easy_client
from tda.streaming import StreamClient
import json, logging, requests, os, asyncio
from .tda_stock import retry_realtime
from websockets import exceptions

log = logging.getLogger(__name__)

client = easy_client(
        api_key=os.environ.get("TDAMERITRADE_CLIENT_ID"),
        redirect_uri=os.environ.get("REDIRECT_URI"),
        token_path=os.environ.get("TOKEN_PATH"))
stream_client = StreamClient(client, account_id=os.environ.get("TDAMERITRADE_ACCOUNT_ID"))


def run_quote_real_time(tickers):
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    task = loop.create_task(read_stream(tickers))
    try:
        loop.run_until_complete(task)
    except SystemExit:
        print("caught SystemExit!")
        task.exception()
        raise
    finally:
        loop.close()


async def read_stream(symbols):
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
    #await stream_client.level_one_equity_subs(StreamClient.QOSLevel.EXPRESS)

    def print_message(message):
        try:
            # print(message['content'][0])
            if message['content'] and message['content'][0] and 'key' in message['content'][0] and 'LAST_PRICE' in message['content'][0]:
                #print(message['content'][0])
                open = message['content'][0]['LAST_PRICE']
                ticker = message['content'][0]['key']
                body = {}
                params = {'open': open}
                if 'CLOSE_PRICE' in message['content'][0]:
                    last_open = message['content'][0]['CLOSE_PRICE']
                    params['last_open'] = last_open

                body[ticker] = params
                url = os.environ.get('OPTIONS_API_URI') + "/ticker/realtime-open"
                headers = {'content-type': 'application/json',
                           'accept': 'application/json',
                           'authorization': os.environ.get('OPTIONS_API_KEY')}
                data = json.dumps(body)
                resp = requests.post(url=url, data=data, headers=headers)
                print("post-realtime-quote-ticker:", resp)

        except AssertionError as e:
            log.exception(e)
        except Exception as e:
            log.exception(e)



    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    #stream_client.add_nasdaq_book_handler(print_message)
    #stream_client.add_level_one_equity_handler(print_message)
    stream_client.add_level_one_equity_handler(print_message)
    #await stream_client.nasdaq_book_subs(['SPY'])
    #await stream_client.level_one_equity_subs(['SPY'])
    await stream_client.level_one_equity_subs(symbols)
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
        for symbol in symbols:
            retry_realtime(symbol, 'quote')





