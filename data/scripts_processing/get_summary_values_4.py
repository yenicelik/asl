"""
    For the 4.1 summary, gets the following values

    Throughput, Response time, Average time in queue, Average length of queue, Average time waiting for memcached

    For
    Writes

    Per
    Middleware, Client, Middleware (Derived from response time)

    For
    One Middleware, Two Middlewares
"""


# First, parse the file as json
import json
import os

import numpy as np

import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_multiple_errorbars, get_latency_log_dataframe

from middleware_xml_to_csv import parse_log

# Do it for experiment 1 for now

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


def get_pattern_exp4_1_client(virtual_client_threads, middleware, middlewareworkerthreads, repetition, client, write):
    """
        Get's the filename given the above specifications.
        This is for easier handling of the data
    :param virtual_client_threads:
    :param repetition:
    :param client:
    :param write:
    :return:
    """
    # out = "virtualclients_{}_middleware{}_middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}.txt"
    # out = "virtualclients_1_middleware1_middlewareworkerthreads_8__rep_0_client_Client1_writes_0"
    out = "Exp41_virtualclients_{}_middleware{}_middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}.txt"
    out = out.format(virtual_client_threads, middleware, middlewareworkerthreads, repetition, client, write)
    return out

#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp4_1():
    """
        Iterates through all the parameter combinations
    :return:
    """

    create_datadir_if_not_exists(GRAPHPATH)
    write = 1 # This experiment consists of writes-only!

    middleware_threads = [(2 ** x) for x in range(3, 7)]
    virtual_clients = [(2 ** x) for x in range(0, 6)]


    total_virtual_clients = len([(2 ** x) for x in range(0, 6)])
    total_middleware_threads = len([(2 ** x) for x in range(3, 7)])

    mw_throughput_means = np.zeros((total_virtual_clients, total_middleware_threads))
    mw_throughput_stddev = np.zeros((total_virtual_clients, total_middleware_threads))
    mw_latency_means = np.zeros((total_virtual_clients, total_middleware_threads))
    mw_latency_stddev = np.zeros((total_virtual_clients, total_middleware_threads))

    client_throughput_means = np.zeros((total_virtual_clients, total_middleware_threads))
    client_latency_means = np.zeros((total_virtual_clients, total_middleware_threads))
    client_throughput_stddev = np.zeros((total_virtual_clients, total_middleware_threads))
    client_latency_stddev = np.zeros((total_virtual_clients, total_middleware_threads))


    for _mt in range(3 - 3, 7 - 3):
        mt = (2 ** (_mt + 3))

        queuetimes = []
        queuesizes = []
        waittimes = []

        for _vc in range(0, 6):
            vc = (2 ** _vc)


            client_all_throughputs = []  # From here on, we average over all values
            client_all_latencies = []

            mw_all_throughputs = []
            mw_all_latencies = []

            tmp_queuetimes = []
            tmp_queuesizes = []
            tmp_waittimes = []

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

                        queuetime = df['differenceTimeEnqueuedAndDequeued'].astype(float).mean() / 1000.
                        tmp_queuetimes.append(queuetime)
                        queuesize = df['queueSize'].astype(float).mean()
                        tmp_queuesizes.append(queuesize)
                        waittime = df['differenceTimeSentToServerAndReceivedResponseFromServer'].astype(float).mean() / 1000.
                        tmp_waittimes.append(waittime)

                        mw_throughput, mw_latency = get_latency_log_dataframe(df)
                        mw_throughput *= mt * 1000 # bcs this gives us throughput per millisecond

                        # print("THROUGHPUT AND LATENCY ARE: ")
                        # print(mw_throughput)
                        # print(mw_latency)

                        mw_all_throughputs.append(mw_throughput)
                        mw_all_latencies.append(mw_latency)

                    except Exception as e:
                        # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                        print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                        print(e)
                        continue

                for client in ['Client1', 'Client2', 'Client3']:

                    for middleware in [1, 2]:

                        # Trying to open and read the file!
                        client_filename = get_pattern_exp4_1_client(
                            virtual_client_threads=vc,
                            middleware=middleware,
                            middlewareworkerthreads=mt,
                            repetition=repetition,
                            client=client,
                            write=write
                        )

                        try:
                            client_throughput, client_latency = get_throughput_latency_default_memtier(filepath=BASEPATH + client_filename)
                            client_all_throughputs.append(client_throughput)
                            client_all_latencies.append(client_latency)

                        except Exception as e:
                            # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                            print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                            print(e)
                            continue

            queuetimes.append(np.mean(tmp_queuetimes))
            queuesizes.append(np.mean(tmp_queuesizes))
            waittimes.append(np.mean(tmp_waittimes))

            # print("VC and MT ", (mt, vc))
            # print("NEW VC and MT ", (_mt, _vc))

            mw_mean_latency = np.mean(mw_all_latencies)
            mw_mean_throughput = np.sum(mw_all_throughputs) / 3.
            mw_stddev_latency = np.std(mw_all_latencies)
            mw_stddev_throughput = np.std(mw_all_throughputs)
            # Append to list
            mw_throughput_means[_vc, _mt] = mw_mean_throughput
            mw_latency_means[_vc, _mt] = mw_mean_latency
            mw_throughput_stddev[_vc, _mt] = mw_stddev_throughput
            mw_latency_stddev[_vc, _mt] = mw_stddev_latency

            client_mean_latency = np.mean(client_all_latencies)
            client_mean_throughput = np.sum(client_all_throughputs) / 3.
            client_stddev_latency = np.std(client_all_latencies)
            client_stddev_throughput = np.std(client_all_throughputs)
            # Append to list
            client_throughput_means[_vc, _mt] = client_mean_throughput
            client_latency_means[_vc, _mt] = client_mean_latency
            client_throughput_stddev[_vc, _mt] = client_stddev_throughput
            client_latency_stddev[_vc, _mt] = client_stddev_latency


        print("MW IS: ", mt)
        argmax_vc = np.argmax(client_throughput_means[:,_mt].flatten())
        print("Argmax vc is: ", 2**argmax_vc)
        print("Max is: ", )
        print("queuesize: ", queuesizes[argmax_vc])
        print("waittimes: ", waittimes[argmax_vc])
        print("queuetimes: ", queuetimes[argmax_vc])
        print("Client troughput mean: ", client_throughput_means[argmax_vc,_mt].flatten())
        print("MW troughput mean: ", mw_throughput_means[argmax_vc,_mt].flatten())
        print("MW derived throughput time: ", 2 * 3 * (2**argmax_vc) / mw_latency_means[argmax_vc,_mt].flatten() * 1000)

    # THROUGHPUTS
    # print("###write:client ", write, client_throughput_means)
    # print("###write:middleware ", write, mw_throughput_means)
    ###write:client  1
    # [[ 1815.45333333  2321.54        2285.64        2127.40333333]
    # [ 4608.49        4581.64        4576.45333333  4406.16333333]
    # [ 6971.06666667  6543.16333333  7374.53333333  6144.32333333]
    # [ 8698.22666667  8063.80666667  9086.58        9738.00333333]
    # [ 8995.92       10068.55333333 11404.78       10261.27      ]
    # [ 7064.09333333 10026.83333333 12586.12       12858.95333333]]
    # ###write:middleware  1
    # [[ 1947.229088    2317.76063679  2322.53675249  2207.33621436]
    # [ 4591.30620045  4605.04654336  4582.13005631  4509.73165549]
    # [ 8020.03037995  6967.31991722  7475.40874085  7804.08509258]
    # [ 8645.69236829 10314.9812626   9302.41430409  9688.76860568]
    # [ 8833.92859926 10153.21361682 12126.18091513 10299.9702301 ]
    # [ 7465.56068924 10133.52159323 12503.89763076 13706.73554513]]


if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp4_1()


