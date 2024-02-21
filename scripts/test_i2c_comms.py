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
        my_streamer.analog_input_selector() # collects pin data on 4 inputs
        print(f"{hex(my_streamer.pins[0])}  {hex(my_streamer.pins[1])} {hex(my_streamer.pins[2])} {hex(my_streamer.pins[3])}")
        
    subprocess.run(["sudo", "killall", "pigpiod"])
    
        

    
    

