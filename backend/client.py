from backend.basics import BaseObject
from backend.signals import Event

import slixmpp
import logging
import json

logging.basicConfig(level=logging.INFO) # update config


class XMPPClient(slixmpp.ClientXMPP, BaseObject):
    def __init__(self, prog, jid, password, name, colour):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        BaseObject.__init__(self, prog)

        self.name = name
        self.colour = colour

        self.register_plugin('xep_0172') # nicknames

        self.add_event_handler("session_start"    , self.session_start)
        self.add_event_handler("message"          , self.message)
        self.add_event_handler("failed_auth"      , self.autherror)
        self.add_event_handler("connection_failed", self.neterror)
        self.add_event_handler("disconnected"     , self.dcerr)

    @classmethod
    def from_file(cls, prog, file):
        with open(file, "r") as f:
            try:
                data = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                data = prog.config.DEFAULT_XMPP
            return cls(prog, data["jid"], prog.crypto.get_password(), data["name"], data["colour"])

    @classmethod
    def from_prog(cls, prog):
        return cls.from_file(prog, prog.config.XMPPDATA_FILE)

    async def sendmsg(self, tojid, data):
        self.send_message(tojid, data)

    @property
    def nick(self):
        return "{}-{}".format(self.name, self.colour)

    async def setName(self, name=None, colour=None):
        self.name   = name   if name else self.name
        self.colour = colour if colour else self.colour
        self.plugin['xep_0172'].publish_nick(self.nick) # update on server

    async def msgevent(self, fromjid, data):
        pass # overide this in the handler
    
    async def autherror(self, event):
        await self.prog.event(Event.AUTH_ERROR, event)

    async def neterror(self, event):
        await self.prog.event(Event.NET_ERROR , event)

    async def dcerr(self, event):
        await self.prog.event(Event.DISCONNECTED , event)

    async def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            await self.msgevent(msg['from'], msg['body'])

    async def session_start(self, event):
        await self.prog.event(Event.LOGGED_IN , event)
        self.send_presence(pnick=self.nick)

    async def get_contacts(self):
        return await self.get_roster() # gets contacts TODO: some nice formatting
    
    async def loggout(self):
        self.disconnect() # logout

    def start(self):
        self.connect()
        self.process(forever=True) # uses asyncio.get_eventloop then starts the loop fucking dickheads