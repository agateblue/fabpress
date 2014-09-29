#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabpress.utils import load_config
from fabric.api import env

# Domain or ip of your production server, where you will log via SSH
# You can append the SSH port it your SSh server run on a non standard port:
# env.hosts = ['mydomain.com:800']

env.hosts = ['mydomain.com']

# The account that will be used to log on host via SSH
env.user = 'eliotberriot'

# Configuration relative to your remote (production) Wordpress instance
remote = {
    # path to your remote wordpress directory (where wp-config.php is stored)
    "path": "/path/to/your/wordpress/install", 

    # Path where database dumps will be stored
    "dumps_path": "/path/to/db/dumps",

    # The url of your remote Wordpress instance
    "url":"mysite.com",

    # Hooks that may be triggered when you run some tasks on remote. 
    # Please refer to documentation for in-depth explanation
    "hooks": {
        # your hooks here
    },

    # the path to your remote wp-cli executable. Ensure you have permission to execute it
    "wp-cli": "wp"
}

# Same as remote, but for your local (development) Wordpress instance
local = {
    # path to your local wordpress directory (where wp-config.php is stored)
    "path": "/path/to/your/wordpress/install", 

    # Path where database dumps will be stored
    "dumps_path": "/path/to/db/dumps",

    # The url of your local Wordpress instance
    "url":"localhost/mysite",

    # Hooks that may be triggered when you run some tasks on local. 
    # Please refer to documentation for in-depth explanation
    "hooks": {
        # your hooks here
    },

    # the path to your remote wp-cli executable. Ensure you have permission to execute it
    "wp-cli": "wp"
}

# A list of theme names you want to skip when syncing themes
# Useful if you are developping your own theme and do not want 
# fabpress trying to download this one from wordpress.org

# skip_themes = ['theme_name']
skip_themes = []

# A list of plugin names you want to skip when syncing plugins
# Useful if you are developping your own plugin and do not want 
# fabpress trying to download this one from wordpress.org

# skip_plugins = ['plugin_name']
skip_plugins = []


# Do not touch this
fabpress_settings = {
    "remote": remote,
    "local": local,    
    "skip_plugins": skip_plugins,
    "skip_themes": skip_themes,
}

# Do not touch this either
load_config(fabpress_settings)