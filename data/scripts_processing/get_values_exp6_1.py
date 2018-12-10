# First, parse the file as json
import json
import os

import numpy as np

import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_multiple_errorbars, get_latency_log_dataframe

from middleware_xml_to_csv import parse_log

# Do it for experiment 1 for now

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp6_1_backups/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp6_1/"


def get_pattern_exp6_1_middleware(
        middlewarethreads,
        number_of_middlewares,
        servers,
        repetition,
        write,
        middleware
):
    """
        Gets the filename given the above specification for the middleware threads
    :return:
    """
    # out = "Middleware{}_threads_{}_vc_{}_rep_{}__writes_{}/"
    out = "Middleware{}_threads_{}_middlewares_{}_servers_{}_rep_{}__writes_{}/"
    out = out.format(middleware, middlewarethreads, number_of_middlewares, servers, repetition, write)
    return out


def get_pattern_exp6_1_client(
        middleware,
        servers,
        number_of_middlewares,
        middlewareworkerthreads,
        repetition,
        client,
        write
):
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
    # out = "Exp41_virtualclients_{}_middleware{}_middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}.txt"
    # out = out.format(virtual_client_threads, middleware, middlewareworkerthreads, repetition, client, write)
    out = "_Exp61middleware{}_number_of_servers__{}_middlewares_{}__middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}_MW{}.txt"
    out = "_Exp61middleware{}_number_of_servers__{}_middlewares_{}__middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}_MW{}.txt"
    # out = "_Exp61middleware2_number_of_servers__1_middlewares_2__middlewareworkerthreads_32__rep_1_client_Client1_writes_0_MW1.txt"
    out = '_Exp61middleware{}_number_of_servers__{}_middlewares_{}__middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}_MW{}.txt'
    out = out.format(number_of_middlewares, servers, number_of_middlewares, middlewareworkerthreads, repetition, client, write,
                     middleware)
    return out


#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp6_1():
    """
        Iterates through all the parameter combinations
    :return:
    """

    write = 1  # This experiment consists of writes-only!

    final_client_throughputs = []
    final_mw_throughputs = []

    final_client_latencies = []
    final_mw_latencies = []

    print("WRITES ARE:::: ", write)

    for number_of_servers in [1, 3]:

        for number_of_middlewares in [1, 2]:

            for number_of_middleware_workerthreads in [8, 32]:

                client_all_throughputs = []  # From here on, we average over all values
                client_all_latencies = []

                mw_all_throughputs = []
                mw_all_latencies = []

                for repetition in range(3):

                    _array_middlewares = [1, 2] if number_of_middlewares == 2 else [1]
                    for middleware in _array_middlewares:
                        # Get throughput and latency from the file
                        middleware_filename = get_pattern_exp6_1_middleware(
                            middlewarethreads=number_of_middleware_workerthreads,
                            number_of_middlewares=number_of_middlewares,
                            servers=number_of_servers,
                            repetition=repetition,
                            write=write,
                            middleware=middleware
                        )

                        try:
                            df = parse_log(BASEPATH + middleware_filename)
                            mw_throughput, mw_latency = get_latency_log_dataframe(df)
                            mw_throughput *= number_of_middleware_workerthreads * 1000  # bcs this gives us throughput per millisecond

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
                        for middleware in _array_middlewares:

                            client_filename = get_pattern_exp6_1_client(
                                middleware=middleware,
                                servers=number_of_servers,
                                number_of_middlewares=number_of_middlewares,
                                middlewareworkerthreads=number_of_middleware_workerthreads,
                                repetition=repetition,
                                client=client,
                                write=write
                            )

                            try:
                                client_throughput, client_latency = get_throughput_latency_default_memtier(
                                    filepath=BASEPATH + client_filename)
                                client_all_throughputs.append(client_throughput)
                                client_all_latencies.append(client_latency)

                            except Exception as e:
                                # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                                print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                                print(e)
                                continue

                mw_mean_latency = np.mean(mw_all_latencies)
                mw_mean_throughput = np.sum(mw_all_throughputs) / 3. / 2. * 3
                mw_stddev_latency = np.std(mw_all_latencies)
                mw_stddev_throughput = np.std(mw_all_throughputs)

                client_mean_latency = np.mean(client_all_latencies)
                client_mean_throughput = np.sum(client_all_throughputs) / 3. * 3
                client_stddev_latency = np.std(client_all_latencies)
                client_stddev_throughput = np.std(client_all_throughputs)

                ## Appending middleware and client values to the tuple list
                # final_client_throughputs = []
                # final_mw_throughputs = []
                #
                # final_client_latencies = []
                # final_mw_latencies = []

                configuration = (number_of_servers, number_of_middlewares, number_of_middleware_workerthreads)

                final_client_throughputs.append(
                    (configuration, (client_mean_throughput, client_stddev_throughput))
                )
                final_mw_throughputs.append(
                    (configuration, (mw_mean_throughput, mw_stddev_throughput))
                )

                final_client_latencies.append(
                    (configuration, (client_mean_latency, client_stddev_latency))
                )
                final_mw_latencies.append(
                    (configuration, (mw_mean_latency, mw_stddev_latency))
                )

    # Iterating through individual lists for easy copy pasta
    print("CLIENT THROUGHPUT")
    for x in final_client_throughputs:
        print(x)

    print("MIDDLEWARE THROUGHPUT")
    for x in final_mw_throughputs:
        print(x)

    print("CLIENT LATENCY")
    for x in final_client_latencies:
        print(x)

    print("MIDDLEWARE LATENCY")
    for x in final_mw_latencies:
        print(x)


if __name__ == "__main__":
    print("Starting to prepare the values for the 2k experiments")

    iterate_through_experiments_exp6_1()
