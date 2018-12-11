# First, parse the file as json
import json
import os

import numpy as np
import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_errorbars, \
    render_lineargraph_multiple_errorbars

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

    vc_array = [(2 ** x) for x in range(0, 6)]
    total_virtual_clients = len(vc_array)

    client_throughput_means = np.zeros((total_virtual_clients, 2)) # (virtualclients, number of server, number of read/writes)
    client_latency_means = np.zeros((total_virtual_clients, 2))
    client_throughput_stddev = np.zeros((total_virtual_clients, 2))
    client_latency_stddev = np.zeros((total_virtual_clients, 2))

    labels = [(2 ** x) for x in range(0, 6)]


    for idx, write in enumerate(["0", "1"]):

        for jdx, virtual_client_threads in enumerate([(2 ** x) for x in range(0, 6)]):

            all_throughputs = []  # From here on, we average over all values
            all_latencies = []

            for repetition in range(3):
                for client in ['Client1', 'Client2', 'Client3']:
                    filename = get_pattern_exp2_1(virtual_client_threads, repetition, client, write)

                    throughput, latency = get_throughput_latency_default_memtier(filepath=filename)
                    # print("Throughput and latency are: ", throughput, latency)

                    all_throughputs.append(throughput)
                    all_latencies.append(latency)

            if write == "1":
                client_throughput_means[jdx, idx] = np.sum(all_throughputs) / 3. # Because we have two servers, and the results replicate
                client_throughput_stddev[jdx, idx] = np.std(all_throughputs)

            else:
                client_throughput_means[jdx, idx] = np.sum(all_throughputs) / 3. # Because we have two servers, and the results replicate
                client_throughput_stddev[jdx, idx] = np.std(all_throughputs)

            latency_mean = np.mean(all_latencies) # Divide by 2, because we have two clients
            latency_stddev = np.std(all_latencies)

            client_latency_means[jdx, idx] = latency_mean
            client_latency_stddev[jdx, idx] = latency_stddev

        ###write 0 [2937.2533333333336, 2935.7933333333335, 2936.99, 2940.6299999999997, 2938.976666666667, 2926.0533333333333]
        ###write 1 [5791.943333333334, 11381.436666666666, 11744.933333333332, 14595.123333333335, 17632.553333333333, 17632.95666666667]

        # Plot the latency and throughput measures
        # render_lineargraph_errorbars(
        #     labels=labels,
        #     mean_array=throughput_means,
        #     stddev_array=throughput_stddevs,
        #     filepath=GRAPHPATH + "exp2_1_throughput_write_{}".format(write),
        #     is_latency=False
        # )
        # render_lineargraph_errorbars(
        #     labels=labels,
        #     mean_array=latency_means,
        #     stddev_array=latency_stddevs,
        #     filepath=GRAPHPATH + "exp2_1_latency_write_{}".format(write),
        #     is_latency=True
        # )

    render_lineargraph_multiple_errorbars(
        labels=labels,
        mean_array=client_throughput_means.T,
        stddev_array=client_throughput_stddev.T,
        filepath=GRAPHPATH + "exp2_1__throughput_client_read_write",
        is_latency=False,
        is_read_write=True
    )
    render_lineargraph_multiple_errorbars(
        labels=labels,
        mean_array=client_latency_means.T,
        stddev_array=client_latency_stddev.T,
        filepath=GRAPHPATH + "exp2_1__latency_client_read_write",
        is_latency=True,
        is_read_write=True
    )


if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp2_1()
