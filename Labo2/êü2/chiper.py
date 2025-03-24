from random import randrange, choice
from primes import generate_big_prime
from math import gcd, log2, ceil


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def generate_keys(n_len):
    p = generate_big_prime(n_len // 2)
    q = generate_big_prime(n_len // 2)
    n = p * q
    d = (p - 1) * (q - 1)
    s = randrange(1, d)
    while gcd(s, d) != 1: 
        s = randrange(1, d)
    e = modinv(s, d)
    return (s, n), (e, n)


def encrypt(pk, message):
    s, n = pk    
    symbols = ceil(log2(n)) // 8
    splits_count = len(message) // symbols + (1 if len(message) % symbols else 0)
    cipher = []
    message += ''.join([choice(message) for i in range(splits_count * symbols - len(message))])
    for i in range(splits_count):
        curr_split = message[i * symbols:(i + 1) * symbols]
        byte_string = bytes(curr_split, encoding='ascii')
        converted = int.from_bytes(byte_string, 'little')
        cipher.append(pow(converted, s, n))
    return ' '.join(map(str, cipher))
    


def decrypt(pk, cipher):
    e, n = pk
    symbols = ceil(log2(n)) // 8
    result = []
    for x in cipher.split(' '):
        x = pow(int(x), e, n)
        byte_string = x.to_bytes(symbols, 'little')
        result.append(byte_string.decode('ascii'))
    return ''.join(result)
  