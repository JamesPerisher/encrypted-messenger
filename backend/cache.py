from backend.basics import BaseObject
from backend.keymanagement import decrypt, encrypt, get_pub
from backend.config import Config
import json

class Cache(BaseObject):
    @classmethod
    def from_prog(cls, prog):
        obj = cls.from_file(prog, Config.CACHE_FILE, Config.DEFAULT_CACHE)
        return obj

    @classmethod
    def from_file(cls, prog, filename, default):
        obj = cls(prog)
        try:
            with open(filename, "r") as f:
                obj.data = decrypt(prog.session.privkey, get_pub(prog.session.privkey), json.loads(f.read()), prog.session.pin)
        except:
            obj.data = default
        return obj

    async def save(self):
        with open(Config.CACHE_FILE, "w") as f:
            f.write(json.dumps(encrypt(self.prog.session.privkey, get_pub(self.prog.session.privkey), self.data, self.prog.session.pin)))

    def __getitem__(self, jid):
        ret = self.data.get(jid, False)
        if not ret: self.data[jid] = str()
        return self.data[jid]

    def __setitem__(self, jid, value):
        self.data[jid] = value