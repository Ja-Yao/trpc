from trpc import Streamer
import time

#initialize streamer object
my_streamer = Streamer()

#setup i2c module 
handle = my_streamer.i2c_setup()


sample_num = 128 # default value

for i in range(sample_num*2):
    my_streamer.analog_input_selector(handle)
    print(my_streamer.pins)
    i+=1

    
    

