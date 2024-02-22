import matplotlib.pyplot as plt
from trpc import TRPCStreamer

if __name__ == "__main__":
    streamer = TRPCStreamer()
    plot_data = streamer.read_emg()

    plt.plot(plot_data, label='regular')
    #plt.plot(plot_data_convert, label='converted to signed')
    plt.xlabel('Sample')
    plt.ylabel('Value')
    plt.title('2\'s Complement Data Plot')
    plt.grid(True)
    plt.legend()

    plt.show()
    
    exit(0)
