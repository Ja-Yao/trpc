from trpc import streamer

#initialize streamer object
my_streamer = streamer()

#setup i2c module 
handle = my_streamer.i2c_setup()


for i in range(4):
    my_streamer.analog_input_selector(handle)
    print(my_streamer.pins)

    
    

