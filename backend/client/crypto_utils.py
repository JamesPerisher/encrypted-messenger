from pgpy import PGPKey, PGPUID
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm
import os
from backend.p2p.p2p_utils import Address, Id


# makes a key with the given name, email, pin, and prefered mediator
def generate_key(name: str, id: Id, mediator: Address, pin: str, comment="We love Kryptos!") -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096) # why so big dammmn
    uid = PGPUID.new(name, comment=comment, email=f"{id.get()}@{mediator.ip}:{mediator.port}")
    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
    key.protect(pin, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256) # secure as shit baby!
    return key

# is hard coded for now # TODO: make this better from config file or some shit
def generate_mediator() -> Address:
    return Address("iniver.net", 7788)

# returns None if the key does not exist
def noneretrun(func):
    def wrapper(key):
        if key is None:
            return None
        return func(key)
    return wrapper

# extracts the id from the key
@noneretrun
def getid(key: PGPKey) -> Id:
    return Id(key.pubkey.uid.email.split('@')[0])

# make an id from random shit
def make_id(key=None): # lets hope we dont have any collisions
    return Id.from_string(os.urandom(64).hex()+str(key))

# extracts the name from the key
@noneretrun
def getname(key: PGPKey) -> str:
    return key.pubkey.uid.name

# extracts the mediator from the key
@noneretrun
def getmediator(key: PGPKey) -> Address: # TODO: idiot handling to prevent errors
    ip,port = key.pubkey.uid.email.split('@')[1].split(':')
    return Address(ip, int(port))

# notes:
# s = key.sign(b"hello")
# s = key.sign(b"hellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohello")
# print(s)

# make a challenge for crypto packets
def generate_challenge(): # might have to do some data mashing to make struct (Packet) happy idk should be fine
    return os.urandom(32) # should probably load bytes length from a file
