import requests
import json
import hmac
import hashlib
import time
from datetime import datetime
from sortedcontainers import SortedDict

class GMO:
    WEBSOCKET_URL = 'wss://api.coin.z.com/ws/public/v1'
    REQUEST_URL = 'https://api.coin.z.com/private'

    params = {'command': 'subscribe', 'channel': 'orderbooks', 'symbol': 'BTC_JPY'}

    @staticmethod
    def orderbook(msg: dict) -> list:
        asks = [[float(m['price']), float(m['size'])] for m in msg['asks']]
        bids = [[float(m['price']), float(m['size'])] for m in msg['bids']]
        return [asks, bids]

    def __init__(self, symbol: str, *args: tuple, **kwargs: dict):
        self.type_ = args[0] if args else None
        self.symbol = symbol
        self.keys = kwargs if kwargs else None

        self.params = {'command': 'subscribe', 'channel': 'orderbooks', 'symbol': symbol}

    def order(self, side: str, size: float, *args: tuple) -> int:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/order'
        body = {
            'symbol': self.symbol,
            'side': side,
            'executionType': self.type_,
            'size': size
        }
        if args:
            body['price'] = args[0]
        text = ts + 'POST' + path + json.dumps(body)
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.post(GMO.REQUEST_URL + path, headers=headers, data=json.dumps(body))
        return int(res.json()['data'])

    def change(self, id_: str, price: int, *args) -> None:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/changeOrder'
        body = {
            "orderId": id_,
            "price": price
        }
        text = ts + 'POST' + path + json.dumps(body)
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        requests.post(GMO.REQUEST_URL + path, headers=headers, data=json.dumps(body))
        return id_

    def cancel(self, id_) -> None:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/cancelOrder'
        body = {
            'orderId': id_
            }
        text = ts + 'POST' + path + json.dumps(body)
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        requests.post(GMO.REQUEST_URL + path, headers=headers, data=json.dumps(body))

    def settlement(self, side: str, size: float, id_: str, *args: tuple) -> None:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path      = '/v1/closeOrder'
        body = {
            "symbol": self.symbol,
            "side": side,
            "executionType": self.type_,
            "settlePosition": [
                {
                    "positionId": id_,
                    "size": size
                }
            ]
        }
        if args:
            body["price"] = args[0]
        text = ts + 'POST' + path + json.dumps(body)
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.post(GMO.REQUEST_URL + path, headers=headers, data=json.dumps(body))
        return int(res.json()['data'])

    def get_position(self) -> float:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/openPositions'
        params = {
            "symbol": self.symbol
        }
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.get(GMO.REQUEST_URL + path, headers=headers, params=params)
        if res.json()['data']:
            return sum([float(res_data['size']) for res_data in res.json()['data']['list']])
        else:
            return 0.0

    def get_remaining_money(self) -> int:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/account/assets'
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.get(GMO.REQUEST_URL + path, headers=headers)
        return int(res.json()['data'][0]['available'])

    def get_order_ids(self) -> int:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/activeOrders'
        params = {
            "symbol": self.symbol
        }
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.get(GMO.REQUEST_URL + path, headers=headers, params=params)
        if res.json()['data']:
            return [res_data['orderId'] for res_data in res.json()['data']['list']]
        else:
            return []

    def get_settlement_ids(self) -> str:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/openPositions'
        params = {
            "symbol": self.symbol
        }
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.get(GMO.REQUEST_URL + path, headers=headers, params=params)
        if res.json()['data']:
            return [res_data['positionId'] for res_data in res.json()['data']['list']]
        else:
            return []

    def get_order_num(self) -> int:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/activeOrders'
        params = {
            "symbol": self.symbol
        }
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.keys['apiKey'],
            'API-TIMESTAMP': ts,
            'API-SIGN': sign
        }
        res = requests.get(GMO.REQUEST_URL + path, headers=headers, params=params)
        if res.json()['data']:
            return len(res.json()['data']['list'])
        else:
            return 0