# ====================================
# Author: Eddie Guo
# Date created: October 17, 2019
#
# Group: NeurAlbertaTech
# Team: Signal Processing
#
# Crude solution to signal processing
# ====================================

from scipy.io import wavfile
from scipy import signal
import numpy as np
import Pull_Audio

def main():
    """Combines all below functions.
    """
    means = indiv_time_means(spectrogram)
    mean = clustered(means, 2)
    print(mean)
    return mean


def indiv_time_means(spectrogram):
    """Takes a spectrogram and returns the means of each frequency associated
    with their respective time points.

    Arguments:
        spectrogram: a spectrogram from a .wav file.

    Returns:
        means (list): a list of means.
    """
    means = []

    i = 0
    while i < len(spectrogram[0]):
        # 'x-axis' represented by i
        # 'y-axis' represented by j
        nums = []

        j = 0
        while j < len(spectrogram):
            # finding the frequency associated with each time point
            nums.append(spectrogram[j, i])
            j += 1
        # finding the mean of the frequencies associated with each time point
        means.append(np.mean(nums))
        i += 1
    return means


def clustered(means, bin_size):
    """Processes a list of means and creates a list of clustered means.

    Arguments:
        means (list): a list of means to process.
        bin_size (int): specified number of means to cluster together.

    Returns:
        clustered_means (list): a list of means of means from a specified bin
        size.
    """
    clustered_mean = 0
    nums_2 = []
    for i in range(len(means)):
        if (means[i] > 1):
            nums_2.append(means[i])
    clustered_mean= np.mean(nums_2)
    return clustered_mean

if __name__ == "__main__":
    Pull_Audio.record()
    sample_rate, samples = wavfile.read('output.wav')  # ./output/audio.wav
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

    main()