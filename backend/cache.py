from backend.basics import BaseObject
from backend.keymanagement import decrypt, encrypt, get_pub



class Cache(BaseObject):
    @classmethod
    def from_prog(cls, prog):
        obj = cls.from_file(prog, prog.config.CACHE_FILE, prog.config.DEFAULT_CACHE)

        obj.data = decrypt(prog.session.privkey, get_pub(prog.session.privkey), obj.data, prog.session.pin)
        return obj

    def save(self):
        self._data = self.data
        self.data = encrypt(self.prog.session.privkey, get_pub(self.prog.session.privkey), self.data, self.prog.session.pin)

        ret = super().save(self.prog.config.CACHE_FILE)
        self.data = self._data

        del self._data # cleanup
        return ret




