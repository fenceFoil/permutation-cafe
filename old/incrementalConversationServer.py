import asyncio
import datetime
import json
import os
import threading
import time
import sqlite3
import subprocess
import uuid
import websockets

serverID = str(uuid.uuid4())

def now():
    return datetime.datetime.now()

lastGeneratedID = None
def generateMessageID():
    global lastGeneratedID
    nextID = None
    while nextID == None or nextID == lastGeneratedID:
        nextID = int(round(time.time()*1000))
    lastGeneratedID = nextID
    return nextID

clientLastWaitingAt = datetime.datetime.now()
#lastMessages = {}
#nextLineID = None

previousMessages = []
#currentMessageID = None

ARCHIVE_DB_FILE = 'conversationArchive.db'

class Message():
    def __init__(self, model, message):
        self.id = generateMessageID()
        self.model = model
        self.message = message
        self.lastUpdated = now() # TODO: Shorten everywhere!
        self.finished = False
        self.hasContent = False

    def updateMessage(self, message, signalHasContent=True, finished=False):
        self.message = message
        self.finished = finished
        if signalHasContent:
            self.hasContent = True
        self.lastUpdated = now()

        # Archive finished messages
        if finished:
            self.archive()

    def archive(self):
        # Create database if it does not already exist
        if not os.path.isfile(ARCHIVE_DB_FILE):
            print('{} not found, creating new db...'.format(ARCHIVE_DB_FILE))
            conn = sqlite3.connect(ARCHIVE_DB_FILE)
            conn.execute('''CREATE TABLE Messages (
                model TEXT,
                id INTEGER,
                message TEXT,
                lastUpdated INTEGER,
                finished INTEGER,
                serverID INTEGER
            )''')
            conn.commit()
            conn.close()

        # Open database
        #info("Opening tab archive database...")
        conn = sqlite3.connect(ARCHIVE_DB_FILE)

        # Write tab data into database
        #info("Writing tab snapshot...")
        message = (
            self.model,
            self.id,
            self.message,
            int(self.lastUpdated.timestamp()*1000),
            1 if self.finished else 0,
            serverID
        )
        conn.execute("INSERT INTO Messages VALUES (?,?,?,?,?,?)", message)

        # Commit new data into database
        #info("Committing new tab archive snapshot into database...")
        conn.commit()
        conn.close()
    
    def toJSON(self):
        #print (json.dumps({"model": self.model, "id": self.id, "message": self.message, "lastUpdated": int(self.lastUpdated.timestamp()*1000), "finished": self.finished}))
        return json.dumps({"model": self.model, "id": self.id, "message": self.message, "lastUpdated": int(self.lastUpdated.timestamp()*1000), "finished": self.finished, "hasContent": self.hasContent})

def getLatestMessages(maxNum):
    global previousMessages
    # Also take the time to prune the messages list down if it's very long now
    PRUNE_LENGTH = 100
    if len(msgs) > PRUNE_LENGTH:
        msgs = sorted(previousMessages, lambda x:x.lastUpdated, reverse=True)[:PRUNE_LENGTH]
    # Sort messages by updated time and grab a few
    msgs = sorted(previousMessages, lambda x:x.lastUpdated, reverse=True)[:maxNum]
    return msgs

def getMessagesSortedByTime():
    global previousMessages
    if not previousMessages:
        return []
    return sorted(previousMessages, key=lambda x:x.lastUpdated, reverse=True)


os.chdir('gpt2tc')
currentModel = None
with open('currentModel.txt', 'r') as f:
    currentModel = f.readline().strip()

def generateLineOfConversation():
    DEBUG = False
    global previousMessages

    # TODO: Take 500 characters of previous conversation and make them the prompt, ending with \n"
    # TODO: Make sure there's a nice and bounded number of linefeed between prompts (or random if that's what was in the dataset?)
    prompt = ""
    for previousMessage in getMessagesSortedByTime():
        if previousMessage.message:
            prompt = previousMessage.message + prompt + '\n'
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
    global currentModel
    newMessage = Message(currentModel, "...")
    previousMessages.append(newMessage)
    proc = subprocess.Popen(['gpt2tc.exe', '-m', '774M', '-l', '400', 'g', prompt], stdout=subprocess.PIPE)
    buffer = b""
    bufferStr = ""
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
            else:
                newMessage.updateMessage(bufferStr[len(prompt):])
            #if bufferStr.startswith('"\r\n'):
            #    bufferStr = b"" # get rid of empty stuff at beginning
            utfErrorCount = 0
        except:
            utfErrorCount += 1
            if utfErrorCount > 12:
                break

    proc.kill()
    #bufferStr = buffer.decode("utf-8").replace('\r', '')
    #print("Output: "+bufferStr)
    newText = bufferStr[len(prompt):]
    print ("Generated: "+newText)
    newMessage.updateMessage(newText, finished=True)

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
    printingDots = False
    while True:
        #time.sleep(3)
        time.sleep(0.5)
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
            printingDots=False
        else:
            if not printingDots:
                print("Not conversing: no clients.")
                printingDots = True
            else:
                print (".", end="")
conversationThread = threading.Thread(target=run_conversation, daemon=True)
conversationThread.start()

async def exposeMessages(websocket, path):
    def getLatestMessageUpdate():
        msgs = getMessagesSortedByTime()
        if msgs and len(msgs) >= 1:
            return msgs[0].lastUpdated
        else:
            return 0

    global previousMessages

    lastUpdateSent = 0
    global clientLastWaitingAt
    while True:
        while lastUpdateSent == getLatestMessageUpdate():
            await asyncio.sleep(0.05)
            clientLastWaitingAt = now()
        await websocket.send("["+','.join([m.toJSON() for m in getMessagesSortedByTime()[:5]])+"]")
        lastUpdateSent = getLatestMessageUpdate()
        # Rate limiting
        await asyncio.sleep(1.0/5)



    # global previousLines
    # lastSent = max(max(list(previousLines.keys())+[0])-3, 0)
    # global clientLastWaitingAt 
    # while True:
    #     while not lastSent+1 in previousLines.keys():
    #         await asyncio.sleep(0.05)
    #         clientLastWaitingAt = datetime.datetime.now()
    #         #print("I sleep...")
    #     await websocket.send(previousLines[lastSent+1])
    #     lastSent += 1

start_server = websockets.serve(exposeMessages, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()