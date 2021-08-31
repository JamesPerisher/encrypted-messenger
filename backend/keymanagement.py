from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import secrets
from hashlib import sha256
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode

import pgpy
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm


def generate_seed(length=16):
    with open("backend/db/words.txt", "r") as f:
        words = f.read().strip().split("\n")

    out = []
    for i in range(length):
        out.append(secrets.choice(words))

    return out


def generate_key(name="DefaultName", colour="#ff00ff"):
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)

    uid = pgpy.PGPUID.new(name, comment=colour)

    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])

    return str(key)

def id_from_priv(key):
    return id_from_pub(get_pub(key))

def id_from_pub(key):
    key, _ = pgpy.PGPKey.from_blob(key)
    return sha256(str(key.encrypt(pgpy.PGPMessage.new("id"))).encode()).hexdigest()
    # return sha256(key.fingerprint.encode()).hexdigest()

def get_pub(key):
    key, _ = pgpy.PGPKey.from_blob(key)
    return str(key.pubkey)

def sign(key, data):
    key, _ = pgpy.PGPKey.from_blob(key)
    h = sha256(data.encode()).hexdigest()

    return str(key.sign(h))

def verify(key, data, signature):
    key, _ = pgpy.PGPKey.from_blob(key)
    h = sha256(data.encode()).hexdigest()
    a = key.verify(h, pgpy.PGPSignature.from_blob(signature))
    return a.__bool__()

def encrypt(privkey, pubkey, data):
    privkey, _ = pgpy.PGPKey.from_blob(privkey)
    pubkey, _ = pgpy.PGPKey.from_blob(pubkey)

    msg = pgpy.PGPMessage.new(data)
    msg |= privkey.sign(msg)
    msg = pubkey.encrypt(msg)
    return str(msg)

    
def decrypt(privkey, pubkey, data):
    privkey, _ = pgpy.PGPKey.from_blob(privkey)
    pubkey, _ = pgpy.PGPKey.from_blob(pubkey)

    try:
        msg = privkey.decrypt(pgpy.PGPMessage.from_blob(data))
    except:
        return "Message decryption error."
    if not pubkey.verify(msg).__bool__(): return "Message authenticity error."
    return str(msg.message)

if __name__ == "__main__":
    key = generate_key("h23r2wegresr3rmm", "sergea23r23rhello")
    sig = sign(key, "testing")
    print(sig)
    print(verify(key, "testing", sig))

    a = encrypt(key, get_pub(key), "Hello World!!!")
    print(a)
    print(decrypt(key, get_pub(key), a))

    print(id_from_priv(key))