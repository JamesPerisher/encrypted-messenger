from backend.basics import BaseObject

import json
from backend.signals import Event
from backend.keymanagement import encrypt, get_pub

class Session(BaseObject):
    def __init__(self, prog, data) -> None:
        super().__init__(prog)
        self.data = data

    async def maketoken(self):
        privkey = self.privkey
        token = encrypt(privkey, get_pub(privkey), json.dumps(
            {
                "jid"          : "",
                "password"     : "",
                "displayname"  :"",
                "displaycolour": ""
            }
        ))

    async def status(self):
        if self.data["active"]:
            await self.prog.event(Event.UNLOCK_PIN)
        else:
            await self.prog.event(Event.LOGIN)

    @classmethod
    def from_file(cls, prog, file):
        with open(file, "r") as f:
            try:
                return cls(prog, json.loads(f.read()))
            except json.decoder.JSONDecodeError:
                return cls(prog, prog.config.DEFAULT_SESSION)

    @classmethod
    def from_prog(cls, prog):
        return cls.from_file(prog, prog.config.CACHE_FILE)

    async def save(self, data=False):
        data = data if data else self.data
        with open(self.prog.config.CACHE_FILE, "w") as f:
            f.write(json.dumps(data))
    