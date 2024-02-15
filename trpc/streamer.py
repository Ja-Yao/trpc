import socket
import pickle
import gpiozero
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

    def setup_i2c(i2c_addr, i2c_bus):
        """Setups i2c communications with ADC
        
        Args:
            i2c_addr: address of ADC
            i2c_bus: i2c bus number? (on pi?)
        
        """
        i2c_flags = 0 # no flags defined currently
        
        #pin registers
        GND = 0b1001000
        VDD = 0b1001001
        SDA = 0b1001010
        SCL = 0b1001011
        
        #0 = recieve / 1 = transmit 
        rw = 1
        
        #register location for pointer registers
        conversion = 0x00
        config = 0x01
        lowthresh = 0x02
        highthresh = 0x03
    
        
        handle = i2c_open(i2c_bus, i2c_addr, i2c_flags)
        
        #writes the desired pin register to the i2c
        i2c_write_byte_data(handle, (SCL << 1) | rw)
        #writes to address pointer register to choose future byte writing
        i2c_write_byte(handle, config)
        
        return handle
        
    def threaded_mux_selector(handle):
        """flips through mux inputs
        
        Args:
            handle: device #
        
        """
        
        #pg 28 of ADS111x datasheet 
        
        #14:12 = MUX configuration
        #8 = conversion mode 
        #7:5 = Data rate = 128sps default     
        
        # starts in state A0   
       
        A1 = 0x5080     #0101 0000 1000 0000
        A2 = 0x6080     #0110 0000 1000 0000
        A3 = 0x7080     #0111 0000 1000 0000
        A0 = 0x4080     #0100 0000 1000 0000 #default state
    
        states = [A1, A2, A3, A0]
        
        #looping variable
        i = 0
        
        for i in range(4):
            i2c_write_word_data(handle, reg, states[i])
            i += 1
            
     
        
        
        
        

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
