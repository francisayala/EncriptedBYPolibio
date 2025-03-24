from math import log2
from random import randint, randrange
import numpy as np

def miller_rabin_is_prime(n, k=None):
    if n < 3:
        raise ValueError
    if k is None:
        k = 2 * int(log2(n))
    t = n - 1
    s = 0
    while t % 2 == 0:
        s += 1
        t //= 2
    interrupted = False
    for i in range(k):
        interrupted = False
        a = randint(2, n - 2)
        x = pow(a, t, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = (x ** 2) % n
            if x == 1:
                return False
            if x == n - 1:
                interrupted = True
                break
        if interrupted:
            continue
        return False
    return True

def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num**0.5)+2, 2):
        if num % n == 0:
            return False
    return True

class PrimeTester:
    def __init__(self, max_prime=5000) -> None:
        self.precomputed = [i for i in range(2, max_prime) if is_prime(i)]

    def test(self, n) -> bool:
        if n < self.precomputed[-1]: 
            return all(n % prime != 0 for prime in self.precomputed) and miller_rabin_is_prime(n)
        else:  
            for prime in self.precomputed:
                if prime * prime > n:
                    break
                if n % prime == 0:
                    return False
            return miller_rabin_is_prime(n)

def generate_big_prime(digits):
    rand_number = randrange(10**(digits - 1), 10 ** digits - 10 ** (digits - 1))
    prime_tester = PrimeTester()
    while not prime_tester.test(rand_number):
        rand_number += 1
    return rand_number