"""
    Anything that is related to reading out histogram values
"""
import json
import pandas as pd

import numpy as np

from middleware_xml_to_csv import parse_log_exp5_1
from utils import get_throughput_latency_default_memtier

import matplotlib.pyplot as plt



def create_multiple_histogram_plot(keys, means, stddevs, filepath, is_latency=False, is_queue=False):
    """

        Create multiple histograms for the middleware
    :param keys:
    :param dataframes_array:
    :return:
    """
    assert means.shape[0] == len(keys), ("sizes dont match! ", means, keys)
    assert means.shape == stddevs.shape, ("sizes dont match! ", means, stddevs)


    plt.figure()

    for idx, key in enumerate(keys):

        current_mean = means[idx, :]
        current_stddev = stddevs[idx, :]

        if is_queue:
            time_labels = ['Time to Enqueue', 'Time in Queue', 'Time Queue to Server', 'Time at Server','Time Server to Client']
            keynames = [(str(key) + " : " + str(x)) for x in time_labels]
            plt.bar(keynames, current_mean, label="Middlewarethreads {}".format(key), yerr=current_stddev, capsize=5)
        else:
            percentile_keys = ["avg", "25", "50", "75", "90", "99"]
            keynames = [(str(key) + " : " + str(x)) for x in percentile_keys]
            plt.bar(
                keynames,
                current_mean, label="Keysize {}".format(key), yerr=current_stddev, capsize=5)

        print("Shapes are: ", len(keynames), current_mean.shape, current_stddev.shape)

        # print("sizes are: ", current_stddev.shape, current_mean.shape, len(keynames))

        # Create a boxplot out of these values now



    if is_queue:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Average number of requests in queue')
    else:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Response Time in ms')


    plt.ylim(ymin=0)
    plt.legend(loc='best')
    plt.xticks(rotation=90)
    plt.gca().legend()

    if filepath is None:
        plt.show()
    else:
        plt.savefig(filepath)
    plt.clf()



def plot_histogram_client(df, savefile=None):
    """
        Plots the histogram
    :param df:
    :return:
    """
    x = df["time_since_begin"]
    y = df["total_ops"]

    plt.bar(x, y)

    if savefile is None:
        plt.show()
    else:
        plt.savefig(savefile)
    plt.clf()

def get_histogram_of_latencies(raw_df):
    latencies = get_histogram_latency_log_dataframe_middleware(raw_df)

    # Remove all latencies bigger than 12 as these are outliers
    # latencies[latencies > 15.] = 0.

    latencies = latencies / 1_000_000.

    freq, bins = np.histogram(latencies, bins=10000)
    bins = bins[:-1]
    # bins = bins / 1_000_000.
    # freq = np.log(freq)

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

    plt.bar(bins, frequencies, bottom=None, width=1)
    # plt.xticks(bins / 10.)
    plt.xlim(0, 15)

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

    ## All throughputs; I can then call "df.plt.histogram" later on
    return df['latency'].to_frame().T


def read_client_histogram_as_dataframe(filepath, percentage_details=False, cumulative=False):
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
                (x['percent'] - cumulative_value)
            ))
            cumulative_value = x['percent']
            if cumulative:
                cumulative_value = 0.


    cumulative_value = 0.
    get_tuples = []
    for x in get_histogram:
        if x['<=msec'] < 10.0:
            get_tuples.append((
                x['<=msec'],
                (x['percent'] - cumulative_value)
            ))
            cumulative_value = x['percent']
            if cumulative:
                cumulative_value = 0.


    set_df = pd.DataFrame(set_tuples, columns=["time_since_begin", "total_ops"])
    get_df = pd.DataFrame(get_tuples, columns=["time_since_begin", "total_ops"])

    # set_df = set_df[set_df['time_since_begin'] < 10.0]
    # get_df = get_df[get_df['time_since_begin'] < 10.0]

    if percentage_details:
        return set_df, get_df, set_ops, get_ops

    return set_df, get_df


def get_average_queue_components(df):
    """
        Given a dataframe, extracts the average of the following values:

            "timeRealOffset",
            "differenceTimeCreatedAndEnqueued",
            "differenceTimeEnqueuedAndDequeued",
            "differenceTimeDequeuedAndSentToServer",
            "differenceTimeSentToServerAndReceivedResponseFromServer",
            "differenceTimeReceivedResponseFromServerAndSentToClient",
            "timeRealDoneOffset"

        || 1541677809689, 1872, 490636, 61797, 850187, 31835, 1541677809691, 534, 0.11864030215507665

        corresponding to


    :return:
    """

    # The following are all averages
    time_to_enqueue = df["differenceTimeCreatedAndEnqueued"].astype(float).mean() / 1_000_000.
    time_in_queue = df["differenceTimeEnqueuedAndDequeued"].astype(float).mean() / 1_000_000.
    time_queue_to_server = df["differenceTimeDequeuedAndSentToServer"].astype(float).mean() / 1_000_000.
    time_at_server = df["differenceTimeSentToServerAndReceivedResponseFromServer"].astype(float).mean() / 1_000_000.
    time_from_server_to_client = df["differenceTimeReceivedResponseFromServerAndSentToClient"].astype(float).mean() / 1_000_000.

    out = np.asarray(
        [time_to_enqueue, time_in_queue, time_queue_to_server, time_at_server, time_from_server_to_client])

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

    avg = np.mean(df['time_since_begin'].astype(float).values)
    _25 = np.max(df[df['total_ops'].astype(float) < 25]['time_since_begin'].astype(float).values)
    _50 = np.max(df[df['total_ops'].astype(float) < 50]['time_since_begin'].astype(float).values)
    _75 = np.max(df[df['total_ops'].astype(float) < 75]['time_since_begin'].astype(float).values)
    _90 = np.max(df[df['total_ops'].astype(float) < 90]['time_since_begin'].astype(float).values)
    _99 = np.max(df[df['total_ops'].astype(float) < 99]['time_since_begin'].astype(float).values)

    out = np.asarray([avg, _25, _50, _75, _90, _99])

    return out


if __name__ == "__main__":
    EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/__Exp51_multikeysize_6_middleware2__rep_1_client_Client2_sharding_True_middlewarethreads_64.txt"
    set_df, get_df = read_client_histogram_as_dataframe(EXAMPLE)
    plot_histogram_client(get_df, savefile="/Users/david/asl-fall18-project/report/img/exp5_1/histogram_client_sharded")

    EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/__Exp51_multikeysize_6_middleware2__rep_1_client_Client2_sharding_False_middlewarethreads_64.txt"
    set_df, get_df = read_client_histogram_as_dataframe(EXAMPLE)
    plot_histogram_client(get_df, savefile="/Users/david/asl-fall18-project/report/img/exp5_1/histogram_client_nonsharded")



    # EXAMPLE = "/Users/david/asl-fall18-project/data/raw/exp5_1_backups/Middleware1_multikeygetsize_1_rep_0__sharding_False__middlewareworkerthreads_64/"
    # df = parse_log_exp5_1(EXAMPLE)
    # print(df.head(5))
    # bins, freq = get_histogram_of_latencies(df)
    # plot_histogram_middleware(bins, freq)
