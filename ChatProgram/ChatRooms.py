import logging
import os
import uuid

class ChatRoom:
    """
    Detta är en klass som håller reda på information om ett chattrum.
    """
    def __init__(self, _name, _password, _private=False):
        """
        namne: rummets namn
        password: rummets lösenord
        private: om rummet ska vara privat

        Sparar variablerna som matas in samt skapar en dictionary som sparar anslutna klienter.
        """
        self.name = _name
        self.password = _password
        self.private = _private
        # Dict of connection : public key
        self.connections = {}
        self.uuid = uuid.uuid1()

    def addConnection(self, _connection, _publicKey=None):
        """
        connection: klientens socket
        publicKey: klientens publika nyckel

        Detta än simpel set funktion som lägger till en key _connection_ i dictionary
        och dess _publicKey_ som value.
        """
        self.connections[_connection] = _publicKey

    def removeConnection(self, _connection):
        """
        connection: klientens socket

        Tar bort connection från rummet.
        """
        if _connection in self.connections:
            self.connections.pop(_connection)

    def logMessage(self, alias: str, message: str):
        """
        message: inkommande meddelandet

        Denna funktionen sparar alla meddelanden skickade till en logfil.
        Filen sparas på datorn med filnamnet "roomname.log". Denna funktion fungerar
        bara på publika rum. Loggar ej privata rum.
        """
        if self.private:
            return

        _filepath = 'chatlogs/'
        if not os.path.exists(_filepath):
            os.mkdir(_filepath)

        with open(_filepath+'chatlog-'+self.name+"-"+str(self.uuid)+'.log', encoding='UTF-8', mode="a") as _log:
            _logTxt = alias + ',' + message + "\n"
            _log.write(_logTxt)

    def getLoggedMessages(self) -> dict:
        """
        Denna funktionen retunerar alla meddelanden som skickats i rummet.
        """
        if self.private:
            return ""

        _file = 'chatlogs/chatlog-'+self.name+"-"+str(self.uuid)+'.log'

        if not os.path.exists(_file):
            return ""

        _fullLog = ""
        with open(_file, encoding='UTF-8', mode='r') as _log:
            _fullLog = _log.readlines()

        return _fullLog


class ChatRooms:
    """
    Denna klassen håller koll på de chattrum som finns.
    """
    def __init__(self):
        """
        Skapar en lista för att hålla koll på alla rum som finns.
        """
        self.chatRooms = []
        self.maxPrivateConnections = 2

    def getRoomNames(self, _includePrivate=False):
        """
        includePrivate: om de private rummen också ska includeras

        Detta är en getter som retunerar alla rum som finns.
        """
        _return = []
        for _chatRoom in self.chatRooms:
            if _chatRoom.private and not _includePrivate:
                continue
            _return.append(_chatRoom.name)

        return _return

    def addRoom(self, _name, _password, _private):
        """
        name: rummets namn
        password: rummets lösenord
        private: om rummet ska vara privat

        Detta skapar ett nytt rum.
        """

        _r = ChatRoom(_name, _password, _private)
        self.chatRooms.append(_r)

        return _r

    def _removeRoom(self, _room):
        """
        room: ett objekt av klassen ChatRoom

        Detta är en funktion som tar bort ett rum.
        """
        if _room in self.chatRooms:
            for _connection in _room.connections:
                _connection.close()
            self.chatRooms.remove(_room)

    def getRoom(self, _name):
        """
        name: rummets namn

        Detta är en getter som retunerar ett rum baserad på rummets namn.
        """
        for _room in self.chatRooms:
            if _name == _room.name:
                return _room

        return None # Nothing found

    def addConnectionToRoom(self, _connection, _name, _password, _publicKey=None):
        """
        connection: klientens socket
        name: rummets namn
        password: rummets lösenord
        publicKey: klientens publika nyckel

        Lägger till en connection till ett rum om lösenordet matchar rummets lösenord.
        """
        _room = self.getRoom(_name)

        if _room is None:
            return None

        if _connection not in _room.connections:
            if _room.password == "" or _room.password == _password:
                if _room.private and len(_room.connections) >= self.maxPrivateConnections:
                    return None
                _room.addConnection(_connection, _publicKey)
                return _room
        else:
            return None

    def removeConnectionFromRoom(self, _connection, _name):
        """
        connection: klientens socket
        name: rummets namn

        Detta tar bort en klient från ett rum.
        """
        _room = self.getRoom(_name)

        if _room is None:
            return None

        if _connection in _room.connections:
            _room.removeConnection(_connection)

            if len(_room.connections) < 1:
                logging.info("Removed room: " + _room.name)
                self.chatRooms.remove(_room)
        else:
            return None
