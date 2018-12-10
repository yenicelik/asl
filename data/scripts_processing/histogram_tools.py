"""
    Anything that is related to reading out histogram values
"""
import json
import pandas as pd

import numpy as np

from middleware_xml_to_csv import parse_log_exp5_1
from utils import get_throughput_latency_default_memtier

import matplotlib.pyplot as plt



def create_multiple_histogram_plot(keys, means, stddevs, filepath, is_latency=False):
    """

        Create multiple histograms for the middleware
    :param keys:
    :param dataframes_array:
    :return:
    """
    assert means.shape[0] == len(keys), ("sizes dont match! ", means, keys)
    assert means.shape == stddevs.shape, ("sizes dont match! ", means, stddevs)

    percentile_keys = ["avg", "25", "50", "75", "90", "99"]

    plt.figure()

    for idx, key in enumerate(keys):

        current_mean = means[idx, :]
        current_stddev = stddevs[idx, :]

        keynames = ["Keysize: " + key + ": Percentile " + x for x in percentile_keys]

        # Create a boxplot out of these values now

        plt.bar(keynames, current_mean, label="Keysize {}".format(key), yerr=current_stddev)

    plt.ylim(ymin=0)
    plt.legend(loc='best')
    plt.xticks(rotation=70)
    plt.gca().legend()

    if filepath is None:
        plt.show()
    else:
        plt.savefig(filepath)
    plt.clf()



def plot_histogram_client(df):
    """
        Plots the histogram
    :param df:
    :return:
    """
    x = df["time_since_begin"]
    y = df["total_ops"]

    plt.bar(x, y)

    plt.show()

def get_histogram_of_latencies(raw_df):
    latencies = get_histogram_latency_log_dataframe_middleware(raw_df)

    freq, bins = np.histogram(latencies, bins=100)
    bins = bins[:-1]

    print("Frequencies and bins")
    print(len(freq))
    print(len(bins))

    print(freq)
    print(bins)

    return bins, freq


def plot_histogram_middleware(bins, frequencies):
    """
        Given one exhaustive dataset of all multiget responses,
        plot the
    :param df:
    :return:
    """

    plt.figure()

    plt.bar(bins, frequencies, width=0.1, bottom=None)

    plt.show()



def get_histogram_latency_log_dataframe_middleware(df):
    """
        Get the latency and throughput from a pandas dataframe of the log
    :param df: A dataframe with the following columns
            "timeRealOffset",
            "differenceTimeCreatedAndEnqueued",
            "differenceTimeEnqueuedAndDequeued",
            "differenceTimeDequeuedAndSentToServer",
            "differenceTimeSentToServerAndReceivedResponseFromServer",
            "differenceTimeReceivedResponseFromServerAndSentToClient",
            "timeRealDoneOffset"
    :return:
    """
    # 1. Sort by time of arrival
    df = df.sort_values("timeRealOffset")

    # 2. Take away the head and tail part
    df_length = len(df)
    df = df.tail( int(df_length * 0.9) )
    df_length = len(df)
    df = df.head( int(df_length * 0.9) )

    # 3. Calculate the mean latency
    # df['latency'] = df['timeRealDoneOffset'].astype(float) - df['timeRealOffset'].astype(float)

    df['latency'] = df['differenceTimeCreatedAndEnqueued'].astype(float) \
                    + df['differenceTimeEnqueuedAndDequeued'].astype(float) \
                    + df['differenceTimeDequeuedAndSentToServer'].astype(float) \
                    + df['differenceTimeSentToServerAndReceivedResponseFromServer'].astype(float)\
                    + df['differenceTimeReceivedResponseFromServerAndSentToClient'].astype(float)

    df['latency'] /= 1_000_000.

    ## All throughputs; I can then call "df.plt.histogram" later on
    return df['latency'].to_frame().T


def read_client_histogram_as_dataframe(filepath, percentage_details=False):
    """
    :param filepath:
    :return:
    """
    with open(filepath) as f:
        data = json.load(f)

        # Throughput
    set_histogram = data['ALL STATS']['SET']
    get_histogram = data['ALL STATS']['GET']

    set_ops = data['ALL STATS']['Sets']['Ops/sec']
    get_ops = data['ALL STATS']['Gets']['Ops/sec']

    # LET's do all SET operations first
    cumulative_value = 0.
    set_tuples = []
    for x in set_histogram:
        if x['<=msec'] < 10.0:
            set_tuples.append((
                x['<=msec'],
                (x['percent'])
            ))
            cumulative_value = x['percent']

    cumulative_value = 0.
    get_tuples = []
    for x in get_histogram:
        if x['<=msec'] < 10.0:
            get_tuples.append((
                x['<=msec'],
                (x['percent'])
            ))
            cumulative_value = x['percent']

    set_df = pd.DataFrame(set_tuples, columns=["time_since_begin", "total_ops"])
    get_df = pd.DataFrame(get_tuples, columns=["time_since_begin", "total_ops"])

    # set_df = set_df[set_df['time_since_begin'] < 10.0]
    # get_df = get_df[get_df['time_since_begin'] < 10.0]

    if percentage_details:
        return set_df, get_df, set_ops, get_ops

    return set_df, get_df

if __name__ == "__main__":
    EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/__Exp51_multikeysize_6_middleware2__rep_1_client_Client2_sharding_True_middlewarethreads_64.txt"
    set_df, get_df = read_client_histogram_as_dataframe(EXAMPLE)

    print(set_df)
    print(get_df)

    # plot_histogram(set_df)

    # EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/Middleware1_multikeygetsize_1_rep_0__sharding_False__middlewareworkerthreads_64/"
    # df = parse_log_exp5_1(EXAMPLE)
    # print(df.head(5))
    # bins, freq = get_histogram_of_latencies(df)
    # plot_histogram_middleware(bins, freq)