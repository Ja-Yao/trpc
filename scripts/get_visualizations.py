import sys
from multiprocessing import Process

from libemg.data_handler import OfflineDataHandler, OnlineDataHandler
from libemg.emg_classifier import EMGClassifier, OnlineEMGClassifier
from libemg.feature_extractor import FeatureExtractor
from libemg.utils import make_regex

from trpc import TRPCStreamer

if __name__ == "__main__":
    streamer = TRPCStreamer()
    odh = OnlineDataHandler()
    fe = FeatureExtractor()
    feature_list = fe.get_feature_groups()["LS9"]
    window_size = 250
    window_increment = 10

    classes_values = ["0", "1", "2"]
    classes_regex = make_regex(left_bound="_C_", right_bound="_EMG.csv", values=classes_values)
    reps_values = ["0", "1", "2", "3", "4", "5", "6", "7"]
    reps_regex = make_regex(left_bound="R_", right_bound="_C_", values=reps_values)
    dic = {
        "reps": reps_values,
        "reps_regex": reps_regex,
        "classes": classes_values,
        "classes_regex": classes_regex
    }

    dh = OfflineDataHandler()
    dh.get_data(folder_location='data/', filename_dic=dic, delimiter=',')
    train_data = dh.isolate_data("reps", [0, 1, 2, 3, 4])

    train_windows, train_meta = train_data.parse_windows(window_size, window_increment)

    # Step 2: Extract features from training data
    training_features = fe.extract_feature_group("LS9", train_windows)

    classifier = OnlineEMGClassifier(offline_classifier=EMGClassifier.from_file("classifiers/lda.pickle"),
                                     window_size=window_size, window_increment=window_increment,
                                     online_data_handler=odh, features=feature_list, output_format="probabilities")
    streamer_process = Process(target=streamer.read_emg)
    try:
        streamer_process.start()
        classifier.run()
        odh.visualize_feature_space(feature_dic=training_features, window_size=window_size,
                                    window_increment=window_increment, sampling_rate=860, normalize=True)
        classifier.visualize(legend=["Hand Open", "Hand Close", "No Movement"])
    except KeyboardInterrupt:
        streamer.close_socket()
        streamer_process.terminate()
        classifier.stop_running()
        print("Exiting...")
        sys.exit(0)
