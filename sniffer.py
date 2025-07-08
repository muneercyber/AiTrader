# sniffer.py

import asyncio
import websockets
import json
from collections import defaultdict
from threading import Lock

WS_URL = "wss://try-demo-eu.po.market/socket.io/?EIO=4&transport=websocket"

class PocketOptionSniffer:
    def __init__(self):
        self.websocket = None
        self.latest_prices = defaultdict(float)  # asset -> price
        self._lock = Lock()
        self.connected = False

    async def connect(self):
        print("📡 Connecting to Pocket Option WebSocket...")
        try:
            async with websockets.connect(WS_URL) as ws:
                self.websocket = ws
                self.connected = True
                print("✅ Connected to WebSocket")
                await self.listen()
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            self.connected = False

    async def listen(self):
        async for message in self.websocket:
            self.handle_message(message)

    def handle_message(self, msg):
        # Basic Socket.IO parser for event messages starting with "42"
        if msg.startswith("42"):
            try:
                payload = json.loads(msg[2:])
                event = payload[0]
                data = payload[1] if len(payload) > 1 else None
                if event == "tick" and data:
                    asset = data.get("asset")
                    price = data.get("price")
                    if asset and price:
                        with self._lock:
                            self.latest_prices[asset] = price
                        print(f"📈 Tick update: {asset} = {price}")
            except Exception as e:
                print(f"⚠️ Failed to parse message: {e}")

    def get_price(self, asset):
        with self._lock:
            return self.latest_prices.get(asset)

# Singleton instance for import
sniffer_instance = PocketOptionSniffer()

async def start_sniffer():
    while True:
        try:
            await sniffer_instance.connect()
        except Exception as e:
            print(f"❌ Sniffer error: {e}")
        print("🔄 Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
