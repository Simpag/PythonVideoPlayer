"""This controls the ui"""
import Client

import threading

def printMessage(_json):
    _print = "<" + _json["alias"] + "> " + _json["message"]
    printToScreen(_print)

def connectedToRoom(_json):
    _print = "<Successfully connected to> " + _json["roomName"]
    printToScreen(_print)
    tempThread = threading.Thread(target=tempMenu2Func, daemon=False, name="TempThread2")
    tempThread.start()

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


def onConnection(hi):
    print(hi)
    tempThread = threading.Thread(target=tempMenu1Func, daemon=False, name="TempThread")
    tempThread.start()

def tempMenu1Func():
    _notConnectedToRoom = True
    while _notConnectedToRoom:
        _msg = """Welcome to the chatroom! 
        type 1 to list all chatrooms
        type 2 to connect to a chatroom
        type 3 to create a chatroom"""
        printToScreen(_msg)

        _input = int(input())

        if _input == 3:
            _roomName = input("Room name: ")
            _roomPassword = input("Room password: ")
            _roomPrivate = bool(input("Private room: "))
            print(_roomPrivate)
            client.createRoom(_roomName, _roomPassword, _roomPrivate)
            _notConnectedToRoom = False
        elif _input == 2:
            _roomName = input("Room name: ")
            _roomPassword = input("Room password: ")
            client.connectToRoom(_roomName, _roomPassword)
            _notConnectedToRoom = False
        else:
            client.requestRoomsList()

def tempMenu2Func():
    while True:
        _msg = input("Message: ")
        client.sendMessage(_msg)

# Simple placeholder menu
if __name__ == '__main__':
    menu1 = """Welcome to the chat app!
    Please enter the ip to the chat server: """
    printToScreen(menu1)
    ip = '192.168.1.7'  # str(input())
    menu2 = """Please enter the port to the chat server: """
    printToScreen(menu2)
    port = 1337  # int(input())
    menu3 = """Enter your alias: """
    printToScreen(menu3)
    alias = input()

    client = Client.Client()
    client.setup(alias, ip, port, onConnection, printMessage, listRooms, connectedToRoom)
    clientThread = threading.Thread(target=client.start, name="clientThread", daemon=True)
    clientThread.start()

    # Waits for the thread to finish..
    clientThread.join()
