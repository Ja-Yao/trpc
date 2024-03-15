from multiprocessing import Lock

import matplotlib.pyplot as plt
from matplotlib.dates import date2num

from trpc import TRPCStreamer

if __name__ == "__main__":
    lock = Lock()
    streamer = TRPCStreamer(lock)
    plot_data = streamer.read_emg()

    dates = date2num([x['timestamp'] for x in plot_data])
    plt.plot_date(dates, [x['voltage'] for x in plot_data])
    # plt.plot(plot_data_convert, label='converted to signed')
    plt.xlabel('Time')
    plt.ylabel('Voltage (V)')
    plt.grid(True)
    plt.legend()

    plt.show()
    
    exit(0)
