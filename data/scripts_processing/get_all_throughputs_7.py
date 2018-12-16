"""
    For section 7, gets all throughputs from section 4

    I consider the following parameters to attain the following values
    lam := Arrival rate in jobs per unit time
    mu := Serivce rate in jobs per unit time

    I take lambda as: - mean arrival rate
        The throughput from the clients

    I take mu as: - mean service rate
        The throughput that my middleware is maximally able to process

    I am given the following values:
        - lambda (max throughput of client)
        - mu (max throughput of middleware)

    I predict the following values:
        - rho (traffic intensity)
        - queue length
        - latency
        - wait time



"""

# in order of Memtier Threads
observed_queue_length = [33.88, 2.4, 48.51, 13.64]
observed_latency = [9.73, 3.95, 13.61, 11.19]
observed_wait_time = [1.72, 2.90, 4.97, 8.76]

import numpy as np

from equations import get_traffic_intensity, get_mean_number_of_jobs_in_queue, \
    get_mean_response_time, get_mean_waiting_time, get_traffic_intensity_mmm, \
    get_mean_queue_size_mmm, get_p0, get_small_ro, get_mean_response_time_mmm, \
    get_mean_waiting_time_mmm

def calculate_everything_mm1(lam, mu):

    assert lam.shape == mu.shape, (lam.shape, mu.shape)

    traffic_intensity = get_traffic_intensity(lam, mu)
    print("Traffic intensity ", traffic_intensity)

    queue_length = get_mean_number_of_jobs_in_queue(traffic_intensity)
    print("Queue length: ", queue_length)

    response_time = get_mean_response_time(mu, traffic_intensity)
    print("Mean response time: ", response_time)

    wait_time = get_mean_waiting_time(traffic_intensity, mu)
    print("Wait time is: ", wait_time)

def calculate_everything_mmm(lam, mu, middlewarethreads):
    services = middlewarethreads

    # services = np.asarray([16, 32, 64, 128])
    # mu = mu / services
    traffic_intensity = get_traffic_intensity_mmm(lam, mu, services)
    print("Traffic intensity ", traffic_intensity)

    # some necessary pre-calculations
    p0 = get_p0(traffic_intensity, middlewarethreads)
    small_rho = get_small_ro(middlewarethreads, traffic_intensity, p0)

    print("Adjusted mean is: ", (mu))

    queue_length = get_mean_queue_size_mmm(traffic_intensity, small_rho)
    print("Queue length: ", queue_length)

    response_time = get_mean_response_time_mmm(traffic_intensity, mu, small_rho, services)
    print("Mean response time: ", response_time)

    wait_time = get_mean_waiting_time_mmm(mu, small_rho, services, traffic_intensity)
    print("Wait time is: ", wait_time)


if __name__ == "__main__":
    # from equations import
    # (Virtual Clients per Thread, Memtier Threads)
    STATS_CLIENT = [
        [2656.66666667, 2626.72666667, 2632., 2446.75333333], # VC 1
        [5024.45333333, 5075.88, 5013.73, 3978.32333333], # VC 2
        [7141.74333333, 7337.37666667, 6490.87, 7266.25], # VC 4
        [7725.51666667, 8915.62333333, 9007.14666667, 7466.56], # VC 8
        [7488.19666667, 8858.88333333, 9078.78, 10831.62], # VC 16
        [8120.06333333, 9209.27333333, 11769.20666667, 12150.17] # VC 32
    ]
    # (Virtual Clients per Thread, Memtier Threads)
    STATS_MW = [
        [2664.70132803, 2641.41654227, 2659.16928326, 2500.8709596], # VC 1
        [5044.87891294, 5099.86250867, 4969.28177418, 4470.9949093], # VC 2
        [7162.72644302, 7358.23351992, 7238.39810733, 7269.8259741], # VC 4
        [8278.15711411, 8919.24392224, 8985.27862859, 8871.1915683], # VC 8
        [7451.92149022, 10491.20785993, 11281.83772559, 11775.754328],  # There is one nan (last item in this row)! # VC 16
        [8157.63297235, 9896.43692309, 11775.75432867, 12984.0081002], # VC 32
    ]

    maximum_service_times = STATS_MW[-1]
    mean_arrival_rate = STATS_CLIENT[-1]
    #
    services = [2*8, 2*16, 2*32, 2*64]
    for i in range(4):
        lam = mean_arrival_rate[i] # ARRIVAL RATE
        mu = maximum_service_times[i] # SERVICE TIME
        m = services[i]
        mu = mu / m
        print()
        calculate_everything_mmm(lam, mu, m)

    # mu = np.max(STATS_MW, axis=0)
    # lam = np.max(STATS_CLIENT, axis=0)
    #
    # calculate_everything_mm1(lam, mu)

