from multiprocessing import Process, Lock

from trpc import TRPCProcessor, TRPCStreamer
from trpc.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    lock = Lock()
    s = TRPCStreamer(lock)
    p = Process(target=s.read_emg, daemon=False)
    processor = TRPCProcessor(model="SVM")
    try:
        p.start()
        processor.run()
    except KeyboardInterrupt:
        logger.info("Shutting down processor...")
        processor.close()
        logger.info("Shutting down streamer...")
        p.terminate()
        s.close_socket()
        exit(0)
