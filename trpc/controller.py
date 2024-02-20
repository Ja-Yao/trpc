import socket
import pigpio

from gpiozero import Servo
from typing import Any, Dict
from trpc.utils.logger import get_logger
from trpc import Streamer, Processor

logger = get_logger(__name__)

SERVO_1_PIN = 17

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

    def __init__(self, streamer: Streamer, classifier: Processor, port: int = 12346, ip_address: str = "127.0.0.1", 
                 gestures: Dict[int, Dict[str, Any]] = {}, pins: Dict[str, int] = {}):
        from trpc import TRPCDriver
        if not gestures:
            gestures = {
                0: {
                    "gesture": "Hand Open",
                    "servo": "Servo 1",
                    "action": Servo.max
                },
                1: {
                    "gesture": "Hand Close",
                    "servo": "Servo 1",
                    "action": Servo.min
                },
                2: {
                    "gesture": "No Movement",
                    "servo": "Servo 1",
                    "action": Servo.mid
                }
            }

        if not pins:
            # These are arbitrary pin values. They should be replaced with the actual pin values
            pins = { "Servo 1": SERVO_1_PIN }

        pigpio.pi()
        self._port = port
        self._ip_address = ip_address
        self._classifier_output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._classifier_output_socket.bind((self._ip_address, self._port))
        self._gestures = gestures
        self._streamer = streamer
        self._classifier = classifier
        self._driver = TRPCDriver(servo_pins=pins, gestures=self._gestures)

    @property
    def port(self):
        return self._port
    
    @property
    def ip_address(self):
        return self._ip_address
    
    @property
    def gestures(self):
        return self._gestures
    
    @property
    def streamer(self):
        return self._streamer
    
    @property
    def classifier(self):
        return self._classifier

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def gestures(self):
        return self._gestures

    @property
    def streamer(self):
        return self._streamer

    @property
    def classifier(self):
        return self._classifier

    @property
    def driver(self):
        return self._driver

    def start(self):
        """Runs the startup process for the controller. This includes starting the streamer and the classifier."""
        # TODO: Have streamer run in a separate process
        # self._streamer.run()
        self._classifier.run()
        logger.info("Controller started")

    def listen(self):
        """Runs the controller and sends the appropriate commands to the robot arm based on the classification."""
        while True:
            try:
                data, addr = self._classifier_output_socket.recvfrom(1024)  # Receive up to 1024 bytes
                gesture_class, confidence, timestamp = data.decode().split()  # Decode the received bytes
                if int(gesture_class) in self._gestures.keys():
                    self._driver.execute_command(self._gestures[int(gesture_class)])
            except KeyboardInterrupt:
                logger.info("Detected keyboard interrupt. Stopping controller and subordinates...")
                break
        
        self.stop()

    def stop(self):
        self._streamer.close_socket()
        self._classifier.close()
        self._driver.disconnect_pins()
