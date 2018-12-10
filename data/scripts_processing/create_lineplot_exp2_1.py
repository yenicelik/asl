# First, parse the file as json
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_errorbars

# Do it for experiment 1 for now

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp2_1_backup/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp2_1/"

def get_pattern_exp2_1(virtual_client_threads, repetition, client, write):
    """
        Get's the filename given the above specifications.
        This is for easier handling of the data
    :param virtual_client_threads:
    :param repetition:
    :param client:
    :param write:
    :return:
    """
    out = "virtualclients_{}__rep_{}_client_{}_writes_{}.txt"
    out = out.format(virtual_client_threads, repetition, client, write)
    return BASEPATH + out


#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp2_1():
    """
        Iterates through all the parameter combinations
    :return:
    """

    create_datadir_if_not_exists(GRAPHPATH)

    for write in ["0", "1"]:

        labels = []
        throughput_means = []
        throughput_stddevs = []
        latency_means = []
        latency_stddevs = []

        for virtual_client_threads in [(2 ** x) for x in range(0, 6)]:
            all_throughputs = []  # From here on, we average over all values
            all_latencies = []

            for repetition in range(3):
                for client in ['Client1', 'Client2', 'Client3']:
                    filename = get_pattern_exp2_1(virtual_client_threads, repetition, client, write)

                    throughput, latency = get_throughput_latency_default_memtier(filepath=filename)
                    # print("Throughput and latency are: ", throughput, latency)

                    all_throughputs.append(throughput)
                    all_latencies.append(latency)

            labels.append(virtual_client_threads)

            throughput_mean = np.sum(all_throughputs) / 3.
            throughput_stddev = np.std(all_throughputs)
            # Append to arrays
            throughput_means.append(throughput_mean)
            throughput_stddevs.append(throughput_stddev)

            latency_mean = np.mean(all_latencies)
            latency_stddev = np.std(all_latencies)
            # Append to arrays
            latency_means.append(latency_mean)
            latency_stddevs.append(latency_stddev)

            print("NEXT")
            print(throughput_mean, latency_mean)

        print("###write", write, throughput_means)
        ###write 0 [2937.2533333333336, 2935.7933333333335, 2936.99, 2940.6299999999997, 2938.976666666667, 2926.0533333333333]
        ###write 1 [5791.943333333334, 11381.436666666666, 11744.933333333332, 14595.123333333335, 17632.553333333333, 17632.95666666667]

        # Plot the latency and throughput measures
        render_lineargraph_errorbars(
            labels=labels,
            mean_array=throughput_means,
            stddev_array=throughput_stddevs,
            filepath=GRAPHPATH + "exp2_1_throughput_write_{}".format(write),
            is_latency=False
        )
        render_lineargraph_errorbars(
            labels=labels,
            mean_array=latency_means,
            stddev_array=latency_stddevs,
            filepath=GRAPHPATH + "exp2_1_latency_write_{}".format(write),
            is_latency=True
        )


if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp2_1()
