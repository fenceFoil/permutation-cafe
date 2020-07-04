# Run gpt2tc to get a whole line of dialog and output all at once.

import subprocess
import os

DEBUG = False

os.chdir('gpt2tc')
proc = subprocess.Popen('gpt2tc.exe -m 774M -l 200 g """', stdout=subprocess.PIPE)
buffer = b""
unprintedBuffer = b""
utfErrorCount = 0 # CONSECUTIVE utf decoding errors count
for line in iter(lambda: proc.stdout.read(1), b''):
    buffer += line
    try:
        bufferStr = buffer.decode("utf-8")
        if DEBUG:
            print(bufferStr)
        if bufferStr.endswith('"\r\n') and len(bufferStr) > 5:
            break
        if bufferStr.startswith('"\r\n'.encode('utf-8')):
            bufferStr = b"" # get rid of empty stuff at beginning
        utfErrorCount = 0
    except:
        utfErrorCount += 1
        if utfErrorCount > 12:
            break

proc.kill()
bufferStr = buffer.decode("utf-8")
if DEBUG:
    print ("Boom! Quote: {}".format(bufferStr))
else:
    print (bufferStr)