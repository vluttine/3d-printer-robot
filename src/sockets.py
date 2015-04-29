'''
Software Project course
Routeplanner
Roope Kallio, Ville Luttinen, Heikki Korhonen & Joni Saunavaara
14.6.2014

Simple TCP socket interface for sending and receving messages.
'''

import socket

class TCPsocket:
    """Simple TCP socket interface for sending and receving messages."""
    _socket = ""
    conn = ""
    addr = ""

    def __init__(self, type, host, port):
        """Set up server or client socket."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if type == "server":
            self._socket.bind((host, port))
            self._socket.listen(1)
            self._socket.setblocking(0)

    def close(self):
        """Close socket."""
        self._socket.close()

    def getMessage(self):
        """Get message from socket. Send ACK to tell that data was received.
        Return list of data."""
        try:
            self.conn, self.addr = self._socket.accept()
            data = self.conn.recv(128000000)
            self.conn.send("ACK")
        except socket.error:
            data = "no data"
        return data.split(';')

    def sendMessage(self, message, host, port):
        """Send message to socket. Check if data was received by checking the socket for ACK.
        Return 1 if everythin went fine. 0 otherwise."""
        try:
            self._socket.settimeout(5)
            self._socket.connect((host, port))
            self._socket.send(message)
            data = self._socket.recv(16)
            if data == "ACK":
                return 1
            else:
                return 0
        except socket.error:
            return 0


