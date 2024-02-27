import pickle
import socket

from abc import ABC, abstractmethod
from ADS1x15 import ADS1115
# from datetime import datetime
from typing import List
from trpc.utils.logger import get_logger

logger = get_logger(__name__)


class Streamer(ABC):
    """Abstract Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @property
    def socket(self):
        return self._socket
    
    @abstractmethod
    def read_emg(self):
        """Reads EMG data from the device"""
        pass

    @abstractmethod
    def write_to_socket(self, emg: List[float | int]):
        """Writes data to socket. On every sample, we pickle the data and send it to the socket.
        
        Args:
            emg: EMG data to write
            movement: Movement data
        """
        pass

    @abstractmethod
    def close_socket(self):
        """Closes the socket"""
        pass

class TRPCStreamer(Streamer):
    """Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self, port: int = 12345, ip_address: str = ""):
        super().__init__()
        self._port = port
        self._ip_address = ip_address
        self._adc = ADS1115(1)
        self._adc.setDataRate(7)
        self._adc.setGain(1)
        self._adc.setMode(ADS1115.MODE_SINGLE)

    def read_emg(self):
        self._adc.requestADC(0)
        # Uncomment the following commented lines to run the test_i2c.py script
        # data = []
        try:
            while True:
                if self._adc.isReady():
                    # data.append({"voltage": self._adc.toVoltage(self._adc.readADC(0)), "timestamp": datetime.now()})
                    # if len(data) == 500:
                    #     break
                    voltages = []
                    voltages.append(self._adc.toVoltage(self._adc.readADC(0)))
                    voltages.append(self._adc.toVoltage(self._adc.readADC(1)))
                    voltages.append(self._adc.toVoltage(self._adc.readADC(2)))
                    voltages.append(self._adc.toVoltage(self._adc.readADC(3)))

                    self.write_to_socket(pickle.dumps(voltages), (self._ip_address, self._port))
        except KeyboardInterrupt:
            logger.info("Interrupted by user. Closing socket and exiting...")
            self.close_socket()
            exit(0)
        except SystemExit:
            self.close_socket()

        # return data
            

    def write_to_socket(self, emg: List[float | int]):
        self._socket.sendto(pickle.dumps(emg), (self._ip_address, self._port))

    def close_socket(self):
        self._socket.close()
