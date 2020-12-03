'''
@haeejuut
Mouthflapper, the part where we record sound from mic
'''
import sounddevice as sd
import numpy as np

from sklearn.preprocessing import minmax_scale
from os import system, name

# Sounddevice props
args = {
    'device' : 1,   
    'duration' : 5,
    'samplerate' : 44100,
    'downsample' : 10,
    'channels' : 2
}
outdata, minVal, maxVal = (None,)*3

def clear(): 
    ''' Clears console '''
    # for windows 
    if name == 'nt': 
        _ = system('cls')
    # for posix 
    else: 
        _ = system('clear') 

def data_handler(indata):
    ''' Calculate normalized audio value (0-1) from the average of input'''
    global minVal, maxVal, outdata
    # Scale to 0 - 1 and take average
    outdata = minmax_scale(indata)
    # Do other stuff to channel data ...

def data_printer(data):
    clear()
    print(str.format('''# {0}
                     \n# {1}''',data[0], data[1]))


def audio_callback(indata, frames, time, status):
    ''' Audio callback for the stream element '''
    if status:
        print(status)
    data_handler(indata)

def main():
    # Init stream and duration of recording
    global outdata
    stream = sd.InputStream(
            device=args['device'],
            channels=args['channels'],
            samplerate=args['samplerate'],
            callback=audio_callback
    )

    recording = True
    try:
        with stream:
            while recording:
                clear()
                print(outdata)
    except KeyboardInterrupt:
        recording = False
        print('Exited via keyboard interruption')

        

if __name__ == '__main__':
    main()
