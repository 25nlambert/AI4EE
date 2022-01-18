from subprocess import Popen
import sys
import time

#filename = sys.argv[1]
while True:
    #print("\nStarting " + filename)
    #p = Popen("python3 " + filename, shell=True)
    time.sleep(10)
    p = Popen("python3 " + "DEPLOYED_ESP32red.py", shell=True)
    p.wait()