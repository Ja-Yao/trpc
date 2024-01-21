from typing import Optional
from libemg.data_handler import OnlineDataHandler


class Processor:
    """Processor class for processing data from a device to the LibEMG pipeline"""
    def __init__(self) -> None:
        # The handler listens to UDP port 12345 by default, with ip address 127.0.0.1.
        # No need to specify these parameters unless we need to change them.
        self.odh = OnlineDataHandler(max_buffer=1024)
        self.classifier = None
        self.set_up_classifier()
        self.odh.start_listening()

    def process_data(self) -> None:
        """Processes data from the electrodes."""
        pass

    def set_up_classifier(self,
                          window_size: Optional[int] = 40,
                          window_increment: Optional[int] = 20,
                          model: Optional[str] = 'LS4',
                          ) -> None:
        """Creates the feature classifier for the processor.

        Args:
            window_size: Size of the window for the classifier
            window_increment: Increment of the window for the classifier
            model: Model to use for the classifier
        """
        pass

    def close(self) -> None:
        """Closes the processor"""
        self.odh.stop_listening()
        self.classifier.stop_running()

