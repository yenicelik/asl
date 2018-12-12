# First, parse the file as json
import json
import os

import numpy as np

import matplotlib.pyplot as plt

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_errorbars, \
    get_latency_log_dataframe, render_lineargraph_multiple_errorbars

from middleware_xml_to_csv import parse_log

# Do it for experiment 1 for now

BASEPATH = "/Users/david/asl-fall18-project/data/raw/exp3_2_backups/"
GRAPHPATH = "/Users/david/asl-fall18-project/report/img/exp3_2/"

def get_pattern_exp3_2_middleware(
        virtualclientthreads,
        middlewarethreads,
        repetition,
        write,
        middleware
):
    """
        Gets the filename given the above specification for the middleware threads
    :return:
    """
    out = "Middleware{}_threads_{}_vc_{}_rep_{}__writes_{}/"
    out = out.format(middleware, middlewarethreads, virtualclientthreads, repetition, write)
    return out


def get_pattern_exp3_2_client(virtual_client_threads, middlewareworkerthreads, repetition, client, write, middleware):
    """
        Get's the filename given the above specifications.
        This is for easier handling of the data
    :param virtual_client_threads:
    :param repetition:
    :param client:
    :param write:
    :return:
    """
    out = "Exp32_virtualclients_{}_middlewareworkerthreads_{}__rep_{}_client_{}_writes_{}.txt_Exp32_MW{}.txt"
    out = out.format(virtual_client_threads, middlewareworkerthreads, repetition, client, write, middleware)
    return out

