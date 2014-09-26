import settings
from fabric.api import output


def load_config(kwargs):
    settings.settings.update(kwargs)
    output['stdout']= False    


def setting(key, origin=None):
    """return the setting for the given origin and the given key (if any)"""
    if origin is not None:
        return settings.settings[origin][key]
    return settings.settings[key]


def reverse(origin):
    if origin == "remote":
        return "local"
    if origin == "local":
        return "remote"


def is_local(origin):
    return origin == "local"


def is_remote(origin):
    return origin == "remote"
