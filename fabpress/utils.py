import settings
from fabric.api import output


def load_config(kwargs):
    settings.settings.update(kwargs)
    output['stdout']= False    


def setting(key, origin=None, default=None):
    """return the setting for the given origin and the given key (if any)"""
    if origin is not None:
        try:
            return settings.settings[origin][key]
        except KeyError:
            return default
    return settings.settings.get(key, default)


def reverse(origin):
    if origin == "remote":
        return "local"
    if origin == "local":
        return "remote"


def is_local(origin):
    return origin == "local"


def is_remote(origin):
    return origin == "remote"
