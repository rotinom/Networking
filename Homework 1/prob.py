#!/usr/bin/python

from math import *
import sys

def choose(n, k):
    return factorial(n) / (factorial(k) * (factorial(n-k)))

def binomial(n, k, p):
    return choose(n, k) * pow(p, k) * pow((1-p), n-k)

def prob_k_transmitting(n, k, p):
    total = 0.0
    for i in xrange(0, k):
        b = binomial(n, i, p)
        total += b

    return 1.0 - total


def p_specific_user(n, p):
    p_others = pow((1-p), n-1)
    return p * p_others

def p_any_user(p_specific, n, p):
    return p_specific * n

def main():

    n, k, p = sys.argv[1:]
    n = int(n)
    k = int(k)
    p = float(p)

    p_specific =  p_specific_user(n, p)
    print "Probability that one user is transmitting: %8.8f" % p_specific

    p_any = p_any_user(p_specific, n, p)
    print "Probability that any user is transmitting: %8.8f" % p_any


    n_xmit = prob_k_transmitting(n, k, p)



    print "Probability any %i of %i are transmitting: %f" % (k, n, n_xmit)

if __name__ == "__main__":
    main()