import socket

class Controller:
    """This class represents the controller for the robot arm assembly. It can read the classification from the
        processor and send the appropriate commands to the robot arm. It takes in the port and ip address of the
        processor output stream as parameters.
    """
    def __init__(self, port: str = '12346', ip_address: str = '127.0.0.1'):
        self.port = port
        self.ip_address = ip_address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip_address, self.port))

    def run(self):
        """Runs the controller"""
        pass