import re
from backend.basics import BaseObject

import json
from backend.signals import Event
from backend.keymanagement import encrypt, get_pub
from backend.asyncrun import run

class Session(BaseObject):
    def __init__(self, prog, data) -> None:
        super().__init__(prog)
        self.data = data
        self.privkey = self.data.get("privkey", False)

        if self.privkey: return
        run(self.prog.event(Event.NO_KEY, ""))


    async def maketoken(self):
        token = encrypt(self.privkey, get_pub(self.privkey), json.dumps(
            {
                "jid"          : self.prog.client.jid,
                "password"     : self.prog.client.password,
                "displayname"  : self.prog.client.displayname,
                "displaycolour": self.prog.client.displaycolour
            }
        ), self.pin) # store all XMPP data in encrypted form

        self.data.update(
        {
            "privkey": self.privkey, # making assumption privkey is pin protected
            "login_token": token
        })

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
        return cls.from_file(prog, prog.config.SESSION_FILE)

    async def save(self):
        with open(self.prog.config.SESSION_FILE, "w") as f:
            f.write(json.dumps(self.data))
    