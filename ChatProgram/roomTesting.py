from time import sleep

import Client
import threading
import random

def printMessage(_json):
    _print = "<" + _json["alias"] + "> " + _json["message"]
    print(_print)

def connectedToRoom(_json):
    _print = "<Successfully connected to> " + _json["roomName"]
    print(_print)

def listRooms(_json):
    try:
        _print = "Available rooms: \n"
        _rooms = _json["rooms"]
        for _room in _rooms:
            _print += _room + "\n"

        printToScreen(_print)
        _input = input()
        # Todo send selected room to server...
    except KeyError:
        printToScreen("No rooms!")


def printToScreen(_print):
    print(_print)


def onConnection(ignore):
    client.createRoom("Test " + str(random.randint(0, 100000000)), "123", False)


if __name__ == '__main__':
    """
    Skapar en massa rum...
    """
    ip = 'localhost'  # str(input())
    port = 1337  # int(input())
    alias = "testing"

    clients = []
    for _i in range(20):
        client = Client.Client()
        client.setup(alias, ip, port, onConnection, printMessage, listRooms, connectedToRoom)
        clientThread = threading.Thread(target=client.start, name="clientThread" + str(_i), daemon=True)
        clientThread.start()
        sleep(0.5)

    clientThread.join()
