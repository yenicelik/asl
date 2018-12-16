"""
    I consider the following parameters to attain the following values
    lam := Arrival rate in jobs per unit time
    mu := Serivce rate in jobs per unit time

    I take lambda as: - mean arrival rate
        The throughput from the clients

    I take mu as: - mean service time
        The throughput that my middleware is maximally able to process
"""

import numpy as np
import math


### get_traffic_intensity_mmm

### Formulae actually used
def get_traffic_intensity(lam, mu):
    """
        Return ro
    """
    return lam / mu

def get_mean_number_of_jobs_in_system(ro):
    """
        Returns E[n] = ro / (1-ro)
    """
    return ro / (1. - ro)

def get_mean_number_of_jobs_in_queue(ro):
    """
        Returns E[n_q]
    """
    return ro**2 / (1. - ro)

def get_mean_response_time(mu, ro):
    """
        Returns E[r]
    """
    return (1. / mu) / (1. - ro) * 1000

def get_mean_waiting_time(ro, mu):
    """
        Returns E[w]
    """
    return ro * (1. / mu) / (1. - ro) * 1000

### M/M/m
def get_traffic_intensity_mmm(lam, mu, m):
    """
        Return rho
    """
    return float(lam) / (mu * float(m) )

def get_p0(rho, m):
    a = 1
    b = ( float(m) * rho) ** m
    b = b / (math.factorial(m) * (1 - rho) )
    c = np.sum([ ((m * rho) ** i) / math.factorial(i) for i in range(1, m)])
    out = a + b + c
    out = 1. / out
    return out

def get_small_ro(m, rho, p_0):
    a = (m * rho) ** m
    b = math.factorial(m) * (1. - rho)
    c = p_0
    out = a / b * c
    return out

def get_mean_queue_size_mmm(rho, small_ro):
    out = rho * small_ro / (1. - rho)
    return out

def get_mean_response_time_mmm(ro, mu, small_ro, m):
    out = (1. / mu)
    out = out * (1. + ( small_ro / (m * (1. - ro) ) ) ) * 1000
    return out

def get_mean_waiting_time_mmm(mu, small_rho, m, rho):
    out = small_rho / (m * mu * (1. - rho)) * 1000
    return out

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - autismo


def get_stability_condition(ro):
    return ro < 1.

def get_probability_of_zero_jobs_in_system(ro):
    """
        Returns p_0
    """
    return 1. - ro

def get_probability_of_n_jobs_in_system():
    """
        Returns p_n
    """
    # TODO: How to calculate this?
    pass


def get_variance_of_number_of_jobs(ro):
    """
        Returns Var[n] = ro / (1. - ro)^2
    """
    return ro / (1. - ro)^2

def get_probability_of_k_jobs_in_the_queue(ro, k):
    """
        Returns P(n_q = k)
    """
    if k == 0:
        out = 1. - ro**2
    else:
        out = (1. - ro) * (ro ** (k + 1) )
    return out

def get_variance_of_number_of_jobs_in_queue(ro):
    """
        Returns Var[n_q]
    """
    return ro ** 2 (1. + ro - ro**2)/(1. - ro)**2

def get_cumulative_distribution_function_of_response_time(r, mu, ro):
    """
        Returns F(r)
    """
    return 1. - np.exp(-r * mu * (1. - ro) )


def get_variance_of_response_time(mu, ro):
    """
        Returns Var[r]
    """
    return 1. / mu**2 / (1. - ro)**2

def get_q_percentile_of_response_time(exp_r, q):
    return exp_r * np.ln(100. / (100. - q))

def get_90th_percentile_of_response_time(exp_r):
    return 2.3 * exp_r

def get_cumulative_distribution_waiting_time(ro, mu, w):
    return 1. - ro * np.exp(-mu * w (1. - ro) )




def get_variance_of_the_waiting_time(ro, mu):
    """
        Retusn Var[w]
    """
    return (2. - ro) * ro / ( (mu ** 2) (1. - ro)**2 )

def get_probability_of_finding_n_or_more_jobs(ro, n):
    return ro ** n

def n_choose_k(a, b):
    return math.factorial(a) / ( math.factorial(b) *  math.factorial(a - b) )

def get_probability_of_serving_n_jobs_in_one_busy_period(n, ro):
    return 1. / n * n_choose_k(2*n - 2, n - 1) * (ro ** (n - 1.) / (1. + ro)**(2*n - 1))

