import socket
import datetime

from os.path import exists
from libemg.datasets import OneSubjectMyoDataset
from trpc import TRPCProcessor


def handle_close(p: TRPCProcessor, s: socket.socket):
    p.close()
    s.close()


if __name__ == "__main__":
    if not exists("data/OneSubjectMyoDataset"):
        # Download the data if it doesn't exist
        print("Downloading data...")
        dataset = OneSubjectMyoDataset(save_dir="data", redownload=False)

    classes = {0: "Hand Open", 1: "Hand Close", 2: "No Movement", 3: "Wrist Extension", 4: "Wrist Flexion"}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 12346))
    processor = TRPCProcessor(model="SVM")
    try:
        processor.run()
        while True:
            data, addr = sock.recvfrom(1024)  # Receive up to 1024 bytes
            gesture_class, prob = data.decode().split()  # Decode the received bytes
            try:
                print({
                    "class": classes[int(gesture_class)],
                    "confidence": f"{round(float(prob) * 100, 2)}%",
                    "timestamp": datetime.datetime.now().strftime("%F %T.%f")[:-3]
                })
            except KeyError:
                print({
                    "class": "Unknown",
                    "confidence": "100.0%",
                    "timestamp": datetime.datetime.now().strftime("%F %T.%f")[:-3]
                })
    except KeyboardInterrupt:
        handle_close(processor, sock)