from Crypto.PublicKey import RSA
from Crypto import Random
import secrets
from hashlib import sha256


def generate_seed(length=16):
    with open("backend/db/words.txt", "r") as f:
        words = f.read().strip().split("\n")

    out = []
    for i in range(length):
        out.append(secrets.choice(words))

    return out


class SeedRand:
    def __init__(self, seed):
        self.current = sha256(seed).digest()

    def gen(self, *args, **kwargs):
        while True:
            self.current = sha256(self.current).digest()
            q = 31
            while q != -1:
                yield chr(self.current[q]).encode()
                q -= 1

    def read(self, length):
        out = list()
        for i in range(length):
            out.append(next(self.gen()))
        return b"".join(out)[0: length]

    # Methods provided for backward compatibility only.
    def flush(self): pass
    def reinit(self): pass
    def close(self): pass

def generate_key(seed):
    key = RSA.generate(1024, SeedRand(("".join(seed)).encode()).read)
    return key.export_key().decode()


def id_from_priv(key):
    return id_from_pub(RSA.import_key(key).public_key().export_key())

def id_from_pub(key):
    return sha256(key).hexdigest()


if __name__ == "__main__":
    seed = generate_seed()
    seed1 = ['wine', 'smart', 'filter', 'jealous', 'coach', 'much', 'elegant', 'seminar', 'joke', 'usage', 'term', 'two', 'oppose', 'anxiety', 'language', 'core']
    print(seed)
    k = generate_key(seed)
    print(k)
    print(id_from_priv(k))
    # print(seed1)
    # print(generate_key(seed1))