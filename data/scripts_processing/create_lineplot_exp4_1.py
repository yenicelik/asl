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

    for _vc in range(0, 6):
        vc = (2 ** _vc)

        for _mt in range(3 - 3, 7 - 3):
            mt = (2 ** (_mt + 3))

            client_all_throughputs = []  # From here on, we average over all values
            client_all_latencies = []

            mw_all_throughputs = []
            mw_all_latencies = []

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

            print("VC and MT ", (mt, vc))
            print("NEW VC and MT ", (_mt, _vc))

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

        print(client_throughput_means[:,_mt].flatten())
        print(total_virtual_clients)

        # Assertions
        len_mt = client_throughput_means[:, _mt].flatten().shape
        len_vc = client_throughput_means[:, _mt].flatten().shape
        len1 = virtual_clients

        print("All lengths are : ")
        print(len_mt)
        print(len_vc)
        print(len1)


    # THROUGHPUTS
    print("###write:client ", write, client_throughput_means)
    print("###write:middleware ", write, mw_throughput_means)
    #     ###write:client  1 [[ 2656.66666667  2626.72666667  2632.          2446.75333333]
    # [ 5024.45333333  5075.88        5013.73        3978.32333333]
    # [ 7141.74333333  7337.37666667  6490.87        7266.25      ]
    # [ 7725.51666667  8915.62333333  9007.14666667  7466.56      ]
    # [ 7488.19666667  8858.88333333  9078.78       10831.62      ]
    # [ 8120.06333333  9209.27333333 11789.20666667 12150.17      ]]
    # ###write:middleware  1 [[ 2664.70132803  2641.41654227  2659.16928326  2500.87095969]
    # [ 5044.87891294  5099.86250867  4969.28177418  4470.99490934]
    # [ 7162.72644302  7358.23351992  7238.39810733  7269.82597414]
    # [ 8278.15711411  8919.24392224  8985.27862859  8871.1915683 ]
    # [ 7451.92149022 10491.20785993 11281.83772559            nan]
    # [ 8157.63297235  9896.43692309 11775.75432867 12984.0081002 ]]

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
