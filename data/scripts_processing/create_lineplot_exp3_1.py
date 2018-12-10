# First, parse the file as json
import json
import os

import numpy as np

import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_errorbars, get_latency_log_dataframe, \
    render_lineargraph_multiple_errorbars

from middleware_xml_to_csv import parse_log

# Do it for experiment 1 for now

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp3_1_backups/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp3_1/"

def get_pattern_exp3_1_middleware(
        virtualclientthreads,
        middlewarethreads,
        repetition,
        write
):
    """
        Gets the filename given the above specification for the middleware threads
    :return:
    """
    out = "Middleware1_threads_{}_vc_{}_rep_{}__writes_{}/"
    out = out.format(middlewarethreads, virtualclientthreads, repetition, write)
    return out


def get_pattern_exp3_1_client(virtual_client_threads, middlewareworkerthreads, repetition, client, write):
    """
        Get's the filename given the above specifications.
        This is for easier handling of the data
    :param virtual_client_threads:
    :param repetition:
    :param client:
    :param write:
    :return:
    """
    out = "_Exp31_virtualclients_{}_middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}.txt"
    out = out.format(virtual_client_threads, middlewareworkerthreads, repetition, client, write)
    return out

#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp3_1():
    """
        Iterates through all the parameter combinations
    :return:
    """

    create_datadir_if_not_exists(GRAPHPATH)

    middleware_threads = [(2 ** x) for x in range(3, 7)]
    virtual_clients = [(2 ** x) for x in range(0, 6)]


    total_virtual_clients = len([(2 ** x) for x in range(0, 6)])
    total_middleware_threads = len([(2 ** x) for x in range(3, 7)])

    for write in [0, 1]:

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

                    # Get throughput and latency from the file
                    middleware_filename = get_pattern_exp3_1_middleware(
                        virtualclientthreads=vc,
                        middlewarethreads=mt,
                        repetition=repetition,
                        write=write,
                    )

                    try:
                        df = parse_log(BASEPATH + middleware_filename)
                        mw_throughput, mw_latency = get_latency_log_dataframe(df)
                        mw_throughput *= mt * 1000 # bcs this gives us throughput per millisecond

                        mw_all_throughputs.append(mw_throughput)
                        mw_all_latencies.append(mw_latency)

                    except Exception as e:
                        print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                        print(e)
                        continue

                    for client in ['Client1', 'Client2', 'Client3']:

                        client_filename = get_pattern_exp3_1_client(
                            virtual_client_threads=vc,
                            middlewareworkerthreads=mt,
                            repetition=repetition,
                            client=client,
                            write=write
                        )

                        # Trying to open and read the file!

                        try:
                            client_throughput, client_latency = get_throughput_latency_default_memtier(filepath=BASEPATH + client_filename)
                            client_all_throughputs.append(client_throughput)
                            client_all_latencies.append(client_latency)

                        except Exception as e:
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
        # print("###write:client ", write, client_throughput_means)
        # print("###write:middleware ", write, mw_throughput_means)
        # ###write:client  0
        # [[2808.04333333 2912.38666667 2917.14       2916.69      ]
        # [2957.69333333 2967.07333333 2957.22333333 2962.41]
        # [2986.96333333 2976.14333333 2969.88666667 2972.36333333]
        # [2988.29       2980.04666667 2976.67666667 2987.68666667]
        # [2961.82       2968.33666667 2975.86333333 7166.16333333]
        # [2983.6        2987.40333333 2985.35333333 9925.5]]
        # ###write:middleware  0
        # [[2814.28795108 2909.57035297 2909.50208686 2907.51873273]
        # [2947.85394772 2928.45272645 2919.24938258 2921.52773026]
        # [2937.36828099 2926.9496225 2921.8400783 2920.19631043]
        # [2934.20444822 2927.39357662 2928.74422209 2931.34928209]
        # [2921.6549093 2928.63869325 2933.69841429 7294.81515571]
        # [2925.00471205 2930.35156472 2931.80591956 9933.96596083]]
        # ###write:client  1
        # [[3151.47666667 3559.28666667 3324.88666667 3440.13      ]
        # [5370.58666667 4486.21333333 4963.17666667 5342.47666667]
        # [6175.65333333 5952.35666667 6788.61666667 6076.56666667]
        # [6629.1        7423.78       7670.52       5945.98666667]
        # [6572.59       5647.82       5726.37333333 5502.28333333]
        # [6456.87       5984.54       5639.96333333 5521.53666667]]
        # ###write:middleware  1
        # [[3499.27350268 3588.32402915 3554.46010296 3485.94742652]
        # [5705.01707986 5084.74707977 5367.4309447  5418.90268995]
        # [7230.21690239 6757.01582276 6908.48512654 6828.03282813]
        # [6605.33768657 8291.93250908 7770.34656525 7524.4092148]
        # [6539.32516182 5734.69643989 5847.30781505 6086.5050552]
        # [6690.67373503 5949.01386219 5610.72881116 5473.04559517]]

        # LATENCIES
        print("###write:client ", write, client_latency_means)
        print("###write:middleware ", write, mw_latency_means)

        ###write:client  0
        # [[ 2.17111111  2.08666667  2.08111111  2.07888889]
        # [4.10111111  4.08222222  4.09        4.08888889]
        # [8.06444444  8.10222222  8.09111111  8.08111111]
        # [16.06888889 16.12111111 16.11444444 16.07777778]
        # [32.29222222 32.23222222 32.19       17.70444444]
        # [64.42666667 64.27222222 64.31777778 19.35]]
        ###write:middleware  0
        # [[ 1.25096676  1.1956242   1.17953668  1.19145878]
        # [3.11627907  3.01029601  3.10988641  3.10387539]
        # [7.18604651 6.93698374 6.9993565 6.88478283]
        # [15.29021634 15.15958816 14.80194665 14.59036723]
        # [31.69589434 31.49905852 31.103991 12.20818745]
        # [64.39753086 64.12792128 63.4432167   2.54793041]]

        ###write:client  1
        # [[ 1.74888889  1.71        1.67333333  1.78      ]
        # [2.20333333  2.41444444  2.20666667  2.26]
        # [3.5         3.66333333  3.55666667  3.55888889]
        # [7.24333333  6.31777778  6.27111111  6.39888889]
        # [14.55111111 16.97666667 16.64111111 15.76444444]
        # [29.73777778 32.25666667 34.10111111 34.72111111]]
        # ###write:middleware  1 [[0.8372779  0.79849772 0.78635779 0.82680607]
        # [1.05682468 1.04084508 1.02484681 1.07172404]
        # [2.22727585 1.68597169 1.71814672 1.76064804]
        # [3.96899225 3.02239382 2.36321394 2.21572826]
        # [5.71059432 2.26458732 2.03719422 2.20171653]
        # [7.32905668 3.37894591 2.5367597 2.49948734]]


        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=client_throughput_means.T,
            stddev_array=client_throughput_stddev.T,
            filepath=GRAPHPATH + "exp3_1__throughput_client_write_{}".format(write),
            is_latency=False
        )
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=client_latency_means.T,
            stddev_array=client_latency_stddev.T,
            filepath=GRAPHPATH + "exp3_1__latency_client_write_{}".format(write),
            is_latency=True
        )

        # Plot the middleware values
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=mw_throughput_means.T,
            stddev_array=mw_throughput_stddev.T,
            filepath=GRAPHPATH + "exp3_1__throughput_middleware_write_{}".format(write),
            is_latency=False
        )
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=mw_latency_means.T,
            stddev_array=mw_latency_stddev.T,
            filepath=GRAPHPATH + "exp3_1__latency_middleware_write_{}".format(write),
            is_latency=True
        )



if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp3_1()
