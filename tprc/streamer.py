import socket
import pickle
import RPi.GPIO as GPIO
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


        for i in range(len(self.num_channels)):
          GPIO.setup(self.pins[i], GPIO.IN)


    def write_to_socket(self, emg, movement: Optional[int] = None):
        """Writes data to socket. On every sample, we pickle the data and send it to the socket.
        
        Args:
            emg: EMG data to write
            movement: Movement data
        """
        adcSamp = 0 #to be edited when found
        running = True #forever while loop for streaming
        wait = 1/adcSamp

        #inputs for reading input[pin]
        emg = {}

        #while running == True:
        #array of dictionary 
        #create json string 
        #read the value of the pin and write to the input array 
        for i in range(len(self.num_channels)):
             emg[i] = GPIO.input[pin[i]]
         


        data_arr = pickle.dumps((emg, movement))
        self.socket.sendto(data_arr, ('127.0.0.1', 12345))

    def close_socket(self):
        """Closes the socket"""
        self.socket.close()
