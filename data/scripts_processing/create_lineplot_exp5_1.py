# First, parse the file as json
import json
import os

import numpy as np

import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_multiple_errorbars, \
    get_latency_log_dataframe, render_lineargraph_errorbars

from middleware_xml_to_csv import parse_log

# Do it for experiment 1 for now

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp5_1/"

def get_pattern_exp5_1_middleware(
        middleware,
        keysize,
        repetition,
        sharding
    ):
    """
        Gets the filename given the above specification for the middleware threads
    :return:
    """
    # out = "Middleware{}_threads_{}_vc_{}_rep_{}__writes_{}/"
    out = "Middleware{}_multikeygetsize_{}_rep_{}__sharding_{}__middlewareworkerthreads_64/"
    if middleware == 2:
        out = "Middleware{}_multikeygetsize_{}_rep_{}__sharding_{}_middlewareworkerthreads_64/"
    out = out.format(middleware, keysize, repetition, sharding)
    return out


def get_pattern_exp5_1_client(
        keysize,
        middleware,
        repetition,
        client,
        sharding
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
    out = "__Exp51_multikeysize_{}_middleware{}__rep_{}_client_{}_sharding_{}_middlewarethreads_64.txt"
    if middleware == 1:
        out = "_Exp51_multikeysize_{}_middleware{}__rep_{}_client_{}_sharding_{}_middlewarethreads_64.txt"
    out = out.format(keysize, middleware, repetition, client, sharding)
    return out

#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp4_1():
    """
        Iterates through all the parameter combinations
    :return:
    """

    create_datadir_if_not_exists(GRAPHPATH)
    write = 1 # This experiment consists of writes-only!

    multikeys = ["1", "3", "6", "9"]
    shardings = [False, True]

    _number_keys = len(multikeys)
    _number_shardings = len(shardings)

    mw_throughput_means = np.zeros((_number_keys, _number_shardings))
    mw_throughput_stddev = np.zeros((_number_keys, _number_shardings))
    mw_latency_means = np.zeros((_number_keys, _number_shardings))
    mw_latency_stddev = np.zeros((_number_keys, _number_shardings))

    client_throughput_means = np.zeros((_number_keys, _number_shardings))
    client_latency_means = np.zeros((_number_keys, _number_shardings))
    client_throughput_stddev = np.zeros((_number_keys, _number_shardings))
    client_latency_stddev = np.zeros((_number_keys, _number_shardings))

    # Iterate through keysizes
    for jdx, sharding in enumerate(shardings):
        print("Sharding: ", sharding)

        for idx, keysize in enumerate(multikeys):
            print("Keysize is: ", keysize)

            client_all_throughputs = []  # From here on, we average over all values
            client_all_latencies = []

            mw_all_throughputs = []
            mw_all_latencies = []

            for repetition in range(3):

                for middleware in [1, 2]:
                    # Get throughput and latency from the file
                    middleware_filename = get_pattern_exp5_1_middleware(
                        middleware=middleware,
                        keysize=keysize,
                        repetition=repetition,
                        sharding=sharding
                    )

                    try:
                        df = parse_log(BASEPATH + middleware_filename)
                        mw_throughput, mw_latency = get_latency_log_dataframe(df)
                        mw_throughput *= 64 * 1000 # bcs this gives us throughput per millisecond

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

                        # TODO: Do it for each individual middleware!
                        # Trying to open and read the file!
                        client_filename = get_pattern_exp5_1_client(
                            keysize=keysize,
                            middleware=middleware,
                            repetition=repetition,
                            client=client,
                            sharding=sharding
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

            mw_mean_latency = np.mean(mw_all_latencies)
            mw_mean_throughput = np.sum(mw_all_throughputs) / 3.
            mw_stddev_latency = np.std(mw_all_latencies)
            mw_stddev_throughput = np.std(mw_all_throughputs)
            # Append to list
            mw_throughput_means[idx, jdx] = mw_mean_throughput
            mw_latency_means[idx, jdx] = mw_mean_latency
            mw_throughput_stddev[idx, jdx] = mw_stddev_throughput
            mw_latency_stddev[idx, jdx] = mw_stddev_latency

            client_mean_latency = np.mean(client_all_latencies)
            client_mean_throughput = np.sum(client_all_throughputs) / 3.
            client_stddev_latency = np.std(client_all_latencies)
            client_stddev_throughput = np.std(client_all_throughputs)
            # Append to list
            client_throughput_means[idx, jdx] = client_mean_throughput
            client_latency_means[idx, jdx] = client_mean_latency
            client_throughput_stddev[idx, jdx] = client_stddev_throughput
            client_latency_stddev[idx, jdx] = client_stddev_latency

        # Middleware
        render_lineargraph_errorbars(
            labels=multikeys,
            mean_array=mw_latency_means[:,jdx],
            stddev_array=mw_latency_stddev[:,jdx],
            filepath=GRAPHPATH + "exp5_1__mw_latency_sharding_{}".format(sharding),
            is_latency=True
        )

        # Client
        render_lineargraph_errorbars(
            labels=multikeys,
            mean_array=client_latency_means[:,jdx],
            stddev_array=client_latency_stddev[:,jdx],
            filepath=GRAPHPATH + "exp5_1__client_latency_sharding_{}".format(sharding),
            is_latency=True
        )

        # Middleware
        render_lineargraph_errorbars(
            labels=multikeys,
            mean_array=mw_throughput_means[:,jdx],
            stddev_array=mw_throughput_stddev[:,jdx],
            filepath=GRAPHPATH + "exp5_1__mw_throughput_sharding_{}".format(sharding),
            is_latency=False
        )

        # Client
        render_lineargraph_errorbars(
            labels=multikeys,
            mean_array=client_throughput_means[:,jdx],
            stddev_array=client_throughput_stddev[:,jdx],
            filepath=GRAPHPATH + "exp5_1__client_throughput_sharding_{}".format(sharding),
            is_latency=False
        )


if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp4_1()
