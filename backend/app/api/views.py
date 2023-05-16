import logging, os, json, redis
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from worker.tasks import get_order_options_exe, create_order_options_exe, cancel_order_options_exe, post_suboptions_exe, post_unsuboptions_exe, post_options_stream_exe, post_quote_stream_exe, post_option_chain_exe, post_quote_exe, post_open_exe, post_expirations_exe, post_setting_exe

logger = logging.getLogger(__name__)
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True)

@api_view(['POST'])
def post_setting(request, format=None):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        data = request.data
        post_setting_exe.delay(data['key'], data['value'])
        return Response(data, status=status.HTTP_201_CREATED)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def post_suboptions(request, format=None):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        data = request.data
        if ('id' in data):
            post_suboptions_exe.delay(data['id'], data['data'])
            return Response(data, status=status.HTTP_201_CREATED)

    return Response('', status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def post_unsuboptions(request, format=None):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        data = request.data
        if ('symbol' in data):
            post_unsuboptions_exe.delay(data['symbol'])
            return Response(data, status=status.HTTP_201_CREATED)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_expirations(request):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'tickers' in data:
            for ticker in data['tickers']:
                post_expirations_exe.delay(ticker)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_option_chain(request):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'ticker' in data:
            rule_id = data['rule_id'] if 'rule_id' in data else ''
            proxy = data['proxy'] if 'proxy' in data else None
            days = int(data['d']) if 'd' in data else None
            post_option_chain_exe.delay(data['ticker'], days, rule_id, proxy)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_quote(request):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'tickers' in data:
            for ticker in data['tickers']:
                if 'stream' in data:
                    post_quote_stream_exe.delay(ticker)
                else:
                    post_quote_exe.delay(ticker)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_quote_stream(request):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'ticker' in data:
            post_quote_stream_exe.delay(data['ticker'])

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_options_stream(request):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'ticker' in data and 'symbols' in data:
            post_options_stream_exe.delay(data['ticker'], data['symbols'])

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_open(request):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'tickers' in data:
            for ticker in data['tickers']:
                post_open_exe.delay(ticker)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def create_order_options(request, format=None):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        data = request.data
        if 'ticker' in data:
            price = None
            if 'price' in data:
                price = float(data['price'])
            stop_price = None
            if 'stop_price' in data:
                stop_price = float(data['stop_price'])
            uuid = None
            if 'uuid' in data:
                uuid = data['uuid']
            type = None
            if 'type' in data:
                type = data['type']
            qty = int(data['qty'])
            create_order_options_exe.delay(data['action'], data['ticker'], qty, price, stop_price, uuid, type)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def get_order_options(request, format=None):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        data = request.data
        if 'order_id' in data:
            uuid = None
            if 'uuid' in data:
                uuid = data['uuid']

            type = None
            if 'type' in data:
                type = data['type']

            get_order_options_exe.delay(data['order_id'], uuid, type)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def cancel_order_options(request, format=None):
    key = os.environ.get('OPTIONS_API_KEY')

    if request.META['HTTP_AUTHORIZATION'] == None or key != request.META['HTTP_AUTHORIZATION']:
        return Response('', status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        data = request.data
        if 'order_id' in data:
            uuid = None
            if 'uuid' in data:
                uuid = data['uuid']

            type = None
            if 'type' in data:
                type = data['type']
            cancel_order_options_exe.delay(data['order_id'], uuid, type)

        return Response(data, status=status.HTTP_200_OK)

    return Response('', status=status.HTTP_403_FORBIDDEN)