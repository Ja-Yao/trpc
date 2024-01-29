from os import makedirs
from os.path import dirname, exists
from typing import List, Optional

from libemg.data_handler import OnlineDataHandler, OfflineDataHandler
from libemg.feature_extractor import FeatureExtractor
from libemg.emg_classifier import EMGClassifier, OnlineEMGClassifier
from libemg.utils import make_regex


class TRPCProcessor:
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

    def __init__(self, window_size: int = 40, window_increment: int = 20, feature_set: str | List[str] = "LS4",
                 model: str = "SVM", classifier_path: Optional[str] = None) -> None:
        self.__window_size = window_size
        self.__window_increment = window_increment
        self.feature_set = feature_set
        self.model = model
        if classifier_path is None:
            self.classifier_path = "classifiers/svm.pickle"
        
        # The handler listens to UDP port 12345 by default, with ip address 127.0.0.1.
        # No need to specify these parameters unless we need to change them.
        self.odh = OnlineDataHandler()
        self.odh.start_listening()
        self.classifier = self._set_up_classifier()

    def _set_up_classifier(self):
        """Creates the feature classifier for the processor."""
        fe = FeatureExtractor()
        feature_list = fe.get_feature_groups()[self.feature_set] if isinstance(self.feature_set, str) \
            else self.feature_set

        try:
            emg = EMGClassifier.from_file(self.classifier_path)
            print("Loaded classifier from file")
        except FileNotFoundError:
            print("Classifier not found. Training classifier from scratch...")
            # Step 1: Parse training data
            classes_values = ["0", "1", "2", "3", "4"]
            classes_regex = make_regex(left_bound="_C_", right_bound=".csv", values=classes_values)
            reps_values = ["0", "1", "2", "3"]
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

    def get_data_handler(self):
        """Returns the data handler"""
        return self.odh

    def get_classifier(self):
        """Returns the classifier"""
        return self.classifier

    def run(self):
        self.classifier.run(block=False)

    def close(self) -> None:
        """Closes the processor"""
        self.odh.stop_listening()
        self.classifier.stop_running()
