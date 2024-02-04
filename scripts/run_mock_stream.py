import numpy as np
import pickle
import socket
import time

from alive_progress import alive_bar
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--file-path', type=str, default='data/OneSubjectMyoDataset/stream/raw_emg.csv')
    parser.add_argument('--num-channels', type=int, default=8)
    parser.add_argument('--sampling-rate', type=int, default=200)

    args = parser.parse_args()
    file_path = args.file_path
    sampling_rate = args.sampling_rate
    num_channels = args.num_channels

    # the following code is from libemg.streamers
    data = np.loadtxt(file_path, delimiter=",")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with alive_bar(len(data)) as bar:
        for index in range(len(data)):
            val = time.time() + (1000 / sampling_rate) / 1000
            while time.time() < val:
                pass
            data_arr = pickle.dumps(list(data[index][:num_channels]))
            sock.sendto(data_arr, ('127.0.0.1', 12345))
            bar()
    sock.close()
