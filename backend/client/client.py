from backend.asyncutils import run_async
from backend.p2p.p2p_utils import Address, Id
from backend.p2p.p2p_client import AsyncConnection
from pgpy import PGPKey, PGPUID
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm
import os

from backend.packet import PACKET_TYPE, Packet



# key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
# uid = PGPUID.new('Abraham Lincoln', comment='Honest Abe', email='abraham.lincoln@whitehouse.gov')
# key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
#             hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
#             ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
#             compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
# s = key.sign(b"hello")
# s = key.sign(b"hellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohello")
# print(s)


def generate_challenge(): # might have to do some data mashing to make struct happy idk should be fine
    return os.urandom(32)


class User:
    def __init__(self, id: Id, key) -> None:
        self.id = id
        self.key = key
    def __repr__(self) -> str:
        return f"User({self.id})"
    def __hash__(self) -> int:
        return self.id.__hash__()
    def __eq__(self, other: object) -> bool:
        return self.id == other.id
    def __ne__(self, other: object) -> bool:
        return self.id != other.id

    def haskey(self):
        return isinstance(self.key, PGPKey)

    async def ping(self, pac, conn): # pong
        await conn.send(Packet(PACKET_TYPE.PING, "PONG!!!"))

    async def handle(self, me): # to be called each time we want to sync data #TODO: implement lock
        # handles all incoming packets
        conn = AsyncConnection.from_id(me.id, self.id, me.mediator)
        while conn.object.keepalive:
            pac = await conn.recv() # get the next packet from the connection

            await { # python switch statement dodgyness
                PACKET_TYPE.PING: self.ping,
            }[pac.type](pac, conn)
        

    @classmethod
    def from_string(cls, string: str, key=None) -> 'User':
        return cls(Id.from_string(string), None)

class Client(User):
    def __init__(self, name: str, id: Id, friends: list, key: PGPKey, pin, mediator) -> None:
        super().__init__(id, key)
        self.friends = friends
        self.key = key
        self.pin = pin
        self.mediator = mediator

    @classmethod
    def from_dict(cls, data: dict, pin: str):
        return cls(data['name'], Id(data['id']), [User.from_string(x) for x in data['friends']], PGPKey.from_blob(data['key']), pin, Address(data['mediator']['ip'], data['mediator']['port']) )

    async def message(self, message: str, to: User):
        pass
        


def main():
    key = '-----BEGIN PGP PRIVATE KEY BLOCK-----\n\n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\n=Rf7B\n-----END PGP PRIVATE KEY BLOCK-----\n'
    c = Client.from_dict({'name':'bob', 'id': 'test', 'friends': ['test2'], 'key': key, 'mediator':{'ip':"test", 'port':1234}}, '1234')
    print(c)