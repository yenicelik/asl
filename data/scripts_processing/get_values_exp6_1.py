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

    write = 0  # This experiment consists of writes-only!

    final_client_throughputs = []
    final_mw_throughputs = []

    final_client_latencies = []
    final_mw_latencies = []



    print("WRITES ARE:::: ", write)

    for number_of_servers in [1, 3]:

        for number_of_middlewares in [1, 2]:

            for number_of_middleware_workerthreads in [8, 32]:

                client_all_throughputs = []  # From here on, we average over all values
                client_all_latencies = []

                mw_all_throughputs = []
                mw_all_latencies = []

                for repetition in range(3):

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

                    for client in ['Client1', 'Client2', 'Client3']:
                        for middleware in _array_middlewares:

                            client_filename = get_pattern_exp6_1_client(
                                middleware=middleware,
                                servers=number_of_servers,
                                number_of_middlewares=number_of_middlewares,
                                middlewareworkerthreads=number_of_middleware_workerthreads,
                                repetition=repetition,
                                client=client,
                                write=write
                            )

                            try:
                                client_throughput, client_latency = get_throughput_latency_default_memtier(
                                    filepath=BASEPATH + client_filename)
                                client_all_throughputs.append(client_throughput)
                                client_all_latencies.append(client_latency)

                            except Exception as e:
                                # print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                                print("WRONG WITH THE FOLLOWING CONFIG: ", client_filename)
                                print(e)
                                continue

                mw_mean_latency = np.mean(mw_all_latencies)
                mw_mean_throughput = np.sum(mw_all_throughputs) / 3.
                mw_stddev_latency = np.std(mw_all_latencies)
                mw_stddev_throughput = np.std(mw_all_throughputs)

                client_mean_latency = np.mean(client_all_latencies)
                client_mean_throughput = np.sum(client_all_throughputs) / 3.
                client_stddev_latency = np.std(client_all_latencies)
                client_stddev_throughput = np.std(client_all_throughputs)

                ## Appending middleware and client values to the tuple list
                # final_client_throughputs = []
                # final_mw_throughputs = []
                #
                # final_client_latencies = []
                # final_mw_latencies = []

                configuration = (number_of_servers, number_of_middlewares, number_of_middleware_workerthreads)

                final_client_throughputs.append(
                    (configuration, (client_mean_throughput, client_stddev_throughput))
                )
                final_mw_throughputs.append(
                    (configuration, (mw_mean_throughput, mw_stddev_throughput))
                )

                final_client_latencies.append(
                    (configuration, (client_mean_latency, client_stddev_latency))
                )
                final_mw_latencies.append(
                    (configuration, (mw_mean_latency, mw_stddev_latency))
                )

    # Iterating through individual lists for easy copy pasta
    print("CLIENT THROUGHPUT")
    for x in final_client_throughputs:
        print(x)

    print("MIDDLEWARE THROUGHPUT")
    for x in final_mw_throughputs:
        print(x)

    print("CLIENT LATENCY")
    for x in final_client_latencies:
        print(x)

    print("MIDDLEWARE LATENCY")
    for x in final_mw_latencies:
        print(x)


