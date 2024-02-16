import socket
import pigpio

from typing import Dict
from trpc.utils.logger import get_logger
from trpc import Streamer, TRPCProcessor

logger = get_logger(__name__)


class Controller:
    """This class represents the controller for the robot arm assembly. It can read the classification from the
    processor and send the appropriate commands to the robot arm. It takes in the port and ip address of the
    processor output stream as parameters.

        Args:
            port: The port of the processor output stream
            ip_address: The ip address of the processor output stream
            gestures: Dictionary of gesture number and corresponding command
            pins: Dictionary of servo number and corresponding pins
    """

    def __init__(self, streamer, classifier, port: int = 12346, ip_address: str = "127.0.0.1", 
                 gestures: Dict[int, Dict[str, int | str]] = {}, pins: Dict[str, int] = {}):
        from trpc import Driver
        if not gestures:
            gestures = {
                0: {
                    "gesture": "Hand Open",
                    "servo": "Servo 1",
                    "value": 1
                },
                1: {
                    "gesture": "Hand Close",
                    "servo": "Servo 1",
                    "value": -1
                },
                2: {
                    "gesture": "No Movement",
                    "servo": "Servo 1",
                    "value": 0
                }
            }

        if not pins:
            # These are arbitrary pin values. They should be replaced with the actual pin values
            pins = { "Servo 1": 17 }

        pigpio.pi()
        self._port = port
        self._ip_address = ip_address
        self._classifier_output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._classifier_output_socket.bind((self._ip_address, self._port))
        self._gestures = gestures
        self._streamer = streamer
        self._classifier = classifier
        self._driver = Driver(servo_pins=pins, gestures=self._gestures)

    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self, value):
        if not isinstance(value, int):
            raise ValueError("Port must be an integer")
        self._port = value

    @property
    def ip_address(self):
        return self._ip_address
    
    @ip_address.setter
    def ip_address(self, value):
        if not isinstance(value, str):
            raise ValueError("IP address must be a string")
        self._ip_address = value

    @property
    def gestures(self):
        return self._gestures
    
    @gestures.setter
    def gestures(self, value):
        if not isinstance(value, dict):
            raise ValueError("Gestures must be a dictionary")
        self._gestures = value

    @property
    def streamer(self):
        return self._streamer
    
    @streamer.setter
    def streamer(self, value):
        if not isinstance(value, Streamer):
            raise ValueError("Streamer must be a Streamer object")
        self._streamer = value

    @property
    def classifier(self):
        return self._classifier
    
    @classifier.setter
    def classifier(self, value):
        if not isinstance(value, TRPCProcessor):
            raise ValueError("Classifier must be a TRPCProcessor object")
        self._classifier = value

    @property
    def driver(self):
        return self._driver
    
    @driver.setter
    def driver(self, value):
        from trpc import Driver
        if not isinstance(value, Driver):
            raise ValueError("Driver must be a Driver object")
        self._driver = value

    def start(self):
        """Runs the startup process for the controller. This includes starting the streamer and the classifier."""
        # TODO: Have streamer run in a separate process
        # self._streamer.run()
        self._classifier.run()
        logger.info("Controller started")

    def listen(self):
        """Runs the controller and sends the appropriate commands to the robot arm based on the classification."""
        logger.info("Running controller")
        while True:
            try:
                data, addr = self._classifier_output_socket.recvfrom(1024)  # Receive up to 1024 bytes
                gesture_class, prob, timestamp = data.decode().split()  # Decode the received bytes
                if int(gesture_class) in self._gestures.keys():
                    self._driver.execute_command(self._gestures[int(gesture_class)])
            except KeyboardInterrupt:
                self._stop()
                logger.info("Detected keyboard interrupt. Stopping controller and subordinates...")
                break

    def stop(self):
        self._streamer.close_socket()
        self._classifier.close()
        self._streamer.close_socket()
