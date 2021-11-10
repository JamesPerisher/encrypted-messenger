from backend.basics import BaseObject

import json
from backend.signals import Event
from backend.keymanagement import encrypt, get_pub
from backend.asyncrun import run
from backend.config import Config

class Session(BaseObject):
    def __init__(self, prog, data) -> None:
        super().__init__(prog, data)
        try:
            self.privkey = self.data.get("privkey", False)
        except AttributeError:
            run(self.prog.event(Event.NO_KEY, ""))
            return

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
        try:
            if self.data["active"]:
                return await self.prog.event(Event.UNLOCK_PIN)
            else:
                return await self.prog.event(Event.LOGIN)
        except TypeError:
            return await self.prog.event(Event.LOGIN)


    async def get_key(self, jid, default="xyz"):
        a = self.data["friends"].get(jid, default)
        if a == "xyz":
            return self.data["friends"]["empty"]
        return a

    @classmethod
    def from_prog(cls, prog):
        return cls.from_file(prog, Config.SESSION_FILE, Config.DEFAULT_SESSION)
    def save(self): return super().save(Config.SESSION_FILE)

    async def logout(self):
        self.data = None
        self.prog.cache.data = None
        self.prog.cache.save()
        await self.save()

        self.prog.on_request_close(None)
    