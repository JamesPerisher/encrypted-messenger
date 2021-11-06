import asyncio
from re import L
from backend.basics import BaseObject
from backend.signals import Event, Packet
from backend.asyncrun import run

import slixmpp
import logging
logging.basicConfig(level=logging.INFO) # update config


def connected(func):
    def f(self, *args, **kwargs):
        try:
            if self.xmpp.is_connected():
                return func(self, *args, **kwargs)
        except AttributeError:
            pass
        return False
    return f

class Client(BaseObject):
    xmpp = None
    _displayname = ""
    _displaycolour = "#ff0ff"
    _jid = ""
    _password = ""
    _active = asyncio.Event()

    @property
    def displayname(self):
        return self._displayname
    @displayname.setter
    def displayname(self, value):
        self._displayname = value
        self._active.set()
    @property
    def displaycolour(self):
        return self._displaycolour
    @displaycolour.setter
    def displaycolour(self, value):
        self._displaycolour = value
        self._active.set()

    @property
    def nick(self):
        return "{}-{}".format(self.displayname, self.displaycolour)

    @property
    def jid(self):
        return self._jid
    @jid.setter
    def jid(self, value):
        self._jid = value
        self._active.set()

    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
        self._active.set()

    @connected
    async def update_roster(self, item, *args, **kwargs):
        return self.xmpp.update_roster(item)

    @connected
    def get_contacts(self):
        return self.xmpp.get_contacts()

    @connected
    async def send(self, tojid, packet):
        return await self.xmpp.sendmsg(tojid, packet.read())

    async def msgevent(self, fromjid, data):
        pass

    async def start(self):
        while True:
            await self._active.wait()
            self._active.clear()

            self.xmpp = XMPPClient(self.prog, self.jid, self.password)
            self.xmpp.msgevent = self.msgevent
            await self.xmpp.setnick(self.nick)
            self.xmpp.connect()

class XMPPClient(slixmpp.ClientXMPP, BaseObject):
    def __init__(self, prog, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        BaseObject.__init__(self, prog)

        self.register_plugin('xep_0172') # nicknames

        self.add_event_handler("session_start"    , self.session_start)
        self.add_event_handler("message"          , self.message)
        self.add_event_handler("failed_auth"      , self.autherror)
        self.add_event_handler("connection_failed", self.neterror)
        self.add_event_handler("disconnected"     , self.dcerr)

    async def sendmsg(self, tojid, data):
        self.send_message(tojid, data)

    async def setnick(self, nick):
        self.nick = nick
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
            await self.msgevent(msg['from'], Packet.from_raw(msg['body']))

    async def session_start(self, event):
        await self.prog.event(Event.LOGGED_IN , event)
        self.send_presence(pnick=self.nick)

    async def get_contacts(self):
        await self.get_roster()
        return self.roster[self.jid]
    
    async def loggout(self):
        self.disconnect() # logout

    def start(self):
        self.connect()
        self.process(forever=True) # uses asyncio.get_eventloop then starts the loop fucking dickheads