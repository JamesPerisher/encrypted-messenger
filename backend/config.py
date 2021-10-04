from backend.basics import BaseObject


class Config(BaseObject):

    USERDATA_DIR = "userdata"

    CACHE_FILE    = "{}/cache.json".format(USERDATA_DIR)
    PRIV_KEY      = "{}/privkey.pem".format(USERDATA_DIR)
    XMPPDATA_FILE = "{}/xmpdata.json".format(USERDATA_DIR)

    DEFAULT_CACHE = {}
    DEFAULT_XMPP  = {"jid":None, "name":None, "colour":None}