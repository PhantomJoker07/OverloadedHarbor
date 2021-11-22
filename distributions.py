import math
from random import random
from scipy.stats import expon
from scipy.stats import norm


# METHODS #

def exponential_distr (lamda, N = 1, use_scipy = False):    
   
    #Using the inverse of the CDF
    if not use_scipy:
        ans = []
        for i in range (0,N):
            ans.append(-(1 / lamda) * math.log(random()))
        if N == 1: return ans [0]
        return ans
    
    # Using scipy
    else:
        if N == 1: return expon.rvs(scale = 1/lamda, size = 1)[0]
        else: return expon.rvs(scale = 1/lamda, size = N)


def normal_distr (O_2 = 1, u_ = 0, use_scipy = False):   
   
    #Box-Muller
    u1 = random()
    u2 = random()
    _std = math.sqrt(O_2)
    if not use_scipy:
        sample = abs(math.cos((2*math.pi*u1)*math.sqrt(2*math.log(1/u2))))
        return sample / _std + u_
   
    # Using scipy
    else:
        return abs(norm.rvs(loc = u_, scale = _std)) 