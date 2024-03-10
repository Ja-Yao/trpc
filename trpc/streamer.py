import pickle
import socket

from abc import ABC, abstractmethod
from ADS1x15 import ADS1115
from typing import List
from trpc.utils.logger import get_logger

logger = get_logger(__name__)


class Streamer(ABC):
    """Abstract Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self, port: int = 12345, ip_address: str = "") -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._port = port
        self._ip_address = ip_address

    @property
    def socket(self):
        return self._socket
    
    @abstractmethod
    def read_emg(self):
        """Reads EMG data from the device"""
        pass

    def write_to_socket(self, emg: List[float | int]):
        """Writes data to socket. On every sample, we pickle the data and send it to the socket.
        
        Args:
            emg: EMG data to write. This should be a list of voltage values read from each channel
        """
        self._socket.sendto(pickle.dumps(emg), (self._ip_address, self._port))

    def close_socket(self):
        """Closes the socket"""
        self._socket.close()


class TRPCStreamer(Streamer):
    """Streamer class for sending data from device to LibEMG pipeline"""
    def __init__(self, port: int = 12345, ip_address: str = ""):
        super().__init__(port, ip_address)
        self._adc = ADS1115(1)
        self._adc.setDataRate(7)
        self._adc.setGain(1)
        self._adc.setMode(ADS1115.MODE_SINGLE)

    def read_emg(self):
        self._adc.requestADC(0)
        try:
            while True:
                if self._adc.isReady():
                    # get list of voltages from each channel in mV
                    voltages = [int(self._adc.toVoltage(self._adc.readADC(i)) * 1000) for i in range(4)]

                    self.write_to_socket(voltages)
        except KeyboardInterrupt:
            logger.info("Interrupted by user. Closing socket and exiting...")
            self.close_socket()
            exit(0)
        except SystemExit:
            self.close_socket()