if __name__ == "__main__":
    print("Starting to prepare the values for the 2k experiments")

    iterate_through_experiments_exp6_1()

    # Read-only operations!
    # CLIENT THROUGHPUT
    # ((1, 1, 8), (3236.14, 41.490879854627195))
    # ((1, 1, 32), (3238.0633333333335, 39.175974528362566))
    # ((1, 2, 8), (3299.116666666667, 39.025349426232))
    # ((1, 2, 32), (3282.44, 38.72366015184457))
    # ((3, 1, 8), (7957.243333333333, 115.09004215165238))
    # ((3, 1, 32), (8690.543333333333, 122.37375243061973))
    # ((3, 2, 8), (8843.03, 64.17493862266035))
    # ((3, 2, 32), (9064.64, 67.59237629595022))
    # MIDDLEWARE THROUGHPUT
    # ((1, 1, 8), (3016.251376529342, 9.98880115676693))
    # ((1, 1, 32), (2931.789381831173, 19.84155818849284))
    # ((1, 2, 8), (2983.5829172137255, 79.68869790153506))
    # ((1, 2, 32), (2966.462327439984, 36.23716606215686))
    # ((3, 1, 8), (7831.5056127847565, 16.068401742084166))
    # ((3, 1, 32), (8279.294563719499, 63.89607403117203))
    # ((3, 2, 8), (8312.87060732433, 90.18106618450823))
    # ((3, 2, 32), (8246.439493131942, 32.21043366652255))
    # CLIENT LATENCY
    # ((1, 1, 8), (59.337777777777774, 2.409171262662642))
    # ((1, 1, 32), (59.36555555555555, 2.181839749238707))
    # ((1, 2, 8), (58.548333333333325, 4.267977988592619))
    # ((1, 2, 32), (58.83611111111111, 4.351958867872526))
    # ((3, 1, 8), (24.193333333333335, 1.034386560022681))
    # ((3, 1, 32), (22.124444444444446, 0.9664035401782918))
    # ((3, 2, 8), (21.756666666666668, 0.9723168207945395))
    # ((3, 2, 32), (21.229444444444443, 0.9981008200144813))
    # MIDDLEWARE LATENCY
    # ((1, 1, 8), (59.63239436619718, 0.21244740997143538))
    # ((1, 1, 32), (58.024604569420035, 0.7490874638260373))
    # ((1, 2, 8), (61.14201877934272, 2.8015291137226876))
    # ((1, 2, 32), (58.39433487383106, 2.0544641036118994))
    # ((3, 1, 8), (23.825757575757574, 0.07037372655366131))
    # ((3, 1, 32), (19.806951703084298, 0.2578144191650141))
    # ((3, 2, 8), (20.45216761810209, 0.2924819078929451))
    # ((3, 2, 32), (20.23104272903077, 0.6196011566050112))


    # Write-only operations!
    # CLIENT THROUGHPUT
    # ((1, 1, 8), (7955.389999999999, 76.27378317613463))
    # ((1, 1, 32), (8314.336666666668, 67.66472921875112))
    # ((1, 2, 8), (9253.689999999999, 736.4126117066136))
    # ((1, 2, 32), (14947.326666666666, 109.67250344125758))
    # ((3, 1, 8), (5238.7699999999995, 178.21092926953474))
    # ((3, 1, 32), (7266.589999999999, 131.00334270544394))
    # ((3, 2, 8), (8367.576666666666, 350.14897109244623))
    # ((3, 2, 32), (11624.713333333333, 94.66373036733138))
    # MIDDLEWARE THROUGHPUT
    # ((1, 1, 8), (7999.949350606581, 479.4927039333444))
    # ((1, 1, 32), (7857.037209060259, 368.5734265066675))
    # ((1, 2, 8), (10936.079404310198, 588.2595763634373))
    # ((1, 2, 32), (15100.158718312823, 164.19250147702303))
    # ((3, 1, 8), (4716.230030840822, 439.64324448323424))
    # ((3, 1, 32), (6820.91488168888, 367.3220613357542))
    # ((3, 2, 8), (8304.465506840197, 345.7272430780726))
    # ((3, 2, 32), (11730.32610601097, 160.40122442368101))
    # CLIENT LATENCY
    # ((1, 1, 8), (24.02777777777778, 0.7009957644154461))
    # ((1, 1, 32), (23.00333333333333, 0.5479456582950943))
    # ((1, 2, 8), (18.028333333333332, 2.919414419974587))
    # ((1, 2, 32), (12.149999999999999, 0.5279483040646177))
    # ((3, 1, 8), (37.08888888888888, 3.911502821293583))
    # ((3, 1, 32), (26.4, 1.4297863088199192))
    # ((3, 2, 8), (21.720000000000002, 1.334470348531998))
    # ((3, 2, 32), (15.63823529411765, 0.7519405115246632))
    # MIDDLEWARE LATENCY
    # ((1, 1, 8), (10.787217931243374, 3.5295872575501974))
    # ((1, 1, 32), (2.109584111024827, 0.01196239341274574))
    # ((1, 2, 8), (17.26126989161588, 3.4225159703537664))
    # ((1, 2, 32), (7.739595683171385, 0.9211237338964331))
    # ((3, 1, 8), (35.01734154929577, 3.7094723286888684))
    # ((3, 1, 32), (8.430878361626176, 1.756767527503239))
    # ((3, 2, 8), (21.568491594729668, 1.3462077633196108))
    # ((3, 2, 32), (12.634094328452472, 0.7275012387819505))
