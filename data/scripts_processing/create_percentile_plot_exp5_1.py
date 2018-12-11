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
    read_client_histogram_as_dataframe

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

def get_avg_25_50_75_90_99_percentiles(df):

    df = df.astype(float).sort_values('latency')  # Sort by latency

    avg = np.mean(df['latency'].astype(float).as_matrix().flatten())
    _25 = np.percentile(df['latency'].astype(float).as_matrix().flatten(), 25)
    _50 = np.percentile(df['latency'].astype(float).as_matrix().flatten(), 50)
    _75 = np.percentile(df['latency'].astype(float).as_matrix().flatten(), 75)
    _90 = np.percentile(df['latency'].astype(float).as_matrix().flatten(), 90)
    _99 = np.percentile(df['latency'].astype(float).as_matrix().flatten(), 99)

    out = np.asarray([avg, _25, _50, _75, _90, _99])

    return out

def get_client_percentiles(df):
    """
        From the client (which is stripped to the top ten minutes), get the percentiles
    :param df:
    :return:
    """
    avg = np.mean(df['time_since_begin'].astype(float))
    _25 = np.max(df[df['total_ops'].astype(float) < 25]['time_since_begin'].astype(float))
    _50 = np.max(df[df['total_ops'].astype(float) < 50]['time_since_begin'].astype(float))
    _75 = np.max(df[df['total_ops'].astype(float) < 75]['time_since_begin'].astype(float))
    _90 = np.max(df[df['total_ops'].astype(float) < 90]['time_since_begin'].astype(float))
    _99 = np.max(df[df['total_ops'].astype(float) < 99]['time_since_begin'].astype(float))

    out = np.asarray([avg, _25, _50, _75, _90, _99])

    return out

#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp5_1():
    """
        Iterates through all the parameter combinations
    :return:
    """

    create_datadir_if_not_exists(GRAPHPATH)

    multikeys = ["1", "3", "6", "9"]
    shardings = [False, True]

    _number_keys = len(multikeys)
    _number_shardings = len(shardings)
    _number_percentiles = len(["avg", "_25", "_50", "_75", "_90", "_99"])

    middleware_latencies = np.zeros((_number_shardings, _number_keys, _number_percentiles, 2, 3)) # the "two" is for the number of middlewares
    client_latencies = np.zeros((_number_shardings, _number_keys, _number_percentiles, 2, 3, 3)) # the "two" and "three" is for middlewares and clients respectively

    # Iterate through keysizes
    for jdx, sharding in enumerate(shardings):
        print("Sharding: ", sharding)

        for idx, keysize in enumerate(multikeys):
            print("Keysize is: ", keysize)

            # ONCE FOR THE MIDDLEWARE
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
                        tmp_latencies_mw = get_histogram_latency_log_dataframe_middleware(df).T
                        # print("ATT")
                        # print(jdx, idx, middleware, repetition)
                        # print(type(jdx), type(idx), type(middleware), type(repetition))
                        middleware_latencies[jdx, idx, :, middleware - 1, repetition] = get_avg_25_50_75_90_99_percentiles(tmp_latencies_mw)

                    except Exception as e:
                        # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                        print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                        print(e)
                        continue



                # ONCE FOR THE CLIENT
                for client_idx, client in enumerate(['Client1', 'Client2', 'Client3']):

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
                            _, tmp_latencies_client_get = read_client_histogram_as_dataframe(filepath=BASEPATH + client_filename)
                            # print("At")
                            # print(jdx, idx, middleware, client_idx, repetition)
                            # print(type(jdx), type(idx), type(middleware), type(client_idx), type(repetition))
                            out = get_client_percentiles(tmp_latencies_client_get)
                            # print("Indecies: ", jdx, idx, :, middleware - 1, client_idx, repetition)
                            if np.isnan(out).any():
                                print("Out is: ", out)
                                client_latencies[jdx, idx, :, middleware - 1, client_idx, repetition] = client_latencies[jdx, idx, :, middleware - 1, client_idx, 0]
                            else:
                                client_latencies[jdx, idx, :, middleware - 1, client_idx, repetition] = out

                        except Exception as e:
                            # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                            print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                            print(e)
                            assert False
                            continue

        # Normalizing the graphs to the appropriate shapes by taking means (and calculating stddevs)
        mean_client_latencies = np.mean(client_latencies, axis=3, keepdims=True)
        mean_client_latencies = np.mean(mean_client_latencies, axis=4, keepdims=True)

        mean_middleware_latencies = np.mean(middleware_latencies, axis=3, keepdims=True)

        mean_client_latencies = mean_client_latencies.squeeze()
        mean_middleware_latencies = mean_middleware_latencies.squeeze()

        print("Squeezed")
        print(mean_client_latencies.shape)
        print(mean_middleware_latencies.shape)


        client_means = np.mean(mean_client_latencies[jdx, :, :, :], axis=2)
        client_stddevs = np.std(mean_client_latencies[jdx, :, :, :], axis=2)

        mw_means = np.mean(mean_middleware_latencies[jdx, :, :, :], axis=2)
        mw_stddev = np.std(mean_middleware_latencies[jdx, :, :, :], axis=2)

        print(mw_means)
        print(client_means)

        print("Means and Stddev")
        print(client_means.shape)
        print(client_stddevs.shape)
        print(mw_means.shape)
        print(mw_stddev.shape)

        create_multiple_histogram_plot(
            keys=multikeys,
            means=client_means,
            stddevs=client_stddevs,
            filepath=GRAPHPATH + "exp5_1_client_percentile_plots_sharded_{}".format(sharding)
        )

        create_multiple_histogram_plot(
            keys=multikeys,
            means=mw_means,
            stddevs=mw_stddev,
            filepath=GRAPHPATH + "exp5_1_mw_percentile_plots_sharded_{}".format(sharding)
        )

    # print(middleware_latencies)
    # print(client_latencies)

