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

    queuetime_means = np.zeros((total_virtual_clients, total_middleware_threads))
    queuelength_means = np.zeros((total_virtual_clients, total_middleware_threads))
    waittime_means = np.zeros((total_virtual_clients, total_middleware_threads))

    for _mt in range(3 - 3, 7 - 3):
        mt = (2 ** (_mt + 3))

        for _vc in range(0, 6):
            vc = (2 ** _vc)

            client_all_throughputs = []  # From here on, we average over all values
            client_all_latencies = []

            mw_all_throughputs = []
            mw_all_latencies = []

            queuetimes = []
            queuelengths = []
            waittimes = []

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

                        # Append queuetimes, queuelength and waittime
                        queuetimes.append(df['differenceTimeEnqueuedAndDequeued'].astype(float).mean())
                        queuelengths.append(df['queueSize'].astype(float).mean())
                        waittimes.append(df['differenceTimeSentToServerAndReceivedResponseFromServer'].astype(float).mean())

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

            # Queuetimes etc.
            queuetime_means[_vc, _mt] = np.mean(queuetimes)
            queuelength_means[_vc, _mt] = np.mean(queuelengths)
            waittime_means[_vc, _mt] = np.mean(waittimes)

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


        # Assertions
        len_mt = client_throughput_means[:, _mt].flatten().shape
        len_vc = client_throughput_means[:, _mt].flatten().shape
        len1 = virtual_clients



    argmax_vc = np.argmax(mw_throughput_means, axis=0)
    print("MW throughputs are: ", mw_throughput_means)
    print("VC maximizing is: ", argmax_vc)

    for idx, mt in enumerate([8, 16, 32, 64]):

        max_vc = argmax_vc[idx]
        print()
        print()
        print()

        print("MT IS: ", mt)
        # Section 7 data
        # print("###write:client ", client_throughput_means[max_vc, idx])
        # print("###write:middleware ", mw_throughput_means[max_vc, idx])
        print("###write:queuesizes ", queuelength_means[max_vc, idx])
        print("###write:latency ", mw_latency_means[max_vc, idx])
        print("###write:waittime_means ", waittime_means[max_vc, idx] / 1000000.)

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

    # Taken out for experiment 7!
    # Plot the client values
    render_lineargraph_multiple_errorbars(
        labels=virtual_clients,
        mean_array=client_throughput_means.T,
        stddev_array=client_throughput_stddev.T,
        filepath=GRAPHPATH + "exp4_1__vc_{}__throughput_client_write_{}".format(mt, write),
        is_latency=False
    )
    render_lineargraph_multiple_errorbars(
        labels=virtual_clients,
        mean_array=client_latency_means.T,
        stddev_array=client_latency_stddev.T,
        filepath=GRAPHPATH + "exp4_1__vc_{}__latency_client_write_{}".format(mt, write),
        is_latency=True
    )

    # print(np.max(mw_throughput_means, axis=0))
    # print(np.max(mw_throughput_means, axis=1))

    # Plot the middleware values
    render_lineargraph_multiple_errorbars(
        labels=virtual_clients,
        mean_array=mw_throughput_means.T,
        stddev_array=mw_throughput_stddev.T,
        filepath=GRAPHPATH + "exp4_1__vc_{}__throughput_middleware_write_{}".format(mt, write),
        is_latency=False
    )
    render_lineargraph_multiple_errorbars(
        labels=virtual_clients,
        mean_array=mw_latency_means.T,
        stddev_array=mw_latency_stddev.T,
        filepath=GRAPHPATH + "exp4_1__vc_{}__latency_middleware_write_{}".format(mt, write),
        is_latency = True
    )



if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp4_1()
