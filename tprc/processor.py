from libemg.data_handler import OnlineDataHandler


class Processor:
    """Processor class for processing data from a device to the LibEMG pipeline"""
    def __init__(self) -> None:
        self.data_handler = OnlineDataHandler()

    def process_data(self):
        """Processes data from device"""
        self.data_handler.start_listening()
        self.data_handler.visualize()

    def close(self):
        """Closes the processor"""
        self.data_handler.stop_listening()
