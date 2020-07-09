import asyncio
import datetime
import threading
import time
import websockets

latestLine = ""
clientLastWaitingAt = datetime.datetime.now()

def run_conversation():
    global latestLine
    while True:
        time.sleep(3)
        if datetime.datetime.now() - clientLastWaitingAt < datetime.timedelta(seconds=30):
            import random
            latestLine = "{}".format(random.choice(["hi", "yo", "yo mama", "wat"]))
            print(latestLine)
        else:
            print("Not conversing: no clients.")
conversationThread = threading.Thread(target=run_conversation, daemon=True)
conversationThread.start()

async def hello(websocket, path):
    lastSent = None
    global latestLine
    global clientLastWaitingAt 
    while True:
        while latestLine == lastSent:
            await asyncio.sleep(0.05)
            clientLastWaitingAt = datetime.datetime.now()
            #print("I sleep...")
        await websocket.send(latestLine)
        lastSent = latestLine

start_server = websockets.serve(hello, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()