import packet
import time
import socket
import threading as thread
import json


class Server:
    """
    server klassen innehåller funktioner för att öppna och avsluta en server
    """
    def __init__(self, ip, port):
        """
        ip: server ip
        port: server port

        Öppnar en socket som binds till den angivna ip samt port.
        Skapar även en lista för anslutna klienter
        """
        self.ip = ip
        self.port = port

        # Setup
        self.running = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        self.server.listen(100)  # 100 active clients at once, can be change if needed
        self.connectedClients = {} # Connection object : room

    def addUser(self, _connection, _ip):
        """
        connection: klient socket
        ip: klient ip

        Öppnar en ny tråd så att servern kan ta emot paket från klienten.
        conn är connection objektet som fås ur socket biblioteket och ip
        är klientens ip adress.
        """
        # sends a message to the client whose user object is connection
        print("User ip: " + str(_ip[0]))

        while True:
            try:
                _packet = _connection.recv(2048)
                if _packet:
                    self.receivedPacket(_packet.decode(), _connection)
                else:
                    """message may have no content if the connection 
                    is broken, in this case we remove the connection"""
                    self.removeUser(_connection)
                    return
            except Exception as e:
                #logging.debug("User exception?", e)
                continue

    def broadcastToRoom(self, _connection, _packet):
        """
        connection: klient socket som skickade meddelandet
        packet: paketet som klienten skickade, innehåler meddelandet
        room: vilket rum klienten är i

        Skickar vidare meddelandet till de andra klienterna som är
        anslutna till chattrummet. Den ser också till så att meddelandet
        inte skickas till klienten som skickade den. Connection är
        klienten som skickade paketet och packet innehåller paketet.
        """
        # _room = self.rooms.getRoom(_jsonPacket["roomName"])
        # Check so the user doesnt try to send a message to a room that doesnt exist
        # or the user isn't connected to.
        # if _room is not None and self.connectedClients[_connection].name == _jsonPacket["roomName"]:
        # _room.logMessage(_jsonPacket["alias"], _jsonPacket["message"])

        if len(self.connectedClients) > 0:
            print("Broadcasted: ", _packet)

        for _client in self.connectedClients.copy():
            if _client != _connection:
                self.sendPacket(_packet, _client)

    def sendRooms(self, _connection):
        """
        connection: klient socketen som frågade om rumslistan

        Skickar en lista på alla rum som finns och är publika
        """
        _packet = packet.serializeSendRoomsList(self.rooms.getRoomNames())
        self.sendPacket(_packet, _connection)

    def removeUser(self, _connection):
        """
        connection: klient socketen som ska stängas

        Tar bort klienten från servern
        """
        if _connection in self.connectedClients:
            print("Removed: " + str(_connection))
            #self.disconnectFromRoom(_connection)
            self.connectedClients.pop(_connection)
            _connection.close()

    def createRoom(self, _connection, _jsonPacket):
        """
        connection: klient socketen som vill skapa rummet
        packet: paketet som innehåller namn och password

        Skapar ett rum med det angivna namnet och lösenordet
        från paketet.
        """
        _rName = _jsonPacket["roomName"]
        _rPassword = _jsonPacket["password"]
        _rPrivate = _jsonPacket["private"]

        _room = self.rooms.addRoom(_rName, _rPassword, _rPrivate)
        self.connectToRoom(_connection, _jsonPacket)
        print("Created room: " + _room.name + " Password: " + _room.password + " Private: " + str(_rPrivate))

    def sendConnectedRoom(self, _connection, _room, _publicKey=None):
        """
        connection: klientens socket som anslöt till rummet
        room: rummets ChatRoom objekt
        publicKey: klientens publika nyckel

        Skickar ett paket till klienten som godkänner att anslutningen till rummet
        lyckades.
        """
        _packet = packet.serializeConnectedRoom(_room.name, _room.private)
        self.sendPacket(_packet, _connection)

        # Skicka chathistoriken
        if not _room.private:
            _cHistory = _room.getLoggedMessages()
            _cHistoryPacket = packet.serializeChatHistory(_cHistory)
            print("Sent log: " + str(_cHistoryPacket))
            self.sendPacket(_cHistoryPacket, _connection)

        # Dela bådas public key
        if _room.private:
            for _otherConn in _room.connections:
                if _otherConn is not _connection:
                    _publicKeyPacket = packet.serializePublickey(_publicKey)
                    self.sendPacket(_publicKeyPacket, _otherConn)
                    _otherPublicKeyPacket = packet.serializePublickey(_room.connections[_otherConn])
                    self.sendPacket(_otherPublicKeyPacket, _connection)
                    return


    def connectToRoom(self, _connection, _jsonPacket):
        """
        connection: klient socket som vill ansluta till rummet
        packet: klientens paket som innehåller rumsnamn och lösenord

        Lägger till klienten i ett rum om lösenordet matchar det
        som angavs när rummet skapades. Namn och lösenordet läses
        ur packetet.
        """
        _room = self.rooms.addConnectionToRoom(_connection, _jsonPacket["roomName"], _jsonPacket["password"], _jsonPacket["publicKey"])

        if _room is not None:
            self.connectedClients[_connection] = _room
            print(str(_connection) + " connected to room: " + self.connectedClients[_connection].name)
            self.sendConnectedRoom(_connection, _room, _jsonPacket["publicKey"])

    def disconnectFromRoom(self, _connection):
        """
        Tar bort klienten från det rummet klienten är ansluten till.
        """
        if (self.connectedClients[_connection] is not None):
            self.rooms.removeConnectionFromRoom(_connection, self.connectedClients[_connection].name)
            print("Removed {0} from room".format(_connection))

    def sendPacket(self, _packet, _connection):
        """
        packet: paketet som ska skickas
        connection: mottagerns socketobjekt

        Skickar paketet till den angivna klienten.
        """
        print("Sent packet: " + str(_packet))
        try:
            _connection.send(_packet)
        except:
            # if the link is broken, we remove the client
            self.removeUser(_connection)

    def receivedPacket(self, _packet, _connection):
        """
        packet: inkommande paketet

        Läser paketet och om det innehåller en typ som servern kan hanter
        så läses innehållet och skickas vidare till motsvarande funktion,
        annars ignoreras paketet.
        """
        print("Received packet: " + str(_packet))
        _jsonMsg = packet.parsePacket(_packet)
        try:
            if _jsonMsg["type"] is packet.Types.play.value:
                _packet = packet.serializePlay()
                self.broadcastToRoom(_connection, _packet)
            elif _jsonMsg["type"] is packet.Types.pause.value:
                _packet = packet.serializePause()
                self.broadcastToRoom(_connection, _packet)
            else:
                print("Packet was not recognized! " + _packet)
        except AttributeError:
            print("Attribute error when comparing packet type! " + str(_packet))
        except KeyError:
            print("Key: Type not found in packet! " + str(_packet))
        except NameError:
            print("Some function naming error!")

    def start(self):
        """
        Här finns en loop som lyssnar efter nya inkommande
        connections, nya klienter. De läggs till i listan
        av klienter och en ny tråd skapas åt klienten med
        adduser funktionen.
        """
        print("Started server!")
        self.running = True
        while self.running:
            _connection, _ip = self.server.accept()

            # Stores connected clients and the room they're connected to.
            self.connectedClients[_connection] = None

            # creates an individual thread for every user that connects
            t = thread.Thread(target=self.addUser, args=(_connection, _ip), name="Client" + str(_ip[1]), daemon=True)
            t.start()
            time.sleep(2)

        self.server.close()

    def stop(self):
        """
        Stannar servern.
        """
        print("Stopping server!")
        self.running = False
