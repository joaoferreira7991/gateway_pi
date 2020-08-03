from app import client
from threading import Thread
import os

# Implement a bash script that tries to initiate pigpiod, and this program

client_thread = Thread(target=client.start, args=(), daemon=True)
client_thread.start()

x = input("")
if x == 0:
    client_thread._stop()
    exit(0)