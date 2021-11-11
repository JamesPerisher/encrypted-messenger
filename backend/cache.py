import json

from backend.config import Config
from backend.basics import BaseObject
from backend.asyncrun import asyncrun
from backend.keymanagement import decrypt, encrypt, get_pub

# Message cache stors messages on the local device encrypted
class Cache(BaseObject):
    # overite super function to decrypty data
    @classmethod
    def from_prog(cls, prog):
        obj = cls.from_file(prog, Config.CACHE_FILE, Config.DEFAULT_CACHE)
        return obj

    # overite super function to decrypty data
    @classmethod
    def from_file(cls, prog, filename, default):
        obj = cls(prog)
        try:
            with open(filename, "r") as f:
                obj.data = json.loads(decrypt(prog.session.privkey, get_pub(prog.session.privkey), f.read(), prog.session.pin))
        except:
            obj.data = default
        return obj

    # overite super function to encrypt data
    @asyncrun
    async def save(self): # save data when possible
        with open(Config.CACHE_FILE, "w") as f:
            f.write(encrypt(self.prog.session.privkey, get_pub(self.prog.session.privkey), json.dumps(self.data), self.prog.session.pin))

    # get data from chahe
    def __getitem__(self, jid):
        ret = self.data.get(jid, False)
        if not ret: self.data[jid] = str()
        return self.data[jid]
    # set chache value
    def __setitem__(self, jid, value):
        self.data[jid] = value
    # get with default getter
    def get(self, jid, default=None):
        return self.data.get(jid, default)