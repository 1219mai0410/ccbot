import requests
import json
import hmac
import hashlib
import time
from datetime import datetime
from sortedcontainers import SortedDict

class bitFlyer:
    WEBSOCKET_URL = 'wss://ws.lightstream.bitflyer.com/json-rpc'
    REQUEST_URL = 'https://api.bitflyer.com/'
    asks, bids = SortedDict(), SortedDict()

    @classmethod
    def orderbook(cls, msg: dict) -> list:
        m = msg['params']['message']
        cls.__update(cls.asks, m['asks'], 1)
        cls.__update(cls.bids, m['bids'], -1)
        a = cls.asks.values()[0][0]
        b = cls.bids.values()[0][0]
        if a < b:
            cls.asks.pop(a, None)
            cls.bids.pop(b, None)
        return [cls.asks.values()[:], cls.bids.values()[:]]

    @staticmethod
    def __update(ob: SortedDict, data: list, sign: int) -> None:
        for d in data:
            p, s = float(d['price']), d['size']
            if s == 0:
                ob.pop(p * sign, None)
            else:
                ob[p * sign] = [p, s]

    def __init__(self, type_: str, symbol: str, **kwargs: dict):
        self.type_ = type_
        self.symbol = symbol
        self.keys = kwargs

        self.params = {'method': 'subscribe', 'params': {'channel': f'lightning_board_{symbol}'}}

    def order(self, side: str, size: float, *args: tuple) -> str:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/me/sendchildorder'
        body = {
            'product_code': self.symbol,
            'child_order_type': self.type_,
            'side': side,
            'size': size
            }
        if args:
            body['price'] = args[0]
        text = ts + 'POST' + path + json.dumps(body)
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY': self.keys['apiKey'],
            'ACCESS-TIMESTAMP': ts,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        res = requests.post(bitFlyer.REQUEST_URL + path, headers=headers, data=json.dumps(body))
        return res.json()['child_order_acceptance_id']

    def change(self, id_: str, *args) -> None:
        self.cancel(id_)
        if args:
            self.order(args[1], args[2], args[0])

    def cancel(self, id_: str) -> None:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/me/cancelchildorder'
        body = {
            'product_code': self.symbol,
            'child_order_acceptance_id': id_
            }
        text = ts + 'POST' + path + json.dumps(body)
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY': self.keys['apiKey'],
            'ACCESS-TIMESTAMP': ts,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        requests.post(bitFlyer.REQUEST_URL + path, headers=headers, data=json.dumps(body))

    def settlement(self, side: str, size: float, *args: tuple) -> None:
        if args:
            return self.order(side, size, args[0])
        else:
            return self.order(side, size)

    def get_position(self) -> float:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = f'/v1/me/getpositions?product_code={self.symbol}'
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY':self.keys['apiKey'],
            'ACCESS-TIMESTAMP': ts,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        res = requests.get(bitFlyer.REQUEST_URL + path, headers=headers)
        return round(sum([res_data['size'] for res_data in res.json()]), 10)

    def get_remaining_money(self) -> int:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = '/v1/me/getcollateral'
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY':self.keys['apiKey'],
            'ACCESS-TIMESTAMP': ts,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        res = requests.get(bitFlyer.REQUEST_URL + path, headers=headers)
        return int(res.json()['collateral'])

    def get_order_ids(self) -> str:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = f'/v1/me/getchildorders?product_code={self.symbol}'
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY':self.keys['apiKey'],
            'ACCESS-TIMESTAMP': ts,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        res = requests.get(bitFlyer.REQUEST_URL + path, headers=headers)
        return [res_data['child_order_acceptance_id'] for resdata in res.json()]

    def get_settlement_ids(self) -> str:
        return self.get_order_id()

    def get_order_num(self) -> int:
        ts = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = f'/v1/me/getchildorders?product_code={self.symbol}&child_order_state=ACTIVE'
        text = ts + 'GET' + path
        sign = hmac.new(bytes(self.keys['secretKey'].encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY':self.keys['apiKey'],
            'ACCESS-TIMESTAMP': ts,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        res = requests.get(bitFlyer.REQUEST_URL + path, headers=headers)
        return len(res.json())