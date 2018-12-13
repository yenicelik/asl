# First, parse the file as json
import numpy as np

from utils import get_throughput_latency_default_memtier, \
    create_datadir_if_not_exists, render_lineargraph_errorbars, get_latency_log_dataframe, \
    render_lineargraph_multiple_errorbars, get_average_queuesize

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

        mw_queueusize_means = np.zeros((total_virtual_clients, total_middleware_threads))
        mw_queueusize_stddev = np.zeros((total_virtual_clients, total_middleware_threads))

        for _vc in range(0, 6):
            vc = (2 ** _vc)

            for _mt in range(3 - 3, 7 - 3):
                mt = (2 ** (_mt + 3))

                all_queuesizes = []

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
                        avg_queuesize = get_average_queuesize(df)
                        all_queuesizes.append(avg_queuesize)

                    except Exception as e:
                        print("WRONG WITH THE FOLLOWING CONFIG: ", middleware_filename)
                        print(e)
                        continue

                print("VC and MT ", (mt, vc))
                print("NEW VC and MT ", (_mt, _vc))

                mw_mean_queuesize = np.mean(all_queuesizes)
                mw_stddev_queuesize = np.std(all_queuesizes)
                # Append to list
                mw_queueusize_means[_vc, _mt] = mw_mean_queuesize
                mw_queueusize_stddev[_vc, _mt] = mw_stddev_queuesize


        # Plot the middleware values
        render_lineargraph_multiple_errorbars(
            labels=virtual_clients,
            mean_array=mw_queueusize_means.T,
            stddev_array=mw_queueusize_stddev.T,
            filepath=GRAPHPATH + "exp3_1__queuesize_middleware_write_{}".format(write),
            is_latency=False,
            is_queue_size=True
        )



if __name__ == "__main__":
    print("Starting to prepare the line-plots")

    iterate_through_experiments_exp3_1()
