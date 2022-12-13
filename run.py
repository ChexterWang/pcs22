import numpy
import warnings
from pandas import DataFrame
from numpy import array, sum, max, ones, isnan, average
from numpy.linalg import norm
from numpy.random import exponential, uniform
from math import pow, sqrt, log2

numpy.set_printoptions(precision=4)
warnings.filterwarnings('ignore')

# channel unit conversion func
dbm2watt = lambda d: 1e-3 * pow(10, d/10)

# channel parameter
B = 1e7 # total bandwidth of the channel = 10MHz
N0 = dbm2watt(-174) # power density of AWGN = -174dBm/Hz
gain_mean = 50

# computation parameter
beta = 0.5 # compression ratio
C = 1000 # cpu cycle for a bit = 1000 cycles/bit

# t(normalized duration of time slot), gradient update
xplus = lambda x: 1 if 1<(x if x>0 else 0) else (x if x>0 else 0)
delta_mu = lambda ul, dl : sum(ul+dl) - 1
delta_gamma = lambda e: sum(e) - 1
step = lambda k: 0.1/sqrt(k)

# iteration limit
delta = 1e-6
k = 1e5

def single_run(size=10, f_e=15e9, add_param=None):
    # number of device dependent parameters
    p_ul = array([dbm2watt(24) for i in range(size)])
    p_dl = array([dbm2watt(46) for i in range(size)])

    # randomized parameter
    h = array([dbm2watt(i) for i in exponential(1/gain_mean, size)])
    r_ul = array([B * log2(1 + p_ul[i]*pow(h[i], 2)/N0/B) for i in range(size)])
    r_dl = array([B * log2(1 + p_dl[i]*pow(h[i], 2)/N0/B) for i in range(size)])
    omega = uniform(1e5, 5e5, size)
    f_l = uniform(1e9, 4e9, size)
    v_l = f_l / C
    v_e = f_e / C

    if(add_param is not None):
        omega = add_param['omega']
        f_l = add_param['f_l']
        v_l = f_l / C

    # initialize multiplier(mu, eta_n, gamma)
    mu = 1
    eta = ones(size)
    gamma = 1

    # gradient update lambda func
    t_ul_n = lambda n: xplus(
        sqrt(eta[n]*omega[n]/mu/r_ul[n]) -
        v_l[n] / r_ul[n] -
        sqrt(gamma*pow(v_l[n], 2)/mu/v_e/r_ul[n]) -
        sqrt(beta*pow(v_l[n], 2)/r_ul[n]/r_dl[n])
    )
    t_dl_n = lambda n: xplus(
        sqrt(eta[n]*omega[n]*beta/mu/r_dl[n]) -
        sqrt(beta*pow(v_l[n], 2)/r_ul[n]/r_dl[n]) - 
        sqrt(gamma*beta*pow(v_l[n], 2)/mu/r_dl[n]/v_e) -
        beta*v_l[n]/r_dl[n]
    )
    t_e_n = lambda n: xplus(
        sqrt(eta[n]*omega[n]/mu/r_dl[n]) -
        sqrt(mu*pow(v_l[n], 2)/gamma/v_e/r_ul[n]) -
        v_l[n]/v_e -
        sqrt(mu*beta*pow(v_l[n], 2)/gamma/r_dl[n]/v_e)
    )
    t_ul = lambda : array([t_ul_n(i) for i in range(size)])
    t_dl = lambda : array([t_dl_n(i) for i in range(size)])
    t_e = lambda : array([t_e_n(i) for i in range(size)])
    delay = lambda ul, e, dl: omega/v_l*(1-1/(1 + v_l/ul/r_ul + v_l/e/v_e + beta*v_l/dl/r_dl))
    phi = lambda ul, e, dl: 0 if (sum(eta)<1) else max(delay(ul, e, dl))
    delta_eta = lambda ul, e, dl: delay(ul, e, dl) - phi(ul, e, dl)
    
    # gradient update loop
    for i in range(1, int(k)+1):
        ul = t_ul()
        dl = t_dl()
        e = t_e()
        mu_new = xplus(mu + step(i) * delta_mu(ul, dl))
        gamma_new = xplus(gamma + step(i) * delta_gamma(e))
        d_eta = delta_eta(ul, e, dl)
        eta_new = array([xplus(eta[j] + step(i) * d_eta[j]) for j in range(size)])
        if (norm(mu_new - mu) < delta and
            norm(gamma_new - gamma) < delta and
            norm(eta_new - eta) < delta
        ):
            break
        mu = mu_new
        gamma = gamma_new
        eta = eta_new

    # final delay time
    lamb = (1/t_ul()/r_ul + C/f_e + beta/t_dl()/r_dl)/(C/f_l + 1/t_ul()/r_ul + C/f_e + beta/t_dl()/r_dl)
    lamb = array([1 if isnan(i) else i for i in lamb])
    return dict(
        partial = max(lamb*omega*C/f_l),
        local = max(omega*C/f_l),
        edge = norm(omega/r_ul) * size + max(omega/v_e) + norm(omega/r_dl) * size,
        ul = t_ul(),
        dl = t_dl(),
    )

def multiple_run(run = 10, size = 10, f_e = 15e9):
    df = DataFrame(data = dict(
        edge = [0 for i in range(run)],
        local = [0 for i in range(run)],
        partial = [0 for i in range(run)]
    ))
    for i in range(run):
        cal = single_run(size=size, f_e=f_e)
        for j in df.columns:
            df.loc[i, j] = cal[j]
    return dict(
        partial = average(df['partial']),
        local = average(df['local']),
        edge = average(df['edge'])
    )