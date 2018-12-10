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

                    # TODO: Do it for each individual middleware!
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
            mw_mean_throughput = np.sum(mw_all_throughputs) / 3. / 2. * 3
            mw_stddev_latency = np.std(mw_all_latencies)
            mw_stddev_throughput = np.std(mw_all_throughputs)
            # Append to list
            mw_throughput_means[_vc, _mt] = mw_mean_throughput
            mw_latency_means[_vc, _mt] = mw_mean_latency
            mw_throughput_stddev[_vc, _mt] = mw_stddev_throughput
            mw_latency_stddev[_vc, _mt] = mw_stddev_latency

            client_mean_latency = np.mean(client_all_latencies)
            client_mean_throughput = np.sum(client_all_throughputs) / 3. * 3
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
    ###write:client  1
    # [[ 3590.04  3523.15  3486.23  3203.82]
    # [6292.38  7283.13  5802.84  5286.27]
    # [12822.09 12900.14 10945.55 11826.27]
    # [14858.38 17017.84 15053.06 15631.05]
    # [14290.61 14488.89 15703.54 17503.5]
    # [13262.05 15692.81 15643.02 17136.28]]
    # ###write:middleware  1 [[ 3376.28716583  3298.77096486  3270.76990351  3198.49372302]
    # [6759.7139484   6898.77960789  6431.74697095  6129.60307612]
    # [12604.6684698 12756.15664466 11672.27901281 12037.82396495]
    # [14306.66490503 16357.66170203 16064.89863541 16075.23476271]
    # [14365.88043259 17748.86651645 18828.88066674 17984.48309185]
    # [13438.92854492 18338.97409148 17882.94459437 17746.23005082]]

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
