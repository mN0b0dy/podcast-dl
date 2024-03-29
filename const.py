import os
import sys

KEY_IMAGE = "itunes:image"
KEY_NAME = "itunes:name"
KEY_OWNER = "itunes:owner"
KEY_AUTHOR = "itunes:author"
KEY_CATEGORY = "itunes:category"

# Item
KEY_TITLE = "itunes:title"
KEY_EPISODE_NO = "itunes:episode"
KEY_EPISODE_TYPE = "itunes:episodeType"
KEY_DURATION = "itunes:duration"

def minutes(seconds):
    seconds = str(seconds).strip()
    if ":" in seconds:
        seconds = seconds.split(":")
        if seconds.count(":") == 2:
            return f'{seconds[1]} min'
        else:
            # count==3?
            return f'{seconds[2]} min'
    return f'{int(int(seconds)/60)} min'

import inspect
def abortif(estr, num=40):
    frame = inspect.currentframe()
    locals = frame.f_back.f_locals
    if (eval(estr, globals(), locals) == True):
        print(f"abortif: {estr}")
        print("[x] Unsupported rss feed.")
        sys.exit(num+1)
