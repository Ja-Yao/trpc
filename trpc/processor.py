from libemg.data_handler import OnlineDataHandler, OfflineDataHandler
from libemg.feature_extractor import FeatureExtractor
from libemg.emg_classifier import EMGClassifier, OnlineEMGClassifier
from libemg.utils import make_regex


class Processor:
    """Processor class for processing data from a device to the LibEMG pipeline"""

    def __init__(self) -> None:
        # The handler listens to UDP port 12345 by default, with ip address 127.0.0.1.
        # No need to specify these parameters unless we need to change them.
        self.odh = OnlineDataHandler()
        self.odh.start_listening()

        self.classifier = self._set_up_classifier()
        self.classifier.run(block=False)

    def _set_up_classifier(self, window_size: int = 40, window_increment: int = 20,
                          feature_set: str = 'LS4', model: str = "SVM"):
        """Creates the feature classifier for the processor.

        Args:
            window_size: Size of the window for the classifier
            window_increment: Increment of the window for the classifier
            feature_set:  The group of features to extract. See the get_feature_list() function for valid options.
            model: Model to use for the classifier
        """
        classes_values = ["0","1","2","3","4"]
        classes_regex = make_regex(left_bound = "_C_", right_bound=".csv", values = classes_values)
        reps_values = ["0", "1", "2", "3"]
        reps_regex = make_regex(left_bound = "R_", right_bound="_C_", values = reps_values)
        dic = {
            "reps": reps_values,
            "reps_regex": reps_regex,
            "classes": classes_values,
            "classes_regex": classes_regex
        }

        odh = OfflineDataHandler()
        odh.get_data(folder_location='data/', filename_dic=dic, delimiter=',')
        train_windows, train_meta = odh.parse_windows(window_size, window_increment)

        fe = FeatureExtractor()
        feature_list = fe.get_feature_groups()[feature_set]
        training_features = fe.extract_features(feature_list, train_windows)

        data_set = {'training_features': training_features, 'training_labels': train_meta['classes']}

        emg = EMGClassifier()
        emg.fit(model=model, feature_dictionary=data_set.copy())
        emg.add_rejection(0.8)

        return OnlineEMGClassifier(emg, window_size, window_increment, self.odh, fe.get_feature_groups()[feature_set],
                                   std_out=True)


    def close(self) -> None:
        """Closes the processor"""
        self.odh.stop_listening()
        if self.classifier is not None:
            self.classifier.stop_running()
