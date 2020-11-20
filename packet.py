import json
from enum import Enum

"""
Innehåller funktioner för att serialisera paket. Alla paket skapas och skickas som ett JSON objekt.
"""

class Types(Enum):
    """
    En lista med de olika packettyper, detta är en hårdkodad lista
    """

    time = 0
    play = 1
    pause = 2

def serializeCreateRoom(_alias, _name, _password, _private=False, _publicKey=None):
    """
    alias: klientens alias
    roomName: rummets namn
    password: rummets lösenord

    Skapar och retunerar ett objekt som kan skickas med packetType, alias, roomName och password.
    """
    _msg = {
        "type": Types.createRoom.value,
        "alias": _alias,
        "roomName": _name,
        "password": _password,
        "private": _private,
        "publicKey": _publicKey,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode create room message!")

    return _send

def serializeConnectRoom(_alias, _name, _password, _publicKey):
    """
    alias: klientens alias
    roomName: rummets namn
    password: rummets lösenord

    Skapar och retunerar ett objekt som kan skickas med packetType, alias, roomName och password.
    """
    _msg = {
        "type": Types.connectRoom.value,
        "roomName": _name,
        "alias": _alias,
        "password": _password,
        "publicKey": _publicKey,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode connect room message!")

    return _send

def serializeDisconnectRoom():
    """
    Skapar och retunerar ett objekt som kan skickas med packetType.
    """
    _msg = {
        "type": Types.disconnectRoom.value,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode connect room message!")

    return _send

def serializePublickey(_pKey):
    """
    alias: klientens alias
    pkey: klientens publika nyckel

    Retunerar ett objekt som kan skickas, packetType läggs även till.
    """
    _msg = {
        "type": Types.publicKey.value,
        "publicKey": _pKey,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failde to encode create public key message!")

    return _send

def serializeMessage(_alias, _message, _roomName, _signature=None):
    """
    alias: klientens alias
    message: meddelandet som ska skickas
    roomName: rummets namn

    Skapar och retunerar ett objekt som kan skickas med packetType alias, message och roomName.
    """
    _msg = {
        "type": Types.message.value,
        "message" : _message,
        "alias": _alias,
        "roomName": _roomName,
        "signature": _signature
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode create message!")
    except ValueError:
        print("Error decoding json message! ", _msg)

    return _send

def serializeRequestRoomsList():
    """
    Skapar och retunerar ett objekt som kan skickas med packettype. Kräver ingen input
    då det endast är en förfrågan.
    """
    _msg = {
        "type": Types.requestRoomsList.value,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode connected message!")
    except ValueError:
        print("Error decoding json message! ", _msg)

    return _send

def serializeSendRoomsList(_rooms):
    """
    rooms: sträng med alla rumsnamn

    Skapar och retunerar ett objekt som kan skickas med packetType samt rooms.
    """
    _msg = {
        "type": Types.roomsList.value,
        "rooms": _rooms
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode connected message!")
        print("Failed to encode connected message!")
    except ValueError:
        print("Error decoding json message! ", _msg)
        print("Error decoding json message! " + str(_msg))

    return _send

def serializeConnectedRoom(_name, _private=False):
    """
    name: rummets namn
    private: om rummet är privat eller ej

    Skickar ett paket till klienten som bekräftar att klienten är ansluten till rummet.
    """
    _msg = {
        "type": Types.connectedRoom.value,
        "roomName": _name,
        "private": _private,
    }

    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode connected message!")
    except ValueError:
        print("Error decoding json message! ", _msg)

    return _send

def serializeChatHistory(_history):
    """
    history: föregående chattmeddelanden

    Skickar chatthistoriken till nyanslutna klienter.
    """
    _msg = {
        "type": Types.chatHistory.value,
        "history": _history
    }

    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError as e:
        print("Failed to encode history message!" + str(e))
    except ValueError as e:
        print("Error decoding json message! " + str(e))

    return _send

def serializeTime(_time):
    """
    alias: klientens alias
    message: meddelandet som ska skickas
    roomName: rummets namn

    Skapar och retunerar ett objekt som kan skickas med packetType alias, message och roomName.
    """
    _msg = {
        "type": Types.time.value,
        "time" : _time,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode create message!")
    except ValueError:
        print("Error decoding json message! ", _msg)

    return _send

def serializePlay():
    """
    alias: klientens alias
    message: meddelandet som ska skickas
    roomName: rummets namn

    Skapar och retunerar ett objekt som kan skickas med packetType alias, message och roomName.
    """
    _msg = {
        "type": Types.play.value,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode create message!")
    except ValueError:
        print("Error decoding json message! ", _msg)

    return _send

def serializePause():
    """
    alias: klientens alias
    message: meddelandet som ska skickas
    roomName: rummets namn

    Skapar och retunerar ett objekt som kan skickas med packetType alias, message och roomName.
    """
    _msg = {
        "type": Types.pause.value,
    }
    try:
        _send = json.dumps(_msg).encode()
    except UnicodeError:
        print("Failed to encode create message!")
    except ValueError:
        print("Error decoding json message! ", _msg)

    return _send

def parsePacket(_packet):
    """
    Skapar och retunerar ett JSON objekt med variabler som kom i paketet
    samt packetType.
    """
    try:
        _msg = json.loads(_packet)
    except ValueError:
        print("Error decoding json message in packet! ", _packet)
        return

    return _msg
