import numpy as np
import time

from pylsl import StreamInfo, StreamOutlet

channels = 1
srate = 250



def sendingData():
    info = StreamInfo('BioSemi', 'EEG', 1, 250, 'float32', 'myuid34234')
    # next make an outlet
    outlet = StreamOutlet(info)
    #a list of 250 values from 0 to 250 separated by 2pi 
    x = np.linspace(0, 2*np.pi, 250)

    focused = (1,5)
    unfocused = (5,1)
    
    alpha_amp,beta_amp = focused
    attention = True

    count = 0
    while True:
        #change focus every 10 seconds
        if count%(250*10) == 0:
            if attention:
                alpha_amp,beta_amp = unfocused
                attention = False
            else:
                alpha_amp,beta_amp = focused
                attention = True
           

        tstep = x[count%250]#value used to make the waves
        #alpha is between 8 and 12 hz
        #alph1 and 2 are 9hz and 11hz waves with random small changes in amp
        alpha1 = np.sin(tstep*9) * (1 +np.random.randn()/20) * alpha_amp *1.5
        alpha2 = np.sin(tstep*11) * (1 +np.random.randn()/20) * alpha_amp
        
        #alph1 and 2 are 17hz and 28hz waves with random small changes in amp
        beta1 = np.sin(tstep*17) * (1 +np.random.randn()/20) * beta_amp
        beta2 = np.sin(tstep*28) * (1 +np.random.randn()/20) *beta_amp
        
        #sum together the different wave points
        current_sample = sum([alpha1,alpha2,beta1,beta2])
        #just incase we want to change the number of channels 
        outlet.push_sample([current_sample])

        count+=1

        time.sleep(1/srate)

