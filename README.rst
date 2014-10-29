Note: fabpress is in early development, use with caution

If you want to developp locally with Wordpress, you usually have to follow these steps: 

- install a local copy of Wordpress
- import your production MySQL database
- search and replace permalinks in database (``http://mysite.com`` to ``http://localhost/dev/mysite``)
- install all your plugins and themes with correct versions
- download media files

Then, each time there is a change on production website and you need to pull these changes, you have to go through the same steps. And the same thing happens if you want to deploy your local website in production.

Going through these steps by hand is a nightmare and this is why I wrote fabpress: I wanted a command-line tool that would let me mirror a Wordpress installation via a single command.

What is fabpress ?
==================

- a bunch of scripts, written in Python on top of `Fabric <http://www.fabfile.org/>`_ and `WP-CLI <http://wp-cli.org/>`_, two awesome tools
- a way to pull/push database, media files, themes, plugins from/to your production wordpress website
- a command-line tool, tested on ArchLinux and Debian, that could probably work on Mac OS and other Linux distributions
- free (as in free speech and free beer), open-source, licensed under BSD

What is *not* fabpress ?
========================

- production-ready. I use it on my projects, and it works. There is absolutely no warranty it will work for you, with your setup. **Before trying it, please, backup your data**. I mean it, seriously.

Requirements
============

On local machine
****************

- Python 2.7
- Fabric for managing connexion to server and calling commands

On remote machine
*****************

- SSH access

On both
*******

- `WP-CLI <http://wp-cli.org/>`_ for dealing with most of the Wordpress stuff
- A Linux system (fabpress was developped and tested on Archlinux and Debian Wheezy)

Installation
============

Recommanded installation procedure requires `pip <http://pip.readthedocs.org/en/latest/installing.html>`_, but you can also use ``easy_install``. Please install pip before continuing.

Fabric
******

Install Fabric your local machine::

    sudo pip install fabric

WP-CLI
******

Follow the procedure detailed on `WP-CLI <http://wp-cli.org/>`_ website, on your local and production machines.

Fabpress
********

Fabpress is available on `PyPi <https://pypi.python.org/pypi/fabpress>`_. Install it on your local machine::

    pip install fabpress --user

This method will also download and install Fabric    

Configuration
=============

First, move into your project directory::

    cd /home/user/projects/mysite

Create a ``fabfile.py`` file::

    echo 'from fabpress import tasks as fp' >> fabfile.py

Then, generate a config file::
    
    fab fp.config.create

This will create a ``fab_settings.py`` file in your project directory. Fell free to add it to your VCS ignored files.

You can now edit the file (it is heavily commented)::

    nano fab_settings.py

Import your settings in your ``fabfile.py``::
    
    echo "import fab_settings" >> fabfile.py    

After that, well, you're almost good to go. Remember to create a MySQL database for your local instance.

A bit of theory
===============

Tasks
*****

A task is an action you can run from command line, using the following notation::

    fab command:argument1=value,argument2="value"

    # Quotes and arguments name are not mandatory
    fab command:value1,value2

    # Some tasks just don't need arguments
    fab command

You can list available commands via ``fab -l`` and get additionnal informations about a fabpress task, with ``fab fp.<command_name>:help``.

Targets
*******

In fabpress, many tasks can be run independantly on remote or local Wordpress instance. For exemple, take the following tasks::

    fab fp.db.sync:local
    fab fp.db.sync:remote

The first one will create a backup of your remote database, download it and import it into your local wordpress instance. The second one will do the opposite: backup your local database, upload it and import it into your remote instance.

When a task require a target argument, which value can be either ``remote`` or ``local``, it usually means data (database, media files, plugins, themes...) will be imported INTO your target wordpress instance. Some tasks do not import data, but still require a target: ``fab fp.db.reset:<target>`` will reset all database tables of targeted installation. 

Note that fabpress help and documentation sometimes mentions ``origin``. This term is a shortcut for designating the opposite of a target. With the following command ``fab.main.sync:local`` your target is ``local``, and ``origin`` is your remote installation, from where data will be imported. 

If you run ``fab.main.sync:remote``, ``origin`` designate your local Wordpress instance.

Example workflow
================

First, we move to our project directory::

    cd /home/user/projects/mysite

Let's mirror the production website, so we can use it locally::

    fab fp.main.mirror:local

    # typical output

    This is an important choice. Do you want to continue ? [y/N] y
    Running main.mirror [on local]...
        Running base.collect_data [on remote]...
        Running main.download [on local]...
            Changing permissions of /var/www/mysite to 770
            wp-config.php was copied from sample. Do you want to edit it ? [Y/n] y
            Edit your file located at /var/www/mysite/wp-config.php then relaunch this command

    fab fp.main.mirror:local
    This is an important choice. Do you want to continue ? [y/N] y

    Existing wp-config.php file found
        Running main.sync [on local]...
            Syncing databases (from remote to local)
                Running db.export [on remote]...
                Running db.import [on local]...
                    Creating a safety backup of local database, juste in case
                    Downloading backup from remote
                    Importing backup.sql into local database...
                    Deleting useless SQL backups...
            Running db.fix_permalinks [on local]...
                Updating URL(s) from mysite.com to localhost/mysite...
            Running theme.sync [on local]...
                Skipping theme blast: it is listed in ignored_themes
            Running plugin.sync [on local]...
                Running media.sync [on local]...
            Syncing media files from remote to local (please, be patient, this may take some time)
    Done.


We can now open ``http://localhost/mysite`` with any web browser, and browse the local copy of our production website.
If you encounter 404 errors, login at ``http://localhost/mysite/wp-admin`` and update your permalinks (Settings > Permalinks). You should not have to do it again after that.

Then, it's time to work. We install themes, plugins, create new pages and posts, import media files...

When we're done and want to push your local changes in production, we just run::

    fab fp.main.push

Later, if we want to import changes from production::

    fab fp.main.pull

Hooks
=====

Sometimes, you want to do something when a task is run. For example, pulling from your theme's Git repository when you run ``fp.theme.sync`` on your remote installation. Hooks are here for that::

    # hooks.py (create this in the same directory as your fab_settings.py)

    from fabric.api import run, cd
    def pull_theme():
        with cd("/var/www/mysite/wp-content/themes/mytheme"):
            run("git pull")


    # fab_settings.py

    import hooks

    remote = {

        # ...

        "hooks": {
            "theme.sync": hooks.pull_theme
        },
    }

Available tasks
===============

Output from ``fab -l``::
    
    fp.config.create         Create a config file from fabpress sample
    fp.db.clear_backups      Remove backup files on target
    fp.db.export             Export the database from target installation to the given path
    fp.db.fix_permalinks     Search and replace all occurence of origin domain with target domain
    fp.db.import             Import the database dump at origin path to the target
    fp.db.reset              Delete all tables in target database
    fp.db.sync               Sync target database with origin, replacing origin permalinks with target permalinks
    fp.fs.drop               Remove all files of target, including target directory
    fp.main.download         Download at target a copy of origin Wordpress files (version and languages preserved)
    fp.main.drop             Delete target files and database. Will also delete the installation parent directory.
    fp.main.help             Get some help
    fp.main.mirror           Create at target an exact mirror of origin wordpress installation
    fp.main.pull             Sync database, themes, plugins and media files from remote to local installation
    fp.main.push             Sync database, themes, plugins and media files from local to remote installation
    fp.main.sync             Pull origin database, themes, plugins and media files to target
    fp.main.wp               Run a wp-cli command on the target. You don't need to prefix it with 'wp', it will be added automatically
    fp.media.sync            Download origin media files to target
    fp.plugin.sync           Download and activate origin plugins on target
    fp.theme.sync            Download and activate origin themes on target

Limitations
===========

- For some reasons, when mirroring a Wordpress installation for the first time, you'll have to manually save the permalinks from the admin, in order to load Custom Posts Types permalinks. Else, accessing a CPT detail page would raise a 404.
- Will only download Themes and Plugins that are available on wordpress.org.


To-do list
==========

- sync wordpress versions
- add support for more than two targets

Changes
=======

0.1.1 - 29/10/2014:
*****************
- Syncing DB now clear transients, which should fix some URL issues with plugins (such as Polylang)

0.1 - 29/09/2014:
*****************
- initial release

Contribute
==========

Contributions, bug reports, and "thank you" are welcomed. Feel free to contact me at <contact@eliotberriot.com>.

License
=======

The project is licensed under BSD licence.
