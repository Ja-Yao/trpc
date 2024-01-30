import socket
import pickle
from gpiozero import DigitalInputDevice as GPIO
import time
from typing import Optional


class Streamer:
    """Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self, num_channels: int = 2) -> None:
        """initializes streamer class
        
        Args:
            num_channels: number of electrodes to read
        
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.num_channels = num_channels
        self.pins = [num_channels]

    def setup_board(self):
        """initialize board from self and sets fixed pins from self as inputs"""
        GPIO.setmode(GPIO.BCM) #number closen for pins correlates directly w GPIO number on board

        pinNum_long = int(input("Select desired pin numbers (seperate w spaces):"))
        self.pins = [int(pin) for pin in pinNum_long.split()]


        for i in range(self.num_channels)
          GPIO.setup(self.pins[i], GPIO.IN)

    def read_GPIO(self):
        #list for read signals
        emg = [[0]*self.num_channels]

        #for reading inputs and set into emg list 
        for i in range(self.num_channels):
            emg[i] = GPIO.input(self.pins[i])
                
        return emg

    def write_to_socket(self, emg, movement: Optional[int] = None):
        """Writes data to socket. On every sample, we pickle the data and send it to the socket.
        
        Args:
            emg: EMG data to write
            movement: Movement data
        """
        

        data_arr = pickle.dumps((emg))
        self.socket.sendto(data_arr, ('127.0.0.1', 12345))

    def close_socket(self):
        """Closes the socket"""
        self.socket.close()
