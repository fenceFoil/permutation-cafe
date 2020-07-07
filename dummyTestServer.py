import asyncio
import datetime
import json
import os
import random
import threading
import time
import sqlite3
import subprocess
import uuid

import websockets

with open('dummyTestJson.json', 'r') as f:
    STATIC_JSON = f.read()

async def exposeMessages(websocket, path):
    while True:
        await websocket.send(STATIC_JSON)
        await asyncio.sleep(1.0)

start_server = websockets.serve(exposeMessages, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()