from os.path import exists
from time import sleep
from libemg.datasets import OneSubjectMyoDataset
from libemg.streamers import mock_emg_stream
from trpc import Controller, Streamer, TRPCProcessor
from trpc.utils.logger import get_logger


logger = get_logger(__name__)

if __name__ == "__main__":
    if exists("data/OneSubjectMyoDataset"):
        pass
    else:
        # Download the data if it doesn't exist
        logger.info("Downloading data...")
        dataset = OneSubjectMyoDataset(save_dir="data", redownload=False)

    classes = {0: "Hand Open", 1: "Hand Close", 2: "No Movement", 3: "Wrist Extension", 4: "Wrist Flexion"}

    controller = Controller(streamer=Streamer(), classifier=TRPCProcessor(model="SVM"))
    controller.start()
    mock_emg_stream(file_path="data/OneSubjectMyoDataset/stream/raw_emg.csv", num_channels=8, sampling_rate=200)
    sleep(120)
    controller.stop()
    