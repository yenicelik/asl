

def get_traffic_intensity(lam, mu):
    """
        Returns the traffic intensity (ro)
    :param lam:
    :param mu:
    :return:
    """
    return lam / float(mu)

def get_mean_number_of_jobs_entire_system(ro):
    """
        Returns the mean number of jobs
        in the entire system
        given the traffic intensity
    :param ro:
    :return:
    """
    return float(ro) / (1. - ro)

def get_mean_number_of_jobs_only_queue(ro):
    """
        Returns the mean number of jobs
        in the queue
        given the traffic intensity
    :param ro:
    :return:
    """
    return float(ro) ** 2 / (1. - ro)

def get_mean_response_time(mu, ro):
    """
        Returns the estimated mean response time
    :param mu:
    :param ro:
    :return:
    """
    return (1. / mu) * (1. - ro)

def get_mean_waiting_time(mu, ro):
    """
        Returns the estimated mean waiting time
    :param mu:
    :param ro:
    :return:
    """
    return ro * (1. / mu) / (1. - ro)

