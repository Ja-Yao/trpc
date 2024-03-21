import subprocess
from multiprocessing import Lock
from os.path import exists

from libemg.datasets import OneSubjectMyoDataset

from trpc import Controller, TRPCStreamer, TRPCProcessor
from trpc.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    if exists("data/OneSubjectMyoDataset"):
        pass
    else:
        # Download the data if it doesn't exist
        logger.info("Downloading data...")
        dataset = OneSubjectMyoDataset(save_dir="data", redownload=False)
    subprocess.run(["sudo", "pigpiod"])

    lock = Lock()
    controller = Controller(streamer=TRPCStreamer(lock), classifier=TRPCProcessor(model="LDA", feature_set="LS9"))

    try:
        controller.start()
        controller.listen()
    except KeyboardInterrupt:
        controller.stop()
        subprocess.run(["sudo", "killall", "pigpiod"])
        logger.info("Controller stopped")
        exit(0)
