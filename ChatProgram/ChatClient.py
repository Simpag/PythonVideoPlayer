#!bin/usr/python
"""This controls the ui"""
import Client

import threading
from functools import partial
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup


# Windows
class WindowManager(ScreenManager):
    """
    Hanterar byten mellan olika menyer.
    """
    pass


class StartWindow(Screen):
    """
    Hanterar alla element i start menyn, bl.a inmatning av alias, ip samt port.
    """
    #ip = ObjectProperty(None)
    #port = ObjectProperty(None)
    alias = ObjectProperty(None)

    def connect(self):
        """
        Ansluter till den angivna servern.
        """
        masterApp.startClient("localhost", 1337, self.alias.text)


class MainMenuWindow(Screen):
    """
    Hanterar alla element i main menyn, skapande av rum sammt anslutande till rum.
    """
    roomsContainer = ObjectProperty(None)
    createRoomName = ObjectProperty(None)
    createRoomPassword = ObjectProperty(None)
    roomsContainer = ObjectProperty(None)
    aliasLabel = ObjectProperty(None)
    private = ObjectProperty(None)

    def createRoom(self):
        """
        Skickar en request till att skapa ett rum.
        """
        if self.createRoomName.text is "":
            return

        masterApp.client.createRoom(self.createRoomName.text, self.createRoomPassword.text, self.private.active)

    def refreshRoomList(self):
        """
        Uppdaterar rumslistan.
        """
        masterApp.refreshRoomsList()

    def joinPrivateRoom(self):
        """
        Visar en popup för att ansluta till privata rum
        """
        showPopup(ConnectPrivateRoomPopup(), "Private Room")


class ChatRoomWindow(Screen):
    """
    Hanterar alla element i chat rummet samt inmatning av chattmeddelande.
    """
    chatContainer = ObjectProperty(None)
    message = ObjectProperty(None)

    def sendMessage(self):
        """
        Skickar det inmatade meddelandet
        """
        if self.message.text is "":
            return

        masterApp.client.sendMessage(self.message.text)
        masterApp.printChatMessage("You", self.message.text)
        self.message.text = ""

    def disconnect(self):
        """
        Lämnar chattrummet.
        """
        masterApp.client.disconnectFromRoom()


# Popups
def showPopup(_popupClassObject, _popupTitle):
    """
    popupClassObject: Vilken popup som ska visas
    popupTitle: Rubriken på popup menyn

    Öppnar popups till skärmen.
    """
    if (_popupClassObject.parent is not None):
        _popupClassObject.parent.remove_widget(_popupClassObject)
    _popup = Popup(title="", content=_popupClassObject, size_hint=(1 / 2, 1 / 2))
    _popupClassObject.popupManager = _popup
    _popup.open()


class FailedToConnectToServerPopup(FloatLayout):
    """
    Visas när fel ipadress inamtades.
    """
    pass


class ConnectRoomPopup(FloatLayout):
    """
    Frågar användaren om lösenord till chattrummet.
    """
    password = ObjectProperty(None)
    popupManager = None

    def __init__(self, _roomName, **kwargs):
        super().__init__(**kwargs)
        self.roomName = _roomName

    def connectToRoom(self):
        masterApp.client.connectToRoom(self.roomName, self.password.text)
        self.popupManager.dismiss()


class ConnectPrivateRoomPopup(FloatLayout):
    """
    Frågar användaren om det privata rummets namn och lösenord.
    """
    password = ObjectProperty(None)
    roomName = ObjectProperty(None)
    popupManager = None

    def connectToRoom(self):
        masterApp.client.connectToRoom(self.roomName.text, self.password.text)
        self.popupManager.dismiss()


# Main class
class ChatApp(App):
    """
    Huvudappen för klienten, hanterar GUI.
    """

    def __init__(self, **kwargs):
        """
        Förbereder för start av klienten.
        """
        super().__init__(**kwargs)
        self.client = Client.Client()
        self.clientThread = threading.Thread(target=self.client.start, name="clientThread", daemon=True)

        self.alias = ""
        self.kv = Builder.load_file("KivyLayout/chat.kv")
        self.windowManager = WindowManager()
        self.screens = [StartWindow(name="StartWindow"), MainMenuWindow(name="MainMenu"),
                        ChatRoomWindow(name="ChatRoom")]
        for screen in self.screens:
            self.windowManager.add_widget(screen)
        self.windowManager.current = "StartWindow"
        # self.screens[1].add_widget(Label(text="Test"))

    def build(self):
        """
        Kivy.
        """
        return self.windowManager

    def startClient(self, _ip: str, _port: int, _alias: str):
        """
        Användaren anger sitt alias, ip samt port och ett client objekt skapas.
        """
        self.alias = _alias
        self.screens[1].aliasLabel.text = _alias
        self.client.setup(_alias, _ip, _port, self.onConnection, self.printChatMessage, self.recievedRoomsList,
                          self.connectedToRoom)
        self.clientThread.start()

    def refreshRoomsList(self):
        """
        Skickar en request till server för att få rumslistan.
        """
        self.screens[1].roomsContainer.clear_widgets()
        self.client.requestRoomsList()

    # Callbacks
    def onConnection(self, _connected: bool):
        """
        connected: Om anslutnigen lyckades

        En callback funktion.
        Kallas när anslutningen till servern har skapats. Visar nästa meny för klienten.
        """
        if _connected:
            self.refreshRoomsList()
        else:
            showPopup(FailedToConnectToServerPopup, "Failed to connect to supplied ip")

    def recievedRoomsList(self, _json):
        """
        json: JSON representation av paketet som inkom från servern, innehåler alla rumsnamn

        En callback funktion.
        Listar alla rum som finns.
        """
        _roomsContainer = self.screens[1].roomsContainer
        for _room in _json["rooms"]:
            _roomsContainer.add_widget(Label(text=_room, color=(0.070, 0.070, 0.070, 1)))
            _btnCB = partial(showPopup, ConnectRoomPopup(_room))
            _btn = Button(text="Join", on_release=_btnCB, )
            _roomsContainer.add_widget(_btn)
        # showPopup(ConnectRoomPopup("test"), "Connect to ")

    def printChatMessage(self, _alias, _message):
        """
        alias: Sändarens alias
        message: Sändarens meddelande

        En callback funktion.
        Formaterar meddelanden från andra klienter.
        """
        if _alias == self.alias:
            _alias = "You"

        _msg = "<{0}> {1}".format(_alias, _message.strip())
        _chatContainer = self.screens[2].chatContainer
        _l = Label(text=_msg, size_hint=(1.0, 1.0), halign="left", valign="middle")
        _l.bind(size=_l.setter('text_size'))
        _l.color = [0.070, 0.070, 0.070, 1]
        _chatContainer.add_widget(_l)

    def connectedToRoom(self, _json):
        """
        json: JSON representation av rummet

        En callback funktion.
        Byter till chatrummets meny när en anslutning till ett rum skapats.
        """
        self.screens[2].chatContainer.clear_widgets()
        self.screens[2].message.text = ""
        self.windowManager.current = "ChatRoom"
        self.windowManager.transition.direction = "left"


# Starts the app
masterApp = ChatApp()
masterApp.run()
