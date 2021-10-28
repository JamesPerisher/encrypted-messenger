from backend.basics import BaseObject
from backend.keymanagement import decrypt, encrypt, get_pub
from backend.config import Config


class Cache(BaseObject):
    @classmethod
    def from_prog(cls, prog):
        obj = cls.from_file(prog, Config.CACHE_FILE, Config.DEFAULT_CACHE)

        obj.data = decrypt(prog.session.privkey, get_pub(prog.session.privkey), obj.data, prog.session.pin)
        return obj

    def save(self):
        self._data = self.data
        self.data = encrypt(self.prog.session.privkey, get_pub(self.prog.session.privkey), self.data, self.prog.session.pin)

        ret = super().save(self.Config.CACHE_FILE)
        self.data = self._data

        del self._data # cleanup
        return ret

    def __getitem__(self, jid):
        ret = self.data.get(jid, False)
        if not ret: self.data[jid] = str()
        return self.data[jid]

    def __setitem__(self, jid, value):
        self.data[jid] = value