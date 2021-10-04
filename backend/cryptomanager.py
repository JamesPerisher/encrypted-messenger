from backend.basics import BaseObject
from backend.signals import Event


class CryptoManager(BaseObject):
    def __init__(self, prog, raw_privkey) -> None:
        super().__init__(prog)
        self.raw_privkey = raw_privkey

    @property
    def public(self):
        return "pub"
    @classmethod
    def from_file(cls, prog, file):
        with open(file, "r") as f:
            return cls(prog, f.read())
    @classmethod
    def from_prog(cls, prog):
        return cls.from_file(prog, prog.config.PRIV_KEY)

    
    def get_password(self):
        print("password")
        return "privkeybasedpassword"

    async def encrypt(self, pubkey, data):
        # make msg
        # sign
        # encrypt
        return "encryted mess of ({}) by ({})".format(data, pubkey)
