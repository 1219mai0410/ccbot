import asyncio
import aiohttp

from ccbot.methods.method import Method
from ccbot.models.model import Model

async def ws_run_forever(
    session: aiohttp.ClientSession,
    model: Model,
    method: Method.function
    ) -> None:
    async with session.ws_connect(model.WEBSOCKET_URL) as ws:
        await ws.send_json(model.params)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                method(model.type_, model.orderbook(msg.json()))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                quit()