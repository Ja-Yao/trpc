import subprocess

from trpc import Controller, TRPCStreamer, TRPCProcessor
from trpc.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    subprocess.run(["sudo", "pigpiod"])

    controller = Controller(streamer=TRPCStreamer(), classifier=TRPCProcessor())

    try:
        controller.start()
        controller.listen()
    except KeyboardInterrupt:
        controller.stop()
        subprocess.run(["sudo", "killall", "pigpiod"])
        logger.info("Controller stopped")
        exit(0)
