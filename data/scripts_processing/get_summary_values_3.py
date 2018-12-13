"""
    For the 3.3 summary, gets the following values

    Throughput, Response time, Average time in queue

    For
    Reads, Writes

    Per
    Middleware, Client

    For
    One Middleware, Two Middlewares
"""

def get_summary_values_3_1():
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
                        mw_throughput *= mt * 1000 # bcs this gives us overall throughput per millisecond, and not per thread anymore

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

        # LATENCIES
        print("###write:client ", write, client_latency_means)
        print("###write:middleware ", write, mw_latency_means)