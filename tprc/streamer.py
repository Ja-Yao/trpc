import socket
import pickle


class Streamer:
    """Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write_to_socket(self, emg, movement):
        """
        Writes data to socket
        
        :param emg: EMG data
        :param movement: Movement data
        """
        data_arr = pickle.dumps((emg, movement))
        self.socket.send(data_arr, ())

    def close_socket(self):
        """Closes socket"""
        self.socket.close()
