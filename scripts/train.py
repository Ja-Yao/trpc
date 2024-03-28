import os.path
from multiprocessing import Process

from libemg.data_handler import OnlineDataHandler
from libemg.screen_guided_training import ScreenGuidedTraining

from trpc import TRPCStreamer

if __name__ == "__main__":
    s = TRPCStreamer()
    odh = OnlineDataHandler(emg_arr=True)
    odh.start_listening()
    p = Process(target=s.read_emg, daemon=False)

    try:
        p.start()

        train_ui = ScreenGuidedTraining()
        if not os.path.isdir("data/training/gestures/"):
            train_ui.download_gestures([1, 2, 3], "data/training/gestures/", download_gifs=True)
        train_ui.launch_training(odh, output_folder="data/training/sgt/", rep_folder="data/training/gestures/")

        p.terminate()
        s.close_socket()
        exit(0)
    
    except KeyboardInterrupt:
        p.terminate()
        s.close_socket()
        exit(0)
