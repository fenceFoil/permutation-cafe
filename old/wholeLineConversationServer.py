import asyncio
import datetime
import os
import threading
import time
import subprocess
import websockets

clientLastWaitingAt = datetime.datetime.now()
previousLines = {}
nextLineID = 1

os.chdir('gpt2tc')
currentModel = None
with open('currentModel.txt', 'r') as f:
    currentModel = f.readline().strip()

def generateLineOfConversation():
    DEBUG = False
    global previousLines, nextLineID

    # TODO: Take 500 characters of previous conversation and make them the prompt, ending with \n"
    prompt = ""
    for previousLineID in sorted(list(previousLines.keys()), reverse=True):
        previousLine = previousLines[previousLineID]
        prompt = previousLine + prompt+'\n'
        if len(prompt) > 500:
            prompt = prompt[-500:]
            break
    if len(prompt) <= 0:
        prompt = '"'

    # TODO: Uncap length
    # TODO: Post process to change ending commas to periods
    # TODO: post process to make sure the final new line start with a double quote
    # TODO: Vulnerable to invalid UTF8 on line 57 )decoding after loop)
    # TODO: When we run past the end of memory, we get the time=1.11 word/s text and no endquote. Consider cropping to last fullstop sentence.
    proc = subprocess.Popen(['gpt2tc.exe', '-m', '774M', '-l', '200', 'g', prompt], stdout=subprocess.PIPE)
    buffer = b""
    unprintedBuffer = b""
    utfErrorCount = 0 # CONSECUTIVE utf decoding errors count
    for line in iter(lambda: proc.stdout.read(1), b''):
        buffer += line
        try:
            bufferStr = buffer.decode("utf-8").replace('\r', '')
            if DEBUG:
                print(bufferStr)
            if bufferStr.endswith('"\n') and len(bufferStr) > 5+len(prompt):
                break
            #if bufferStr.startswith('"\r\n'):
            #    bufferStr = b"" # get rid of empty stuff at beginning
            utfErrorCount = 0
        except:
            utfErrorCount += 1
            if utfErrorCount > 12:
                break

    proc.kill()
    bufferStr = buffer.decode("utf-8").replace('\r', '')
    if DEBUG:
        print ("Boom! Quote: {}".format(bufferStr))
    else:
        #print("Output: "+bufferStr)
        newText = bufferStr[len(prompt):]
        print ("Generated: "+newText)
        previousLines[nextLineID] = newText
        nextLineID += 1

MODELS = [
    'dialog-lankhmar-all-774M-1000',
    'dialog-permutationCity-774M-2-300'
]
CURR_MODEL_INDEX = 0

def selectModel(model):
    global currentModel
    if currentModel != model:
        os.rename('gpt2_774M.bin', currentModel+'.bin')
        os.rename(model+'.bin', 'gpt2_774M.bin')
        currentModel = model
        with open('currentModel.txt', 'w') as f:
            f.write(model)

def run_conversation():
    global latestLine
    while True:
        time.sleep(3)
        if datetime.datetime.now() - clientLastWaitingAt < datetime.timedelta(seconds=30):
            # Generate a line of conversation

            # Choose model
            global CURR_MODEL_INDEX, MODELS
            CURR_MODEL_INDEX = (CURR_MODEL_INDEX+1)%len(MODELS)
            print("Switching model to: {}".format(MODELS[CURR_MODEL_INDEX]))
            selectModel(MODELS[CURR_MODEL_INDEX])
            # Run inference
            print("Running inference.")
            generateLineOfConversation()
        else:
            print("Not conversing: no clients.")
conversationThread = threading.Thread(target=run_conversation, daemon=True)
conversationThread.start()

async def hello(websocket, path):
    global previousLines
    lastSent = max(max(list(previousLines.keys())+[0])-3, 0)
    global clientLastWaitingAt 
    while True:
        while not lastSent+1 in previousLines.keys():
            await asyncio.sleep(0.05)
            clientLastWaitingAt = datetime.datetime.now()
            #print("I sleep...")
        await websocket.send(previousLines[lastSent+1])
        lastSent += 1

start_server = websockets.serve(hello, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()