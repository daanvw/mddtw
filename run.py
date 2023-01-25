import numpy as np
import matplotlib.pyplot as plt
import time

import mddtw
import visualize

def main():
    dictionary = np.load("./datasets/ademhaling.npy", allow_pickle=True).item()
    start = 225000
    series = np.vstack(list(dictionary.values())).T
    series = series[start:start+10000, :]
    series = series[:, 1]

    # A time series is represented as a (n x d)-numpy array where n is the length of the time series and d is its dimensionality
    # f = open("./datasets/ecg-heartbeat-av.csv")
    # series = np.array(f.readlines(), dtype=np.double)

    # Z-normalise time series
    series = (series - np.mean(series, axis=0)) / np.std(series, axis=0)

    # Parameter p determines the 'strictness' of the algorithm  
    #   - higher --> less strict (time series subsequences match more easily)
    #   - lower  --> more strict (time series subsequences match less easily) 
    p = 0.66

    # Number of motifs to be found
    nb_motifs = 4

    # Sampling frequency
    fs = 25
    # Max and min duration in seconds
    dur_min = 2
    dur_max = 6

    l_min = int(dur_min * fs)
    l_max = int(dur_max * fs)

    # This parameter determines how much the motifs may overlap
    overlap = 0

    # Other parameters
    gamma = 1
    tau, gamma = mddtw.estimate_tau_from_std(series, p, gamma=gamma)
    delta = -10 * tau
    step_sizes = np.array([(1, 1), (1, 2), (2, 1)])
    buffer = max(l_min // 2, 10)
    delta_factor = 0.5

    motifs, _ = run_and_time(series, nb_motifs, tau=tau, delta=delta, delta_factor=delta_factor, l_min=l_min, l_max=l_max, buffer=buffer, overlap=overlap, step_sizes=step_sizes)
    visualize.plot_motif_sets(series, motifs)
    plt.show()


# am and cm
def run_and_time(series, nb_motifs, tau, delta, delta_factor=0.5, l_min=4, l_max=None, buffer=None, overlap=0, step_sizes=np.array([[1, 1], [1, 2], [2, 1]])):
    md = mddtw.MDDTW(series, tau=tau, delta=delta, delta_factor=delta_factor, l_min=l_min, l_max=l_max, step_sizes=step_sizes, use_c=False)
    start_time_total = time.time()
    start_time = time.time()
    md.align()
    end_time = time.time()
    print(f"Align took: {end_time - start_time} seconds")

    start_time = time.time()
    md.kbest_paths(buffer=buffer)
    end_time = time.time()
    print(f"Paths took: {end_time - start_time} seconds")

    start_time = time.time()
    md.calculate_fitnesses(allowed_overlap=overlap, pruning=True)
    end_time = time.time()
    print(f"Fitness took: {end_time - start_time} seconds")

    start_time = time.time()
    motifs = md.kbest_motifs(k=nb_motifs, overlap=overlap)
    end_time = time.time()
    print(f"Best Motifs took: {end_time - start_time} seconds")
    end_time_total = time.time()
    return motifs, end_time_total - start_time_total

def run(series, nb_motifs, tau, delta, delta_factor=0.5, l_min=4, l_max=None, buffer=None, overlap=0, step_sizes=np.array([[1, 1], [1, 2], [2, 1]])):
    md = mddtw.MDDTW(series, tau=tau, delta=delta, delta_factor=delta_factor, l_min=l_min, l_max=l_max, step_sizes=step_sizes, use_c=False)
    md.kbest_paths(buffer=buffer)
    md.calculate_fitnesses(allowed_overlap=overlap, pruning=True)
    motifs = md.kbest_motifs(k=nb_motifs, overlap=overlap)
    return motifs

main()