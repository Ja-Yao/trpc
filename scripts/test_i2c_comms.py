from trpc import Streamer
import time
import subprocess


if __name__ == "__main__":
    subprocess.run(["sudo", "pigpiod"])
    
    #initialize streamer object
    my_streamer = Streamer()

    #setup i2c module 
    handle = my_streamer.setup_i2c()


    sample_num = 128 # default value
    #to collect a large number of input sets
    for i in range(sample_num*2):
        my_streamer.analog_input_selector(handle) # collects pin data on 4 inputs
        print(my_streamer.pins) # prints out set of pins per sample
        i+=1
        
    subprocess.run(["sudo", "killall", "pigpiod"])
    
        

    
    

