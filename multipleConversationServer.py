import asyncio
import datetime
import json
import os
import platform
import random
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

activeConversations = []

ARCHIVE_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'multiConversationArchive.db')
# Create database if it does not already exist
if not os.path.isfile(ARCHIVE_DB_FILE):
    print('{} not found, creating new db...'.format(ARCHIVE_DB_FILE))
    conn = sqlite3.connect(ARCHIVE_DB_FILE)
    conn.execute('''CREATE TABLE Messages (
        model TEXT,
        id INTEGER,
        message TEXT,
        lastUpdated INTEGER,
        createdTime INTEGER,
        finished INTEGER,
        serverID INTEGER,
        prompt TEXT,
        conversationID TEXT
    )''')
    conn.execute('''CREATE TABLE Conversations (
        id TEXT,
        createdTime INTEGER,
        serverID INTEGER
    )''')
    conn.execute('''CREATE TABLE ConversationParticipantActivity (
        conversationID TEXT,
        activityTime INTEGER,
        participant TEXT,
        isArrival INTEGER,
        isDeparture INTEGER
    )''')
    conn.commit()
    conn.close()

class Conversation():
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.createdTime = now()
        self.messages = []
        self.participants = []

        # Archive self into database
        conn = sqlite3.connect(ARCHIVE_DB_FILE)
        message = (
            self.id,
            int(self.createdTime.timestamp()*1000),
            serverID
        )
        conn.execute("INSERT INTO Conversations VALUES (?,?,?)", message)
        conn.commit()
        conn.close()

    def addParticipant(self, model):
        self.participants.append(model)

        # Write new participant changes into database
        conn = sqlite3.connect(ARCHIVE_DB_FILE)
        message = (
            self.id,
            int(now().timestamp()*1000),
            model,
            1,
            0
        )
        conn.execute("INSERT INTO ConversationParticipantActivity VALUES (?,?,?,?,?)", message)
        conn.commit()
        conn.close()

    def addMessage(self, message):
        self.messages.append(message)

    def getLatestMessages(self, maxNum):
        # Sort messages by updated time and grab a few
        msgs = sorted(self.messages, lambda x:x.lastUpdated, reverse=True)[:maxNum]
        return msgs

    def getMessagesSortedByTime(self):
        return sorted(self.messages, key=lambda x:x.lastUpdated, reverse=True)

    def encodeForWebsite(self):
        return {
            "id": self.id,
            "messages": [m.encodeForWebsite() for m in self.messages],
            "participants": self.participants
        }

class Message():
    def __init__(self, model, message):
        self.id = generateMessageID()
        self.model = model
        self.message = message
        self.lastUpdated = now()
        self.finished = False
        self.hasContent = False
        self.createdTime = now()
        self.prompt = None

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
            int(self.createdTime.timestamp()*1000),
            1 if self.finished else 0,
            serverID,
            self.prompt,
            findConversationByParticipant(self.model).id
        )
        conn.execute("INSERT INTO Messages VALUES (?,?,?,?,?,?,?,?,?)", message)

        # Commit new data into database
        #info("Committing new tab archive snapshot into database...")
        conn.commit()
        conn.close()
    
    #def toJSON(self):
    #    #print (json.dumps({"model": self.model, "id": self.id, "message": self.message, "lastUpdated": int(self.lastUpdated.timestamp()*1000), "finished": self.finished}))
    #    return json.dumps({"model": self.model, "id": self.id, "message": self.message, "lastUpdated": int(self.lastUpdated.timestamp()*1000), "finished": self.finished, "hasContent": self.hasContent})

    def encodeForWebsite(self):
        return {
            "model": self.model,
            "id": self.id,
            "message": self.message,
            "lastUpdated": int(self.lastUpdated.timestamp()*1000), 
            "finished": self.finished, 
            "hasContent": self.hasContent
        }



os.chdir('gpt2tc')
currentModel = None
with open('current774MModel.txt', 'r') as f:
    currentModel = f.readline().strip()

def generateLineOfConversation(conversation, model):
    DEBUG = False

    # TODO: Take 500 characters of previous conversation and make them the prompt, ending with \n"
    # TODO: Make sure there's a nice and bounded number of linefeed between prompts (or random if that's what was in the dataset?)
    prompt = ""
    for previousMessage in conversation.getMessagesSortedByTime():
        if previousMessage.message and len(previousMessage.message.strip())>2:
            prompt = previousMessage.message.strip() + '\r\n' + prompt
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
    newMessage = Message(model, "...")
    conversation.addMessage(newMessage)
    newMessage.prompt = prompt
    proc = subprocess.Popen(['gpt2tc.exe' if platform.system() == 'Windows' else 'gpt2tc', '-m', '774M', '-l', '400', 'g', prompt], stdout=subprocess.PIPE)
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
                newMessage.updateMessage(('"' if prompt == '"' else '') + bufferStr[len(prompt):])
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
    newText = ('"' if prompt == '"' else '') + bufferStr[len(prompt):]
    print ("Generated: "+newText)
    newMessage.updateMessage(newText, finished=True)

