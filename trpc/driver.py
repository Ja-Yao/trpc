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
        self.servo_pins = servo_pins
        self.gestures = gestures
        
        pin_factory=PiGPIOFactory()
        self.servos = {servo: Servo(pin, pin_factory) for servo, pin in self.servo_pins.items()}
        self.state = "No Movement"

    @property
    def servo_pins(self):
        return self.servo_pins
    
    @servo_pins.setter
    def servo_pins(self, value):
        if not isinstance(value, dict):
            raise ValueError(f"Invalid servo_pins: {value}")
        self.servo_pins = value

    @property
    def state(self):
        return self.state
    
    @state.setter
    def state(self, value):
        if value not in self.gestures.values():
            raise ValueError(f"Invalid state: {value}")
        self.state = value       

    def execute_command(self, command: Dict[str, int | str]):
        """Sends the command to the given servo

            Args:
                command: The command to be sent to the servo
        """
        gesture = command.get("gesture")
        servo = self.servos.get(f"Servo {command.get('servo')}")  # Convert the key to a string
        value = command.get("value")

        if gesture == self.state:
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
            
            self.state = gesture
        except:
            logger.error(f"Invalid or unknown command: {command}")

    def disconnect_pins(self):
        """Disconnects the pins and the servos"""
        for servo in self.servos.values():
            servo.close()
        logger.info("Disconnected pins")
