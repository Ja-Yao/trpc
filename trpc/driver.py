from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from typing import Dict
from trpc.utils.logger import get_logger

logger = get_logger(__name__)


class Driver:
    """Driver class for sending commands to the servos. This class takes in the servo pins and the port and ip address
        of the processor output stream as parameters.

        Args:
            servo_pins: Dictionary of servo number and corresponding pins
            gestures: Dictionary of gesture number and corresponding command
    """
    def __init__(self, servo_pins: Dict[str, int], gestures: Dict[int, Dict[str, int | str]]):
        self.__servo_pins = servo_pins
        self.__gestures = gestures
        self.__servos = {servo: Servo(pin=pin, pin_factory=PiGPIOFactory(host="127.0.1.1")) for servo, pin in self.__servo_pins.items()}

    def execute_command(self, command: Dict[str, int | str]):
        """Sends the command to the given servo

            Args:
                command: The command to be sent to the servo
        """
        logger.info(f"Executing command: {command}")
        gesture = command.get("gesture")
        servo = self.__servos.get(f"Servo {command.get('servo')}")  # Convert the key to a string
        value = command.get("value")

        if servo is not None:
            if value == 0:
                logger.info("Returning to mid position")
                servo.mid()
            elif value == 1:
                logger.info("Moving to max position")
                servo.max()
            elif value == -1:
                logger.info("Moving to min position")
                servo.min()
