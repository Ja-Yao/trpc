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

    controller = Controller(streamer=Streamer(), classifier=TRPCProcessor(model="SVM"))
    controller.start()
    controller.listen()
    