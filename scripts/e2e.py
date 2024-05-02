import subprocess
from argparse import ArgumentParser

from trpc import Controller, TRPCStreamer, TRPCProcessor
from trpc.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--classifier-file-path", type=str, help="Path to the classifier file")

    args = parser.parse_args()
    file_path = args.classifier_file_path

    if not file_path:
        raise ValueError("Please provide the path to the classifier file")

    subprocess.run(["sudo", "pigpiod"])

    controller = Controller(streamer=TRPCStreamer(), classifier=TRPCProcessor(classifier_path=file_path))

    try:
        controller.start()
        controller.listen()
    except KeyboardInterrupt:
        controller.stop()
        subprocess.run(["sudo", "killall", "pigpiod"])
        logger.info("Controller stopped")
        exit(0)