#     mw_mean_latency = np.mean(mw_all_latencies)
#     mw_mean_throughput = np.sum(mw_all_throughputs) / 3. / 2. * 3
#     mw_stddev_latency = np.std(mw_all_latencies)
#     mw_stddev_throughput = np.std(mw_all_throughputs)
#     # Append to list
#     mw_throughput_means[idx, jdx] = mw_mean_throughput
#     mw_latency_means[idx, jdx] = mw_mean_latency
#     mw_throughput_stddev[idx, jdx] = mw_stddev_throughput
#     mw_latency_stddev[idx, jdx] = mw_stddev_latency
#
#     client_mean_latency = np.mean(client_all_latencies)
#     client_mean_throughput = np.sum(client_all_throughputs) / 3. * 3
#     client_stddev_latency = np.std(client_all_latencies)
#     client_stddev_throughput = np.std(client_all_throughputs)
#     # Append to list
#     client_throughput_means[idx, jdx] = client_mean_throughput
#     client_latency_means[idx, jdx] = client_mean_latency
#     client_throughput_stddev[idx, jdx] = client_stddev_throughput
#     client_latency_stddev[idx, jdx] = client_stddev_latency
#
# # Middleware
# render_lineargraph_errorbars(
#     labels=multikeys,
#     mean_array=mw_latency_means[:,jdx],
#     stddev_array=mw_latency_stddev[:,jdx],
#     filepath=GRAPHPATH + "exp5_1__mw_latency_sharding_{}".format(sharding),
#     is_latency=True
# )
#
# # Client
# render_lineargraph_errorbars(
#     labels=multikeys,
#     mean_array=client_latency_means[:,jdx],
#     stddev_array=client_latency_stddev[:,jdx],
#     filepath=GRAPHPATH + "exp5_1__client_latency_sharding_{}".format(sharding),
#     is_latency=True
# )
#
# # Middleware
# render_lineargraph_errorbars(
#     labels=multikeys,
#     mean_array=mw_throughput_means[:,jdx],
#     stddev_array=mw_throughput_stddev[:,jdx],
#     filepath=GRAPHPATH + "exp5_1__mw_throughput_sharding_{}".format(sharding),
#     is_latency=False
# )
#
# # Client
# render_lineargraph_errorbars(
#     labels=multikeys,
#     mean_array=client_throughput_means[:,jdx],
#     stddev_array=client_throughput_stddev[:,jdx],
#     filepath=GRAPHPATH + "exp5_1__client_throughput_sharding_{}".format(sharding),
#     is_latency=False
# )


if __name__ == "__main__":
    print("Starting to prepare the percentile-plots")


    iterate_through_experiments_exp5_1()
