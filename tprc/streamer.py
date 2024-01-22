import socket
import pickle
import RPi.GPIO as GPIO
import time
from typing import Optional


class Streamer:
    """Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.channelNum = None
        self.pins = []

    def setup_board(self):
        GPIO.setmode(GPIO.BOARD)
        self.channelNum = input("Select number of desired channels:")

        pinNum_long = int(input("Select desired pin numbers (seperate w spaces):"))
        self.pins = [int(pin) for pin in pinNum_long.split()]


        for i in range(len(self.channelNum)):
          GPIO.setup(self.pins[i], GPIO.IN)

    def write_to_socket(self, emg, movement: Optional[int] = None):
        """Writes data to socket. On every sample, we pickle the data and send it to the socket.
        
        Args:
            emg: EMG data to write
            movement: Movement data
        """
        data_arr = pickle.dumps((emg, movement))
        self.socket.sendto(data_arr, ('127.0.0.1', 12345))

    def close_socket(self):
        """Closes the socket"""
        self.socket.close()
