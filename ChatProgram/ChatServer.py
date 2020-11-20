import Server

"""
Hanterar server objektet
"""

if __name__ == '__main__':
    """
    Tar in ip och port som argument. Gör sedan ett server objekt
    och startar servern.
    """
    ip = 'localhost'
    port = 1337
    server = Server.Server(ip, port)
    try:
        print("Trying to start server...")
        server.start()
    except KeyboardInterrupt:
        server.stop()
        exit()
