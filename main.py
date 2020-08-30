from app import client
from threading import Thread
import os

client_thread = Thread(target=client.start, args=())
client_thread.start()