#### Iterating through all experiment files, creating the graphs
def iterate_through_experiments_exp3_2():
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

                    for middleware in [1, 2]:

                        # Get throughput and latency from the file
                        middleware_filename = get_pattern_exp3_2_middleware(
                            virtualclientthreads=vc,
                            middlewarethreads=mt,
                            repetition=repetition,
                            write=write,
                            middleware=middleware
                        )

                        try:
                            df = parse_log(BASEPATH + middleware_filename)
                            mw_throughput, mw_latency = get_latency_log_dataframe(df)
                            mw_throughput *= mt * 1000 # because we have two middlewares # * (2./3.) # because the load of the clients is distributed on two middlewares

                            print("Throughput is: ", mw_throughput)

                            mw_all_throughputs.append(mw_throughput)
                            mw_all_latencies.append(mw_latency)

                        except Exception as e:
                            print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                            print(e)
                            continue

                    for client in ['Client1', 'Client2', 'Client3']:

                        client_filename = get_pattern_exp3_2_client(
                            virtual_client_threads=vc,
                            middlewareworkerthreads=mt,
                            repetition=repetition,
                            client=client,
                            write=write,
                            middleware=middleware
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
                mw_mean_throughput = np.sum(mw_all_throughputs) / 3. / 2. # because we have 3 repeats, and two middlewares (throughput per middleware is calculated as the total throughput)
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
        print("###write:client ", write, client_throughput_means)
        print("###write:middleware ", write, mw_throughput_means)
        ###write:client  0
        # [[ 1920.88        1918.63333333  1879.97666667  2040.63666667]
        # [2948.59        2948.03        2953.48666667  4106.08333333]
        # [2984.82333333  2906.10666667  2994.25        7329.56]
        # [2968.63666667  2931.46333333  4117.91        9388.87666667]
        # [2948.98        2924.93       10709.36       10652.36333333]
        # [2967.09333333  2988.49       11116.91333333 10953.04]]
        ###write:middleware  0
        # [[ 1823.82088122  1831.66427863  1788.32232092  1963.94693059]
        # [2894.0011844   2893.19407003  2889.4399206   3919.63102998]
        # [2904.84043756 2916.86120553 2914.29668445 6350.16067147]
        # [2919.44080752  2923.44783548  2898.39238625  8313.77410761]
        # [2916.26533345 2912.31134097 9796.16787827 9657.16189206]
        # [2923.77401065  2917.48683475 10330.97247506  9984.91367675]]

        ###write:client  1
        # [[1371.69       1433.82666667 1428.60333333 1474.68333333]
        # [2243.24333333 2678.12       2598.63       2644.23]
        # [3439.77333333 4868.33       4909.14       3774.43333333]
        # [5648.88333333 5682.95333333 6149.03       6716.31666667]
        # [5882.05       7103.95333333 6660.81333333 8108.17]
        # [5883.05333333 6663.61333333 6983.25666667 4487.62]]
        ###write:middleware  1 [[1401.75925962 1472.40508414 1479.24123472 1517.59234247]
        # [2784.22311061 2977.37234977 2626.56406027 2976.11177963]
        # [5079.75686936 5304.33947114 4915.28801361 4549.81135794]
        # [6597.81205289 6870.64256402 6942.7881017  6715.72352865]
        # [6539.19650736 7693.89813362 8053.29642461 8131.41925129]
        # [6670.31737933 7462.38036606 7429.34669134 7160.16151776]]

        # LATENCIES
        print("###write:client ", write, client_latency_means)
        print("###write:middleware ", write, mw_latency_means)

        ###write:client  0
        # [[ 1.57666667  1.58        1.61333333  1.49777778]
        # [2.05555556 2.06222222 2.05777778 1.48888889]
        # [4.05666667  4.17        4.03777778  1.65222222]
        # [8.10111111 8.21222222 6.61666667 2.57333333]
        # [16.22222222 16.40888889  4.49777778  4.53666667]
        # [32.37111111 32.09222222 8.65888889 8.78444444]]
        ###write:middleware  0 [[ 0.75373062  0.71682754  0.79261609  0.68196475]
        # [1.14245532  1.15601874  1.12761835  0.6962914]
        # [3.00268178 3.06263071 3.08864053 0.82161966]
        # [7.07679403  6.89052932  6.98758393  1.18371943]
        # [15.26808786 15.11082288 1.48361568 1.50505344]
        # [31.39592934 31.16684201  1.71758052  1.96693429]]

        ###write:client  1 [[ 2.18222222  2.08888889  2.09666667  2.03111111]
        # [1.83222222  1.97444444  1.83111111  2.00444444]
        # [2.02111111  2.17222222  1.92888889  1.63666667]
        # [3.78        2.89777778  2.76444444  2.87222222]
        # [7.29444444  5.97222222  5.64333333  3.69111111]
        # [12.14444444 10.79       10.41555556 14.27666667]]
        ###write:middleware  1
        # [[ 1.14301648  1.03218857  1.02287563  0.98682917]
        # [1.02473659  1.01945742  1.08312422  1.00336116]
        # [1.09529057 1.12426547 1.15199756 1.10026307]
        # [2.38971881  1.71178708  1.66788647  1.66212348]
        # [5.65331611 3.1920922 2.80038391 2.75255764]
        # [11.12888022  4.42134564  2.9218675   2.73590902]]

        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=client_throughput_means.T,
            stddev_array=client_throughput_stddev.T,
            filepath=GRAPHPATH + "exp3_2__throughput_client_write_{}".format(write),
            is_latency=False
        )
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=client_latency_means.T,
            stddev_array=client_latency_stddev.T,
            filepath=GRAPHPATH + "exp3_2__latency_client_write_{}".format(write),
            is_latency=True
        )

        # Plot the middleware values
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=mw_throughput_means.T,
            stddev_array=mw_throughput_stddev.T,
            filepath=GRAPHPATH + "exp3_2__throughput_middleware_write_{}".format(write),
            is_latency=False
        )
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=mw_latency_means.T,
            stddev_array=mw_latency_stddev.T,
            filepath=GRAPHPATH + "exp3_2__latency_middleware_write_{}".format(write),
            is_latency=True
        )


if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp3_2()
