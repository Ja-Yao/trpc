import socket

from typing import Dict
from trpc.utils.logger import get_logger
from trpc import Driver, Streamer, TRPCProcessor

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
                    "value": 1
                },
                1: {
                    "gesture": "Hand Close",
                    "value": -1
                },
                2: {
                    "gesture": "No Movement",
                    "value": 0
                }
            }

        if not pins:
            # These are arbitrary pin values. They should be replaced with the actual pin values
            pins = {"Servo 1": 17, "Servo 2": 18, "Servo 3": 19, "Servo 4": 20, "Servo 5": 21, "Servo 6": 22}

        self.port = port
        self.ip_address = ip_address
        self.classifier_output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.classifier_output_socket.bind((self.ip_address, self.port))
        self.gestures = gestures
        self.streamer = streamer
        self.classifier = classifier
        self.driver = Driver(servo_pins=pins, gestures=self.gestures)

    @property
    def port(self):
        return self.port
    
    @port.setter
    def port(self, value):
        if not isinstance(value, int):
            raise ValueError("Port must be an integer")
        self.port = value

    @property
    def ip_address(self):
        return self.ip_address
    
    @ip_address.setter
    def ip_address(self, value):
        if not isinstance(value, str):
            raise ValueError("IP address must be a string")
        self.ip_address = value

    @property
    def gestures(self):
        return self.gestures
    
    @gestures.setter
    def gestures(self, value):
        if not isinstance(value, dict):
            raise ValueError("Gestures must be a dictionary")
        self.gestures = value

    @property
    def streamer(self):
        return self.streamer
    
    @streamer.setter
    def streamer(self, value):
        if not isinstance(value, Streamer):
            raise ValueError("Streamer must be a Streamer object")
        self.streamer = value

    @property
    def classifier(self):
        return self.classifier
    
    @classifier.setter
    def classifier(self, value):
        if not isinstance(value, TRPCProcessor):
            raise ValueError("Classifier must be a TRPCProcessor object")
        self.classifier = value

    @property
    def driver(self):
        return self.driver
    
    @driver.setter
    def driver(self, value):
        if not isinstance(value, Driver):
            raise ValueError("Driver must be a Driver object")
        self.driver = value

    def start(self):
        """Runs the startup process for the controller. This includes starting the streamer and the classifier."""
        # TODO: Have streamer run in a separate process
        self.streamer.run()
        self.classifier.run()
        logger.info("Controller started")

    def listen(self):
        """Runs the controller and sends the appropriate commands to the robot arm based on the classification."""
        logger.info("Running controller")
        while True:
            try:
                data, addr = self.classifier_output_socket.recvfrom(1024)  # Receive up to 1024 bytes
                gesture_class, prob, timestamp = data.decode().split()  # Decode the received bytes
                if int(gesture_class) in self.gestures.keys():
                    self.driver.execute_command(self.gestures[int(gesture_class)])
            except KeyboardInterrupt:
                self.stop()
                logger.info("Detected keyboard interrupt. Stopping controller and subordinates...")
                break

    def stop(self):
        self.streamer.close_socket()
        self.classifier.close()
        self.streamer.close_socket()
