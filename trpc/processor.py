from abc import ABC, abstractmethod
from os import makedirs
from os.path import dirname, exists
from typing import List, Optional

from libemg.data_handler import OnlineDataHandler, OfflineDataHandler
from libemg.emg_classifier import EMGClassifier, OnlineEMGClassifier
from libemg.feature_extractor import FeatureExtractor
from libemg.utils import make_regex

from trpc.utils.logger import get_logger

logger = get_logger(__name__)


class Processor(ABC):
    """Abstract Class for processing data from a device to the LibEMG pipeline

        Args:
            window_size: Size of the window for the classifier
            window_increment: Increment of the window for the classifier
            feature_set: The group of features to extract. This can be a string or a custom list of features. See the
                         get_feature_groups() function for predefined groups.
            model: Model to use for the classifier
            classifier_path: Path to the classifier file. If the file does not exist, the classifier will be trained
                             from scratch and saved to this path.
    """

    def __init__(self, window_size: int = 40, window_increment: int = 20, feature_set: str | List[str] = "LS9",
                 model: str = "LDA", classifier_path: Optional[str] = None) -> None:
        self.__window_size = window_size
        self.__window_increment = window_increment
        self._feature_set = feature_set
        self._model = model
        if classifier_path is None:
            self.classifier_path = "classifiers/lda.pickle"

        # The handler listens to UDP port 12345 by default, with ip address 127.0.0.1.
        # No need to specify these parameters unless we need to change them.
        self._odh = OnlineDataHandler()
        self._odh.start_listening()
        self._classifier = self._set_up_classifier()

    # Not providing a setter for any of the properties because they are not meant to be changed after initialization
    @property
    def window_size(self):
        return self.__window_size

    @property
    def window_increment(self):
        return self.__window_increment

    @property
    def feature_set(self):
        return self._feature_set

    @property
    def model(self):
        return self._model

    @property
    def odh(self):
        return self._odh

    @property
    def classifier(self):
        return self._classifier

    def _set_up_classifier(self):
        """Creates the feature classifier for the processor."""
        fe = FeatureExtractor()
        feature_list = fe.get_feature_groups()[self._feature_set] if isinstance(self._feature_set, str) \
            else self._feature_set

        try:
            emg = EMGClassifier.from_file(self.classifier_path)
            logger.info("Loaded classifier from file")
        except FileNotFoundError:
            logger.info("Classifier not found. Training classifier from scratch...")
            # Step 1: Parse training data
            classes_values = ["0", "1", "2", "3", "4"]
            classes_regex = make_regex(left_bound="_C_", right_bound=".csv", values=classes_values)
            reps_values = ["0", "1", "2"]
            reps_regex = make_regex(left_bound="R_", right_bound="_C_", values=reps_values)
            dic = {
                "reps": reps_values,
                "reps_regex": reps_regex,
                "classes": classes_values,
                "classes_regex": classes_regex
            }

            odh = OfflineDataHandler()
            odh.get_data(folder_location='data/', filename_dic=dic, delimiter=',')
            train_windows, train_meta = odh.parse_windows(self.__window_size, self.__window_increment)

            # Step 2: Extract features from training data
            training_features = fe.extract_features(feature_list, train_windows)

            # Step 3: Create training data set
            data_set = {'training_features': training_features, 'training_labels': train_meta['classes']}

            # Step 4: Train the classifier on the training data
            emg = EMGClassifier()
            # Having velocity control is useful for proportional control of the robot. See
            # https://libemg.github.io/libemg/documentation/classification/classification.html#velocity-control-sup-4-sup
            emg.add_velocity(train_windows, train_meta['classes'])
            emg.add_rejection(0.8)
            emg.fit(model=self.model, feature_dictionary=data_set.copy())
            if not exists(self.classifier_path):
                makedirs(dirname(self.classifier_path), exist_ok=True)
            emg.save(self.classifier_path)

        return OnlineEMGClassifier(emg, self.__window_size, self.__window_increment, self.odh, feature_list)

    @abstractmethod
    def run(self, block: bool = False):
        """Runs the processor. This can be a blocking or non-blocking function.

            Args:
                block: If True, the processor will block the main thread until the processor is stopped. If False, it
                          will run in a separate process.
        """
        pass

    @abstractmethod
    def close(self):
        """Closes the processor"""
        pass


class TRPCProcessor(Processor):
    """Class for processing data from a device to the LibEMG pipeline

        Args:
            window_size: Size of the window for the classifier
            window_increment: Increment of the window for the classifier
            feature_set: The group of features to extract. This can be a string or a custom list of features. See the
                         get_feature_groups() function for predefined groups.
            model: Model to use for the classifier
            classifier_path: Path to the classifier file. If the file does not exist, the classifier will be trained
                             from scratch and saved to this path.
    """

    def __init__(self, window_size: int = 40, window_increment: int = 20, feature_set: str | List[str] = "LS9",
                 model: str = "LDA", classifier_path: Optional[str] = None) -> None:
        super().__init__(window_size, window_increment, feature_set, model, classifier_path)

    def run(self, block: bool = False):
        self._classifier.run(block=block)

    def close(self):
        self.odh.stop_listening()
        self._classifier.stop_running()
