import socket

from typing import Dict


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
                    "servo": 1,
                    "value": 1
                },
                1: {
                    "gesture": "Hand Close",
                    "servo": 1,
                    "value": -1
                },
                2: {
                    "gesture": "No Movement",
                    "servo": 1,
                    "value": 0
                }
            }

        if not pins:
            # These are arbitrary pin values. They should be replaced with the actual pin values
            pins = {"Servo 1": 17, "Servo 2": 18, "Servo 3": 19, "Servo 4": 20, "Servo 5": 21, "Servo 6": 22}

        self.port = port
        self.ip_address = ip_address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip_address, self.port))
        self.gestures = gestures
        self.streamer = streamer
        self.classifier = classifier
        self.driver = Driver(servo_pins=pins, gestures=self.gestures)

    def start(self):
        """Runs the controller"""
        # TODO: Have streamer run in a separate process
        # self.streamer.run()
        self.classifier.run()
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)  # Receive up to 1024 bytes
                gesture_class, prob = data.decode().split()  # Decode the received bytes
                if gesture_class in self.gestures and float(prob) > 0.8:
                    self.driver.execute_command(self.gestures[int(gesture_class)])
            except KeyboardInterrupt:
                self.stop()
                break

    def stop(self):
        self.streamer.close_socket()
        self.classifier.close()
