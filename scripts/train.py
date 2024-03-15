from multiprocessing import Lock, Process

from libemg.data_handler import OnlineDataHandler
from libemg.screen_guided_training import ScreenGuidedTraining

from trpc import TRPCStreamer

if __name__ == "__main__":
    lock = Lock()
    s = TRPCStreamer(lock)
    odh = OnlineDataHandler(emg_arr=True)
    odh.start_listening()
    p = Process(target=s.read_emg, daemon=False)
    p.start()

    train_ui = ScreenGuidedTraining()
    train_ui.download_gestures([1, 2, 3, 6, 7], "data/gestures/", download_gifs=True)
    train_ui.launch_training(odh, output_folder="data/training/sgt/", rep_folder="data/training/test")
