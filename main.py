# importing time and vlc
import threading
import time, vlc
import mediaplayer
import server
import client

# https://www.olivieraubert.net/vlc/python-ctypes/doc/
# https://gits-15.sys.kth.se/gruprog19/simgra-p-uppgift

def UpdateVideoTime(_time):
    player.SetTime(_time)

def PauseVideo():
    player.OnPause()


def ResumeVideo():
    player.OnPlay()


"""
# method to play video
def StartVideo(source):
    # creating a vlc instance
    vlc_instance = vlc.Instance()

    # creating a media player
    player = vlc_instance.media_player_new()

    # creating a media
    media = vlc_instance.media_new(source)

    # setting media to the player
    player.set_media(media)

    # play the video
    player.play()

    return player
"""

myServer = None
myClient = client.Client()
port = 1337

player = None

if __name__ == "__main__":
    isHost = input("Are you the host? ").lower()
    ip = input("Enter host ip: ")
    if isHost == "true" or isHost == "yes":
        myServer = server.Server(ip, port)
        isHost = True
        try:
            print("Trying to start server...")
            serverThread = threading.Thread(target=myServer.start, name="serverThread", daemon=True)
            serverThread.start()
        except KeyboardInterrupt:
            exit()
    else:
        isHost = False

    myClient.setup("", ip, port, myServer, UpdateVideoTime, ResumeVideo, PauseVideo)
    #if not isHost:
    myClientThread = threading.Thread(target=myClient.start, name="clientThread", daemon=True)
    myClientThread.start()

    # Create a Tk.App(), which handles the windowing system event loop
    root = mediaplayer.Tk_get_root()
    root.protocol("WM_DELETE_WINDOW", mediaplayer._quit)

    player = mediaplayer.Player(root, title="tkinter vlc", hostServer=myServer, client=myClient)
    # show the player window centred and run the application
    root.mainloop()
    if isHost:
        myServer.stop()
    quit()


# call the video method
#video_source = input("Video location: ")
#player = StartVideo(video_source)

#input("Press enter to exit")
# C:\Users\Simon\Desktop\Iron Man 2.mp4