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

    for number_of_middlewares in [1, 2]:

        for number_of_servers in [1, 3]:

            for number_of_middleware_workerthreads in [8, 32]:

                client_all_throughputs = []  # From here on, we average over all values
                client_all_latencies = []

                for repetition in range(3):

                    mw_all_throughputs = []
                    mw_all_latencies = []

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

                    configuration = (number_of_middlewares, number_of_servers, number_of_middleware_workerthreads)

                    final_mw_throughputs.append(
                        (configuration, (repetition, np.sum(mw_all_throughputs)))
                    )

                    final_mw_latencies.append(
                        (configuration, (repetition, np.mean(mw_all_latencies)))
                    )

    # Iterating through individual lists for easy copy pasta
    # print("CLIENT THROUGHPUT")
    # for x in final_client_throughputs:
    #     print(x)

    print("MIDDLEWARE THROUGHPUT")
    for idx, x in enumerate(final_mw_throughputs):
        if idx % 3 == 0:
            print()
        print(x)

    # print("CLIENT LATENCY")
    # for x in final_client_latencies:
    #     print(x)

    print("MIDDLEWARE LATENCY")
    for idx, x in enumerate(final_mw_latencies):
        if idx % 3 == 0:
            print()
        print(x)


if __name__ == "__main__":
    print("Starting to prepare the values for the 2k experiments")

    iterate_through_experiments_exp6_1()





    # READ ONLY
    # MIDDLEWARE THROUGHPUT
    #
    # ((1, 1, 8), (0, 3030.368381665926))
    # ((1, 1, 8), (1, 3008.7491991878414))
    # ((1, 1, 8), (2, 3009.6365487342573))
    #
    # ((1, 1, 32), (0, 2959.130269898489))
    # ((1, 1, 32), (1, 2912.6519434872116))
    # ((1, 1, 32), (2, 2923.5859321078183))
    #
    # ((1, 3, 8), (0, 7815.086222399755))
    # ((1, 3, 8), (1, 7853.320197405555))
    # ((1, 3, 8), (2, 7826.1104185489585))
    #
    # ((1, 3, 32), (0, 8190.482517122101))
    # ((1, 3, 32), (1, 8309.26529348873))
    # ((1, 3, 32), (2, 8338.135880547663))
    #
    # ((2, 1, 8), (0, 2984.9511002934228))
    # ((2, 1, 8), (1, 2983.651215337728))
    # ((2, 1, 8), (2, 2982.1464360100254))
    #
    # ((2, 1, 32), (0, 2959.2115816913747))
    # ((2, 1, 32), (1, 2960.670408012511))
    # ((2, 1, 32), (2, 2979.504992616068))
    #
    # ((2, 3, 8), (0, 8150.738611905544))
    # ((2, 3, 8), (1, 8435.898960564722))
    # ((2, 3, 8), (2, 8351.97424950272))
    #
    # ((2, 3, 32), (0, 8302.667297474149))
    # ((2, 3, 32), (1, 8169.003130315987))
    # ((2, 3, 32), (2, 8267.648051605685))
    # MIDDLEWARE LATENCY
    #
    # ((1, 1, 8), (0, 59.7))
    # ((1, 1, 8), (1, 59.852112676056336))
    # ((1, 1, 8), (2, 59.34507042253521))
    #
    # ((1, 1, 32), (0, 57.202108963093146))
    # ((1, 1, 32), (1, 57.85764499121265))
    # ((1, 1, 32), (2, 59.01405975395431))
    #
    # ((1, 3, 8), (0, 23.748148148148147))
    # ((1, 3, 8), (1, 23.918518518518518))
    # ((1, 3, 8), (2, 23.810606060606062))
    #
    # ((1, 3, 32), (0, 19.933701657458563))
    # ((1, 3, 32), (1, 19.447513812154696))
    # ((1, 3, 32), (2, 20.03963963963964))
    #
    # ((2, 1, 8), (0, 61.014084507042256))
    # ((2, 1, 8), (1, 61.20070422535211))
    # ((2, 1, 8), (2, 61.21126760563381))
    #
    # ((2, 1, 32), (0, 57.253075571177504))
    # ((2, 1, 32), (1, 59.26801405975395))
    # ((2, 1, 32), (2, 58.66191499056174))
    #
    # ((2, 3, 8), (0, 20.407407407407405))
    # ((2, 3, 8), (1, 20.749531176746366))
    # ((2, 3, 8), (2, 20.199564270152507))
    #
    # ((2, 3, 32), (0, 19.816511071294606))
    # ((2, 3, 32), (1, 20.948673354813515))
    # ((2, 3, 32), (2, 19.927943760984185))