MODELS = [
    {
        'cover': 'lankhmarCover.jpg',
        'id': 'dialog-lankhmar-all-774M-1000',
        'title': 'Fafhrd and the Gray Mouser',
        'author': 'Fritz Leiber'
    },
    {
        'cover': 'permutationCityCover.jpg',
        'id': 'dialog-permutationCity-774M-2-300',
        'title': 'Permutation City',
        'author': 'Greg Egan'
    },
    {
        'cover': 'hitchhikerCover.jpg',
        'id': 'dialog-hitchhikerAll-774M-700',
        'title': 'The Hitchhiker''s Guide to the Galaxy Trilogy',
        'author': 'Douglas Adams'
    },
    {
        'cover': 'barsoomCover.jpg',
        'id': 'dialog-marsSeries-774M-600',
        'title': 'The Barsoom Series',
        'author': 'Edgar Rice Burroughs'
    },
    {
        'cover': '50shadesCover.jpg',
        'id': 'dialog-50shades-774M-1200',
        'title': '50 Shades of Grey',
        'author': 'E. L. James'
    },
]
MODEL_IDS = [participant['id'] for participant in MODELS]

lastSpeakerModel = None
def selectNextSpeaker():
    """Choose next speaker from among the active conversations. Don't repeat. """
    # TODO: Consider making deck persistant and reshuffle/deal again only once empty
    global lastSpeakerModel
    activeParticipants = []
    for conversation in activeConversations:
        for participant in conversation.participants:
            if participant != lastSpeakerModel:
                activeParticipants.append(participant)
    chosenOne = random.choice(activeParticipants)
    lastSpeakerModel = chosenOne
    return chosenOne

def findConversationByParticipant(model):
    for c in activeConversations:
        if model in c.participants:
            return c
    return None

def selectModel(model):
    global currentModel
    if currentModel != model:
        os.rename('gpt2_774M.bin', currentModel+'.bin')
        os.rename(model+'.bin', 'gpt2_774M.bin')
        currentModel = model
        with open('current774MModel.txt', 'w') as f:
            f.write(model)

def startConversations():
    """Start two static conversations that run forever, erasing old ones"""

    global activeConversations
    activeConversations = []
    for i in range(2):
        con = Conversation()
        activeConversations.append(con)
    # Deal out the models like cards into the conversations
    shuffledModelDeck = MODEL_IDS.copy()
    random.shuffle(shuffledModelDeck)
    currConversation = 0
    while len(shuffledModelDeck) > 0:
        model = shuffledModelDeck.pop(0)
        activeConversations[currConversation].addParticipant(model)
        currConversation = (currConversation+1)%len(activeConversations)

def run_conversations():
    """Blocking method that updates conversations with new messages and drifting participants forever"""

    startConversations()

    while True:
        time.sleep(0.5)

        # Check for viewers, wait for them to appear if there are none
        savedClientLastWaitingAt = clientLastWaitingAt
        if now() - clientLastWaitingAt > datetime.timedelta(seconds = 60):
            print ("Not conversing: no clients viewing.")
            while clientLastWaitingAt == savedClientLastWaitingAt:
                time.sleep(0.5)

        # Generate another message
        nextParticipant = selectNextSpeaker()
        print ("Switching model to: {}".format(nextParticipant))
        selectModel(nextParticipant)
        print ("Running inference.")
        generateLineOfConversation(findConversationByParticipant(nextParticipant), nextParticipant)

conversationThread = threading.Thread(target=run_conversations, daemon=True)
conversationThread.start()

async def exposeMessages(websocket, path):
    # Push static information once to the client
    await websocket.send(json.dumps({'participantsMetadata':MODELS}))

    # Then push ongoing changes...
    def getLatestMessageUpdateTime():
        # Pull messages from all active conversations and return the latest update time found
        latestFound = 0
        for c in activeConversations:
            for m in c.messages:
                t = m.lastUpdated.timestamp()
                if latestFound < t:
                    latestFound = t
        return latestFound

    lastUpdateSent = 0
    global clientLastWaitingAt
    while True:
        latestTime = lastUpdateSent
        while lastUpdateSent == latestTime:
            await asyncio.sleep(0.05)
            clientLastWaitingAt = now()
            latestTime = getLatestMessageUpdateTime()
        # Send an update to webpages: a list of all active conversations and enough data to display them
        lastUpdateSent = latestTime
        await websocket.send(json.dumps({'update':[c.encodeForWebsite() for c in activeConversations]}))
        # Rate limiting
        await asyncio.sleep(1.0/5)

start_server = websockets.serve(exposeMessages, "localhost", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()