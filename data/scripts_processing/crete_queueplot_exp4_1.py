# First, parse the file as json
import json
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_multiple_errorbars, \
    get_latency_log_dataframe, render_lineargraph_errorbars

from histogram_tools import get_histogram_latency_log_dataframe_middleware, \
    create_multiple_histogram_plot, \
    read_client_histogram_as_dataframe, get_average_queue_components

from middleware_xml_to_csv import parse_log

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp4_1_backups/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp4_1/"

def get_pattern_exp4_1_middleware(
        virtualclientthreads,
        middlewarethreads,
        repetition,
        write,
        middleware
):
    """
        Gets the filename given the above specification for the middleware threads
    :return:
    """
    out = "Middleware{}_threads_{}_vc_{}_rep_{}__writes_{}/"
    out = out.format(middleware, middlewarethreads, virtualclientthreads, repetition, write)
    return out




def create_queue_barplots():

    create_datadir_if_not_exists(GRAPHPATH)

    middleware_threads = [(2 ** x) for x in range(3, 7)]
    virtual_clients = [(2 ** x) for x in range(0, 6)]


    total_virtual_clients = len([(2 ** x) for x in range(0, 6)])
    total_middleware_threads = len([(2 ** x) for x in range(3, 7)])

    # The following are the different values we're going to plot:
    #
    time_labels = ['Time to Enqueue', 'Time in Queue', 'Time Queue to Server', 'Time at Server', 'Time Server to Client']

    print("Time labels have shape: ", len(time_labels))

    for write in [1]:

        for _vc in range(0, 6):
            vc = (2 ** _vc)

            middleware_latencies = np.zeros((total_middleware_threads, len(time_labels), 2, 3))  # 3 repetitions, 2 middlewares

            for _mt, mt in enumerate(middleware_threads):
                mt = (2 ** (_mt + 3))

                # ONCE FOR THE MIDDLEWARE
                for repetition in range(3):

                    for middleware in [1, 2]:
                        # Get throughput and latency from the file
                        middleware_filename = get_pattern_exp4_1_middleware(
                            virtualclientthreads=vc,
                            middlewarethreads=mt,
                            repetition=repetition,
                            write=write,
                            middleware=middleware
                        )

                        try:
                            df = parse_log(BASEPATH + middleware_filename)
                            middleware_latencies[_mt, :, middleware - 1, repetition] = get_average_queue_components(df)

                        except Exception as e:
                            # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                            print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                            print(e)
                            continue

            # Normalizing the graphs to the appropriate shapes by taking means (and calculating stddevs)
            mean_middleware_latencies = np.mean(middleware_latencies, axis=2, keepdims=True)
            stddev_middleware_latencies = np.std(mean_middleware_latencies, axis=3, keepdims=True)
            mean_middleware_latencies = np.mean(mean_middleware_latencies, axis=3, keepdims=True)

            mw_means = mean_middleware_latencies.squeeze().T
            mw_stddev = stddev_middleware_latencies.squeeze().T

            print("Means and Stddev")
            print(mw_means.shape)
            print(mw_stddev.shape)
            print(len(time_labels))
            print(time_labels)

            print(mw_means)

            create_multiple_histogram_plot(
                keys=middleware_threads,
                means=mw_means.T,
                stddevs=mw_stddev.T,
                filepath=GRAPHPATH + "exp4_1_mw_percentile_plots_writes_{}__vc_{}".format(write, vc),
                is_queue=True
            )

if __name__ == "__main__":
    create_queue_barplots()

    # EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/__Exp51_multikeysize_6_middleware2__rep_1_client_Client2_sharding_True_middlewarethreads_64.txt"
    # set_df, get_df = read_client_histogram_as_dataframe(EXAMPLE)
    #
    # print(set_df)
    # print(get_df)
    #
    # # plot_histogram(set_df)
    #
    # EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/Middleware1_multikeygetsize_1_rep_0__sharding_False__middlewareworkerthreads_64/"
    # df = parse_log_exp5_1(EXAMPLE)
    # print(df.head(5))
    # bins, freq = get_histogram_of_latencies(df)
    # plot_histogram_middleware(bins, freq)