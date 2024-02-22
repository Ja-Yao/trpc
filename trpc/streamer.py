import pickle
import socket

from abc import ABC, abstractmethod
from ADS1x15 import ADS1115
from time import sleep
from typing import Optional
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
    def write_to_socket(self, emg, movement: Optional[int] = None):
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
        self._adc.setMode(ADS1115.MODE_CONTINUOUS)

    def read_emg(self):
        self._adc.readADC(0)
    
        while True:
            raw = self._adc.getValue()
            logger.info("{0:.3f} V".format(self._adc.toVoltage(raw)))
            sleep(1)
            

    def write_to_socket(self, emg, movement: Optional[int] = None):
        data = {"emg": emg, "movement": movement}
        self._socket.sendto(pickle.dumps(data), (self._ip_address, self._port))

    def close_socket(self):
        self._socket.close()
