"""
    The XML files consume way too much space.
    We will need to parse them into csv's of only entries (no XML overhead)

    The keys saved by the middleware are the following

        uuid, requestType, threadID, timeRealOffset,
        differenceTimeCreatedAndEnqueued,
        differenceTimeEnqueuedAndDequeued,
        differenceTimeDequeuedAndSentToServer,
        differenceTimeSentToServerAndReceivedResponseFromServer,
        differenceTimeReceivedResponseFromServerAndSentToClient,
        timeRealDoneOffset

"""

# "Middleware1_threads_4_vc_1_rep_0__writes_0"

import pandas as pd
import os

PROCESSED_PATH = "/Users/david/asl-fall18-project/data/processed/exp3_1_backup/"
BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp3_1_backup/"

EXAMPLE_FILE = BASEPATH + "Middleware1_threads_64_vc_1_rep_0__writes_0/log.txt.1"
EXAMPLE_DIR = BASEPATH + "Middleware1_threads_64_vc_1_rep_0__writes_0/"

def parse_single_log(filename):
    """
        Parses a single log file
    :return: all the records contained in this single log record
    """
    out = []

    with open(filename, encoding="utf-8") as file:
        for line in file:

            if "<message>||" in line:
                logline = line.split("|| ")[1]
                logline = logline.split("<")[0]
                logline = logline.split(",")
                logline = tuple([x.strip() for x in logline])
                out.append(logline)

    return out

def parse_single_log_exp5_1(filename):
    """
        Parses a single log file
    :return: all the records contained in this single log record
    """
    out = []

    with open(filename, encoding="utf-8") as file:
        for line in file:

            if "<message>-|-|" in line:
                logline = line.split("-|-|")[1]
                logline = logline.split("<")[0]
                logline = logline.split(",")
                logline = tuple([x.strip() for x in logline])
                out.append(logline)

    return out

def parse_log_exp5_1(directory):
    """
        Opens stuff
    :param directory:
    :return:
    """
    full_records = []
    print("Directory is: ", directory)
    files = list(os.listdir(directory))
    files = [x.strip() for x in files if ".lck" not in x]

    for file in files:
        tmp = parse_single_log_exp5_1(directory + file)
        full_records += tmp

    out = pd.DataFrame(full_records, columns=[
        "timeRealOffset",
        "differenceTimeCreatedAndEnqueued",
        "differenceTimeEnqueuedAndDequeued",
        "differenceTimeDequeuedAndSentToServer",
        "differenceTimeSentToServerAndReceivedResponseFromServer",
        "differenceTimeReceivedResponseFromServerAndSentToClient",
        "timeRealDoneOffset",
        "totalRequests",
        "type"
    ])

    return out


def parse_log(directory):
    """
        Opens up the logs for a single log-directory, and parses all items
    :return: a dataframe with all the logs concatenated from the individual log files
    """

    full_records = []

    files = list(os.listdir(directory))
    files = [x.strip() for x in files if ".lck" not in x]

    for file in files:

        tmp = parse_single_log(directory + file)

        full_records += tmp

    out = pd.DataFrame(full_records, columns=[
        "timeRealOffset",
        "differenceTimeCreatedAndEnqueued",
        "differenceTimeEnqueuedAndDequeued",
        "differenceTimeDequeuedAndSentToServer",
        "differenceTimeSentToServerAndReceivedResponseFromServer",
        "differenceTimeReceivedResponseFromServerAndSentToClient",
        "timeRealDoneOffset",
        "totalRequests",
        "throughput",
        "queueSize"
    ])

    return out

def iterate_through_all_logs_in_experiment_directory():
    """
        This is the main function which takes all
    :return:
    """
    template = "Middleware1_threads_{}_vc_{}_rep_{}__writes_0/"

    for virtual_client_threads in [(2 ** x) for x in range(0, 6)]:

        for middleware_workerthread in [(2 ** x) for x in range(3, 7)]:

            for i in range(3):

                dirpath = template.format(
                    middleware_workerthread,
                    virtual_client_threads,
                    i
                )

                print("Parsing file: ", BASEPATH + dirpath)

                if os.path.exists(BASEPATH + dirpath):
                    log_dataframe = parse_log(BASEPATH + dirpath)

                    if len(log_dataframe) > 0:
                        log_dataframe.to_csv(PROCESSED_PATH + dirpath[:-1] + ".csv")

    print("Done!")


if __name__ == "__main__":
    print("Well")
    # parse_single_log(EXAMPLE_FILE)
    iterate_through_all_logs_in_experiment_directory()
