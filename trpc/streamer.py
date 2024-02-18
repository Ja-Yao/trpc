from abc import ABC, abstractmethod
import socket
import pickle
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
        self._socket.bind((self._ip_address, self._port))

    def write_to_socket(self, emg, movement: Optional[int] = None):
        data = {"emg": emg, "movement": movement}
        self._socket.sendto(pickle.dumps(data), (self._ip_address, self._port))

    def close_socket(self):
        self._socket.close()
