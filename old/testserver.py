import subprocess
import os

os.chdir('gpt2tc')
#proc = subprocess.run('echo """')
#proc = subprocess.run(['echo', '\"'])
proc = subprocess.Popen('gpt2tc.exe -m 774M -l 200 g """', stdout=subprocess.PIPE)
buffer = b""
utfErrorCount = 0 # CONSECUTIVE utf decoding errors count
for line in iter(lambda: proc.stdout.read(1), b''):
    buffer += line
    try:
        bufferStr = buffer.decode("utf-8")
        print(bufferStr)
        if bufferStr.endswith('"\r\n') and len(bufferStr) > 5:
            #proc.kill()
            break
        utfErrorCount = 0
    except:
        utfErrorCount += 1
        if utfErrorCount > 12:
            #proc.kill()
            break

proc.kill()
bufferStr = buffer.decode("utf-8")
print ("Boom! Quote: {}".format(bufferStr))