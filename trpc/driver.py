from abc import ABC, abstractmethod
from typing import Callable, Dict

from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

from trpc.utils.logger import get_logger

logger = get_logger(__name__)


class Driver(ABC):
    """Abstract Driver class for sending commands to the servos. This class takes in the servo pins and the port and
        ip address of the processor output stream as parameters.

        Args:
            servo_pins: Dictionary of servo number and corresponding pins
    """

    def __init__(self, servo_pins: Dict[str, int]):
        if not isinstance(servo_pins, dict):
            raise ValueError(f"Invalid servo_pins: {servo_pins}")

        self._servo_pins = servo_pins

        pin_factory = PiGPIOFactory()
        self._servos = {servo: Servo(pin=pin, pin_factory=pin_factory) for servo, pin in self._servo_pins.items()}
        self._state = "No Movement"

    @abstractmethod
    def execute_command(self, command: Dict[str, str | Callable[[Servo], None]]):
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
    """

    def __init__(self, servo_pins: Dict[str, int]):
        super().__init__(servo_pins)

    def execute_command(self, command: Dict[int, Dict[str, str | Callable[[Servo], None]]]):
        gesture = list(command.keys())[0]

        servo: Servo = self._servos.get(command.get(gesture).get('servo'))
        action: Callable[[Servo], None] = command.get(gesture).get("action")

        if gesture == self._state:
            return

        try:
            action(servo)
            self._state = gesture
        except Exception as e:
            logger.error(f"Error executing command: {command}; {str(e)}")

    def disconnect_pins(self):
        for servo in self._servos.values():
            servo.close()
        logger.info("Disconnected pins")
