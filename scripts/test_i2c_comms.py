from trpc import streamer

#initialize streamer object
my_streamer = streamer()

#setup i2c module 
handle = my_streamer.i2c_setup()

signal_per_sec = 128 # default value


for i in range(signal_per_sec):
    my_streamer.analog_input_selector(handle)
    print(my_streamer.pins)
    i+=1

    
    

