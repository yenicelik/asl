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

        max_throughput = 0
        max_throughput_client = 0

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

                queuetimes = []

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
                        mw_throughput *= mt * 1000 # bcs this gives us overall throughput per millisecond, and not per thread anymore

                        queuetimes.append(df['differenceTimeEnqueuedAndDequeued'].astype(float).mean())

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

                            print("Client: ", client_throughput, client_latency)

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

                if max_throughput < mw_mean_throughput:
                    max_throughput = mw_mean_throughput
                    print("TTT", write, mw_mean_throughput, mw_mean_latency, np.mean(queuetimes))

                # Append to list
                mw_throughput_means[_vc, _mt] = mw_mean_throughput
                mw_latency_means[_vc, _mt] = mw_mean_latency
                mw_throughput_stddev[_vc, _mt] = mw_stddev_throughput
                mw_latency_stddev[_vc, _mt] = mw_stddev_latency

                client_mean_latency = np.mean(client_all_latencies)
                client_mean_throughput = np.sum(client_all_throughputs) / 3.
                client_stddev_latency = np.std(client_all_latencies)
                client_stddev_throughput = np.std(client_all_throughputs)


                if max_throughput_client < client_mean_throughput:
                    max_throughput_client = client_mean_throughput
                    print("TTT CLIENT", write, client_mean_throughput, client_mean_latency)

                # Maximal values at: (printouts!)


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

        # LATENCIES
        print("###write:client ", write, client_latency_means)
        print("###write:middleware ", write, mw_latency_means)

        ###write:client  0 [[2829.99666667 2828.78       2841.12333333 2832.09666667]
        # [2914.32       2916.49       2902.36666667 2963.79      ]
        # [2978.07       2982.04       2926.90666667 2961.14      ]
        # [2930.64       2996.5        2980.55333333 2971.27666667]
        # [2920.55666667 2939.13       2975.22333333 2949.03333333]
        # [2966.08666667 2969.74666667 2933.78       2944.79      ]]
        # ###write:middleware  0 [[2888.56768177 2872.94686583 2876.40834308 2863.0490837 ]
        # [2952.04131319 2937.70233791 2918.01762357 2947.80422581]
        # [2989.20268883 2974.35714111 2912.9803837  2934.38863854]
        # [2933.52705812 2979.39794505 2961.4934029  2940.88512509]
        # [2915.57629929 2930.44136708 2952.3195043  2941.34950968]
        # [2983.28945045 2974.97495859 2925.1779705  2935.00349311]]
        # ###write:client  0 [[ 2.11333333  2.11222222  2.10555556  2.11111111]
        # [ 4.12222222  4.11555556  4.14        4.04888889]
        # [ 8.06        8.05444444  8.19444444  8.10111111]
        # [16.44666667 16.03333333 16.06111111 16.17111111]
        # [32.96       32.63777778 32.23333333 32.51333333]
        # [64.82444444 64.60222222 65.45       65.20888889]]
        # ###write:middleware  0 [[ 1.3167424   1.18404118  1.19176319  1.17406692]
        # [ 3.05772075  3.06435006  3.08202826  3.02690768]
        # [ 7.03875969  6.86615187  6.97812098  6.82174604]
        # [15.12661499 14.78340234 14.6029601  14.49839125]
        # [31.04134367 30.77606178 30.94594595 30.51061114]
        # [64.37984496 63.11079911 63.46138996 62.44980695]]

        ###write:client  1 [[3271.34       3220.32666667 3215.53333333 3321.11666667]
        # [5386.31666667 5549.33333333 5136.30666667 5292.51333333]
        # [6729.64333333 6900.06333333 6690.59666667 6214.48333333]
        # [7061.56       7363.10333333 7541.20666667 7139.32333333]
        # [7295.09       7490.80666667 7629.65333333 6914.55      ]
        # [7228.72       6711.01666667 7753.10333333 7454.68      ]]
        # ###write:middleware  1 [[3287.41072931 3284.10276218 3236.10885263 3348.17928571]
        # [5425.01178366 5583.56806439 5174.72885707 5332.7263551 ]
        # [6667.75480504 6881.43820305 6818.78960064 7011.40707111]
        # [6968.99163433 7292.81531008 7476.06856816 7092.02329642]
        # [7199.49091298 7430.69321895 7658.79654156 7739.66985074]
        # [7369.68367374 7615.74155019 7635.26281836 7333.33824439]]
        # ###write:client  1 [[ 1.83333333  1.86333333  1.86444444  1.80555556]
        # [ 2.24777778  2.16444444  2.34555556  2.28      ]
        # [ 3.58        3.48222222  3.48888889  3.41111111]
        # [ 6.81444444  6.53555556  6.38222222  6.77      ]
        # [13.19111111 12.80444444 12.57444444 12.30222222]
        # [26.64888889 25.42666667 24.74444444 25.82111111]]
        # ###write:middleware  1 [[ 0.95865633  0.99356499  0.98584299  0.94144144]
        # [ 1.05426357  1.07722008  1.14740262  1.10841916]
        # [ 1.73901809  1.4002574   1.41508969  1.48529033]
        # [ 3.26873385  1.85971686  1.72651223  1.84685326]
        # [ 5.56330749  2.57014157  2.15837807  2.01412311]
        # [15.27655236  3.07501152  2.19581187  2.69169728]]


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
