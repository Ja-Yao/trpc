from libemg.data_handler import OnlineDataHandler
from libemg.screen_guided_training import ScreenGuidedTraining
from trpc import TRPCStreamer

if __name__ == "__main__":
    s = TRPCStreamer()
    odh = OnlineDataHandler(emg_arr=True)
    odh.start_listening()

    train_ui = ScreenGuidedTraining()
    train_ui.download_gestures([1, 2, 3, 6, 7], "data/gestures/", download_gifs=True)
    train_ui.launch_training(odh, output_folder="data/training/sgt/", rep_folder="data/training/test")
