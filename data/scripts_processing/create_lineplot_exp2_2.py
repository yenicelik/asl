# First, parse the file as json
import json
import os

import numpy as np

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_errorbars

# Do it for experiment 1 for now

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp2_2_backups/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp2_2/"

def get_pattern_exp2_2(virtual_client_threads, repetition, client, server, write):
    """
        Get's the filename given the above specifications.
        This is for easier handling of the data
    :param virtual_client_threads:
    :param repetition:
    :param client:
    :param write:
    :return:
    """
    out = "virtualclients_{}__rep_{}_client_{}__writes_{}.txt_Server{}"
    out = out.format(virtual_client_threads, repetition, client, write, 1 if server == "Server1" else 2)
    return BASEPATH + out


#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp2_2():
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
                for client in ['Client1']:
                    for server in ['Server1', 'Server2']:
                        filename = get_pattern_exp2_2(virtual_client_threads, repetition, client, server, write)

                        throughput, latency = get_throughput_latency_default_memtier(filepath=filename)

                        all_throughputs.append(throughput)
                        all_latencies.append(latency)

            labels.append(virtual_client_threads)

            throughput_mean = np.sum(all_throughputs)  / 3. # Divide by 2, because we have two clients
            throughput_stddev = np.std(all_throughputs)
            # Append to arrays
            throughput_means.append(throughput_mean)
            throughput_stddevs.append(throughput_stddev)

            latency_mean = np.sum(all_latencies) / 3. # Divide by 2, because we have two clients
            latency_stddev = np.std(all_latencies)
            # Append to arrays
            latency_means.append(latency_mean)
            latency_stddevs.append(latency_stddev)

            print("NEXT")
            print(throughput_mean, latency_mean)

        print("###write", write, throughput_means)
        ###write 0 [2173.206666666667, 4134.1466666666665, 5830.243333333333, 5885.3, 5872.653333333333, 5831.44]
        ###write 1 [2067.6566666666668, 3963.2400000000002, 7176.743333333333, 11750.013333333334, 11814.659999999998, 11859.336666666668]

        # Plot the latency and throughput measures
        render_lineargraph_errorbars(
            labels=labels,
            mean_array=throughput_means,
            stddev_array=throughput_stddevs,
            filepath=GRAPHPATH + "exp2_2__throughput_write_{}".format(write),
            is_latency=False
        )
        render_lineargraph_errorbars(
            labels=labels,
            mean_array=latency_means,
            stddev_array=latency_stddevs,
            filepath=GRAPHPATH + "exp2_2__latency_write_{}".format(write),
            is_latency=True
        )


if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp2_2()
