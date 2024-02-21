import socket
import pickle
import pigpio
import time
from typing import Optional

#pointer register within ADC
CONVERSION = 0x00
CONFIG = 0x01
LOWTHRESH = 0x02
HIGHTHRESH = 0x03

#i2c pin registers
GND = 0b1001000
VDD = 0b1001001
SDA = 0b1001010
SCL = 0b1001011


class Streamer:
    """Streamer class for sending data from device to LibEMG pipeline"""

    def __init__(self, i2c_addr: int = 0x48, i2c_bus: int = 1, num_channels: int = 4) -> None:
        """initializes streamer class

        Args:
            num_channels: number of electrodes to read
            i2c_addr: address of the i2c device
            i2c_bus: bus number of the i2c device


        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pi = pigpio.pi()

        # for setting up i2c device
        self.i2c_addr = i2c_addr  # found using i2c detect tool on rasp pi (connects to i2C 1)
        self.i2c_bus = i2c_bus  # found on the pi documentation
        self.handle = 0

        self.pins = [None for i in range(num_channels)]

    def setup_i2c(self):
        """Setups i2c communications with ADC

        Args:
            self

        """
        i2c_flags = 0  # no flags defined currently        

        # create
        handle = self.pi.i2c_open(self.i2c_bus, self.i2c_addr, i2c_flags)

        if handle < 0:
            print("i2c_open failed")
            return -1

        self.handle = handle

    def analog_input_selector(self):
        """flips through mux inputs

        Args:
            handle: device # as setup in i2c_setup

        """

        # pg 28 of ADS111x datasheet

        # 14:12 = MUX CONFIGuration
        # 8 = CONVERSION mode
        # 7:5 = Data rate = 128sps default

        # starts in state A0

        A1 = 0b0101_0000_0110_0000
        A2 = 0b0110_0000_0110_0000
        A3 = 0b0111_0000_0110_0000
        A0 = 0b0100_0000_0110_0000  # default state

        states = [A1, A2, A3, A0]

        # register of data stream
        SDA = 0b1001010

        for i in range(3):
            self.pi.i2c_write_byte(self.handle, CONVERSION)  # changes ptr to conversion register

            read_word = self.pi.i2c_read_word_data(self.handle, CONVERSION)  # reads lsb then msb
            flipped_word = ((read_word & 0x0F) << 4) | ((read_word & 0xF0) >> 4)  # flips the word ex 0x18 to 0x81

            self.pins[i] = flipped_word  # adds to output list

            self.pi.i2c_write_byte(self.handle, CONFIG)  # changes addr pointer reg to CONFIG

            flipped_state = ((states[i] & 0x0F) << 4) | ((states[i] & 0xF0) >> 4)  # flips the word ex 0x18 to 0x81
            self.pi.i2c_write_word_data(self.handle, CONFIG, flipped_state)  # changes A# for next iteration


    def write_to_socket(self, emg, movement: Optional[int] = None):
        """Writes data to socket. On every sample, we pickle the data and send it to the socket.

        Args:
            emg: EMG data to write
            movement: Movement data
        """

        data_arr = pickle.dumps((emg))
        self.socket.sendto(data_arr, ("127.0.0.1", 12345))

    def close_socket(self):
        """Closes the socket"""
        self.socket.close()
