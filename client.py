import packet

import socket
import select
import sys


class Client:
    """
    klient klassen innehåller funktioner för att ansluta till servern,
    skapa alias, chattrum samt skicka chattmeddelanden.
    """
    def __init__(self):
        """
        Variabler initialiseras.
        """
        # User input in setup
        self.alias = None
        self.ip = None
        self.port = None
        self.hostServer = None

        # Callbacks
        self.onTimeReceived = None
        self.onPlayReceived = None
        self.onPauseReceived = None

        # Other
        self.running = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setup(self, _alias, _ip, _port, _hostServer=None, _onTimeReceived=None, _onPlayReceived=None, _onPauseReceived=None):
        """
        alias: klient namn
        ip: server ip
        port: server port
        onConncted: server connection callback
        onMessageReceived: server messege recieved callback

        Här connectar klient objektet till servern med den angivna
        ipadressen samt port. Alla callback funktioner sparas också.
        """
        # User input
        self.alias = _alias
        self.ip = _ip
        self.port = _port
        self.hostServer = _hostServer
        self.onTimeReceived = _onTimeReceived
        self.onPlayReceived = _onPlayReceived
        self.onPauseReceived = _onPauseReceived

    def start(self):
        """
        Här startas klienten och en tråd skapas som lyssnar för inkommande
        paket från servern.
        """
        try:
            try:
                self.server.connect((self.ip, self.port))
                self.running = True
            except ConnectionRefusedError:
                print("Can not connect to host!")
                return

            print("Connected!")
            while self.running:

                # maintains a list of possible input streams
                sockets_list = [self.server]

                read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

                for socks in read_sockets:
                    if socks == self.server:
                        packet = socks.recv(2048)
                        if (packet is None):
                            continue

                        self.receivedPacket(packet.decode())
        except ConnectionResetError:
            print("Connection lost to server!")
            self.stop()

    def stop(self):
        """
        Här stängs klienten av.
        """
        self.running = False
        self.server.close()

    def receivedTime(self, _jsonMsg):
        """
        jsonMsg: JSON representation av historiken

        Läser av chat historiken från rummet.
        """
        _time = _jsonMsg["time"]
        self.onTimeReceived(_time)

    def sendPlay(self):
        """
        Skickar en förfrågan om listan på rum som finns
        """
        _packet = packet.serializePlay()
        self.sendPacket(_packet)

    def receivedPlay(self):
        """
        jsonMsg: JSON representation av historiken

        Läser av chat historiken från rummet.
        """
        self.onPlayReceived()

    def sendPause(self):
        """
        Skickar en förfrågan om listan på rum som finns
        """
        _packet = packet.serializePause()
        self.sendPacket(_packet)

    def receivedPause(self):
        """
        jsonMsg: JSON representation av historiken

        Läser av chat historiken från rummet.
        """
        self.onPauseReceived()

    def sendPacket(self, _packet):
        """
        packet: Paketet som ska skickas

        Skickar paketet till servern.
        """
        try:
            #if self.hostServer is not None:
            #    self.hostServer.broadcastToRoom(self.ip, _packet)
            #else:
            print("Sent packet: ", _packet)
            self.server.send(_packet)
        except:
            self.stop()

    def receivedPacket(self, _packet):
        """
        Läser paketet.
        """
        _jsonMsg = packet.parsePacket(_packet)
        print("Received: ", _jsonMsg)
        # try:
        if _jsonMsg["type"] is packet.Types.time.value:
            self.receivedTime(_jsonMsg)
        elif _jsonMsg["type"] is packet.Types.play.value:
            self.receivedPlay()
        elif _jsonMsg["type"] is packet.Types.pause.value:
            self.receivedPause()
        else:
            print("Packet was not recognized! " + _packet)
        # except TypeError:
        #    if _jsonMsg is None:
        #        self.stop()
        #    else:
        #        print("Error reading json: ", _jsonMsg)
