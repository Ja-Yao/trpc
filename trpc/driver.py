from abc import ABC, abstractmethod
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from typing import Dict
from trpc.utils.logger import get_logger

logger = get_logger(__name__)

class Driver(ABC):
    """Abstract Driver class for sending commands to the servos. This class takes in the servo pins and the port and ip address
        of the processor output stream as parameters.

        Args:
            servo_pins: Dictionary of servo number and corresponding pins
            gestures: Dictionary of gesture number and corresponding command
    """
    def __init__(self, servo_pins: Dict[str, int], gestures: Dict[int, Dict[str, int | str]]):
        if not isinstance(servo_pins, dict):
            raise ValueError(f"Invalid servo_pins: {servo_pins}")
        
        if not isinstance(gestures, dict):
            raise ValueError(f"Invalid gestures: {gestures}")

        self._servo_pins = servo_pins
        self._gestures = gestures
        
        pin_factory = PiGPIOFactory()
        self._servos = {servo: Servo(pin=pin, pin_factory=pin_factory) for servo, pin in self._servo_pins.items()}
        self._state = "No Movement"

    @abstractmethod
    def execute_command(self, command: Dict[str, int | str]):
        """Sends the command to the given servo

            Args:
                command: The command to be sent to the servo
        """
        pass

    @abstractmethod
    def disconnect_pins(self):
        """Disconnects the pins and the servos"""
        pass

class TRPCDriver(Driver):
    """Driver class for sending commands to the servos. This class takes in the servo pins and the port and ip address
        of the processor output stream as parameters.

        Args:
            servo_pins: Dictionary of servo number and corresponding pins
            gestures: Dictionary of gesture number and corresponding command
    """
    def __init__(self, servo_pins: Dict[str, int], gestures: Dict[int, Dict[str, int | str]]):
        super().__init__(servo_pins, gestures)     

    def execute_command(self, command: Dict[str, int | str]):
        gesture = command.get("gesture")
        servo = self._servos.get(command.get('servo'))
        value = command.get("value")

        if gesture == self._state:
            return

        try:
            if value == 0:
                servo.max()
            elif value == 1:
                servo.min()
            elif value == -1:
                servo.mid()
            
            self._state = gesture
        except:
            logger.error(f"Invalid or unknown command: {command}")

    def disconnect_pins(self):
        for servo in self._servos.values():
            servo.close()
        logger.info("Disconnected pins")
