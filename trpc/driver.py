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
        self._servo_pins = servo_pins
        self._gestures = gestures
        
        pin_factory = PiGPIOFactory()
        self._servos = {servo: Servo(pin=pin, pin_factory=pin_factory) for servo, pin in self._servo_pins.items()}
        self._state = "No Movement"

    @property
    def servo_pins(self):
        return self._servo_pins
    
    @servo_pins.setter
    def servo_pins(self, value):
        if not isinstance(value, dict):
            raise ValueError(f"Invalid servo_pins: {value}")
        self._servo_pins = value

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if value not in self._gestures.values():
            raise ValueError(f"Invalid state: {value}")
        self._state = value       

    def execute_command(self, command: Dict[str, int | str]):
        """Sends the command to the given servo

            Args:
                command: The command to be sent to the servo
        """
        gesture = command.get("gesture")
        servo = self._servos.get(command.get('servo'))
        value = command.get("value")

        if gesture == self._state:
            logger.info("No change since last command")
            return

        try:
            if value == 0:
                logger.info("Returning to mid position")
                servo.mid()
            elif value == 1:
                logger.info("Moving to max position")
                servo.max()
            elif value == -1:
                logger.info("Moving to min position")
                servo.min()
            
            self._state = gesture
        except:
            logger.error(f"Invalid or unknown command: {command}")

    def disconnect_pins(self):
        """Disconnects the pins and the servos"""
        for servo in self._servos.values():
            servo.close()
        logger.info("Disconnected pins")
