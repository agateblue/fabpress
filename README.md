


# Requirements

- Python 2.7 (on locale machine)
- [Fabric](http://docs.fabfile.org) for managing connexion to server and calling commands (on locale machine)
- [WP-CLI](http://wp-cli.org/) for dealing with most of the Wordpress stuff (on both locale and remote machines)
- A Linux system (fabpress was developped and tested on Archlinux and Debian Wheezy) (on both locale and remote machines)

Please install wp-cli on both local and remote server before going any further.


# Configuration

If you want to enable .htaccess generation, please follow the instructions from [here](http://wp-cli.org/commands/rewrite/flush/) and [here](http://wp-cli.org/config/). If you don't do this, after mirroring a Wordpress installation, you'll have to log into your mirrored installation and save permalinks manually.

# Roadmap :

- adding theme synchronisation

# Limitations

- for some reasons, when mirroring a Wordpress installation for the first time, you'll have to manually save the permalinks from the admin, in order to load Custom Posts Types permalinks. Else, accessing a CPT detail page would raise a 404.