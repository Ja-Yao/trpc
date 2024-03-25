import pickle
import socket
from abc import ABC, abstractmethod
from multiprocessing.synchronize import Lock as LockType
from typing import List

from ADS1x15 import ADS1115

from trpc.utils.logger import get_logger

logger = get_logger(__name__)


class Streamer(ABC):
    """Abstract Streamer class for sending data from device to LibEMG pipeline"""

    def __init__(self, port: int = 12345, ip_address: str = "127.0.0.1") -> None:
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
    """Streamer class for sending data from device to LibEMG pipeline.

        Args:
            lock: Lock object to synchronize access to the i2c device
            port: Port number for the socket
            ip_address: IP address for the socket
    """

    def __init__(self, lock, port: int = 12345, ip_address: str = "127.0.0.1"):
        super().__init__(port, ip_address)

        self._adc = None
        if not isinstance(lock, LockType):
            raise ValueError(f"Invalid lock: {lock}")
        self._lock = lock

    def read_emg(self):
        self._adc = ADS1115(1)

        # set the gain and data rate (samples/second)
        self._adc.setDataRate(ADS1115.DR_ADS111X_860)
        self._adc.setGain(ADS1115.PGA_4_096V)

        # set the mode to single shot
        self._adc.setMode(ADS1115.MODE_SINGLE)

        self._adc.requestADC(0)
        try:
            while True:
                if self._adc.isReady():
                    # get list of voltages from each channel in mV
                    with self._lock:
                        voltages = [self._adc.toVoltage(self._adc.readADC(i)) for i in range(4)]
                        self.write_to_socket(voltages)
        except KeyboardInterrupt:
            logger.info("Interrupted by user. Closing socket and exiting...")
            self.close_socket()
            exit(0)
        except SystemExit:
            self.close_socket()
