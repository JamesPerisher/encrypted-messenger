
# Message routing config
AUTHORITIES = [("localhost", 6969)]

# Constants for messagemanagement
APPNAMELINK = "encrypted-msger" # need to import this from config
NEWWORD_A = "$A_NEW_RENDER_WORD_A$" # users migt be able to do some strange rendering with these but who cares
NEWWORD_B = "$B_NEW_RENDER_WORD_B$" # users migt be able to do some strange rendering with these but who cares
NEWWORD_FULL = "{}{}".format(NEWWORD_A, NEWWORD_B)


# Server config
BASE_SESSION = {
    "friends": {
        # can add a default friend here like a bot or a help account idfk
    }
}
BASE_CACHE = dict() # can add defualt cached items

DATABASE_URL = "sqlite+aiosqlite:///backend/db/database.db"
MAX_UNAME = 21

# Userdata config
USERDATA_PATH = "userdata"
SESSION_FILE  = "{}/session.json".format(USERDATA_PATH)
SESSION_CACHE = "{}/cache.json"  .format(USERDATA_PATH)


# Should technicaly be able to load themes for these settings

# Render config themes
BASE_IMAGE = "app/images/useraccountbase.png"
FONT = "LemonMilkMedium-mLZYV.otf"
DATE_FONT_SIZE = 11

# Render colour themes
SUPERBRIGHT       = "#000000"
DARK              = "#121212"
LIGHTBACKGROUND   = "#2E2E2E"
BACKGROUND        = "#3B3B3B"
BRIGHT            = "#787878"
BUTTONBACKGROUND  = "#aaaaaa"
SUPERDARK         = "#ffffff"

ERROR             = "#aa0000"
HEIGHLIGHT_COLOUR = "#064ca0"
APP_COLOUR        = "#290f47"
