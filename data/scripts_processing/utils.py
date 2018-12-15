import json
import os

import pandas as pd

import numpy as np

import matplotlib.pyplot as plt


def get_average_queuesize(df):
    average_queuesize = df['queueSize'].astype(float).mean()

    return average_queuesize



def get_latency_log_dataframe(df):
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
    df['latency'] = df['timeRealDoneOffset'].astype(float) - df['timeRealOffset'].astype(float)
    latency = np.mean(df['latency'])

    # We divided during middleware measure, we need to multiple again
    # df['originalTimeRealDoneOffset'] = df['timeRealDoneOffset'].multiply(df['totalRequests'])
    # df['originalTimeRealOffset'] = df['timeRealOffset'].multiply(df['totalRequests'])

    # throughput = np.mean(df['totalRequests'].astype(float)) / latency

    # TODO: How to calculate throughput?

    throughput = np.mean(df['throughput'].astype(float))
    # print("Ops per second: ", throughput)
    # # 4. Calculate the mean throughput
    # throughput = len(df['totalRequests']) / latency

    # print("SSS")
    # print(throughput)

    return throughput, latency

def render_lineargraph_multiple_errorbars(
        labels,
        mean_array,
        stddev_array,
        filepath,
        is_latency=False,
        is_read_write=False,
        is_sharded=False,
        is_queue_size=False
):
    """
        Renders and saves the graph to the given filepath.
        Use this if you have a numpy array of the following type:

            (number_of_middlewarethread_tries, number_of_virtualclientthreads)
    :param labels:
    :param mean_array:
    :param stddev_array:
    :return:
    """

    max_ele = np.nanmax(mean_array + 2*stddev_array) * 1.1

    for i in range(mean_array.shape[0]):
        if is_sharded:
            if i == 0:
                thelabel = "non-sharded"
            else:
                thelabel = "sharded"
        elif is_read_write:
            if i == 0:
                thelabel = "read"
            else:
                thelabel = "write"
        else:
            thelabel = 'Middleware threads {}'.format( 2**(i+3) )
        plt.errorbar(labels, mean_array[i,:], stddev_array[i,:], linestyle='--',
                     marker='.', markersize=10, label=thelabel, capsize=5)

    plt.ylim(ymin=0, ymax=max_ele)
    plt.xlim(xmin=0)
    plt.legend(loc='best')
    plt.gca().legend()

    if is_queue_size:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Average number of requests in queue')
    elif is_latency:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Latency in ms')
    else:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Throughput in ops / sec')

    if filepath is None:
        plt.show()
    else:
        plt.savefig(filepath)
    plt.clf()

def render_lineargraph_errorbars(
        labels,
        mean_array,
        stddev_array,
        filepath,
        shownow=True,
        is_latency=False,
        label=""
):
    """
        Renders and saves the graph to the given filepath
    :param labels:
    :param mean_array:
    :param stddev_array:
    :return:
    """
    max_ele = np.nanmax(mean_array + 2*stddev_array) * 1.1

    plt.errorbar(labels, mean_array, stddev_array, linestyle='--',
                 marker='.', markersize=7, capsize=5)

    plt.ylim(ymin=0, ymax=max_ele)
    plt.xlim(xmin=0)

    if is_latency:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Latency in ms')
    else:
        plt.xlabel('Number of Virtual Clients per Thread')
        plt.ylabel('Throughput in ops / sec')

    if shownow:
        if filepath is None:
            plt.show()
        else:
            plt.savefig(filepath)
        plt.clf()

def create_datadir_if_not_exists(directory):
    """
        Creates the directory to which we save the figures we render
        (if not yet existent)
    :return:
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_throughput_latency_default_memtier(filepath):
    """
        Given a filepath, it retrieves the latency and throughput of that experiment
        (The total experiment values, not differentiated by set and get values)
    :param filepath:
    :return:
    """
    with open(filepath) as f:
        data = json.load(f)

    # Throughput
    throughput = data['ALL STATS']['Totals']['Ops/sec']
    latency = data['ALL STATS']['Totals']['Latency']

    return throughput, latency