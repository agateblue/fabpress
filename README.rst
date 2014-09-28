
Why ?
=====

If you want to developp locally with Wordpress, you usually have to follow these steps: 

- install a local copy of Wordpress
- import your production MySQL database
- search and replace permalinks in database (`http://mysite.com` to `localhost/dev/mysite`)
- install all your plugins and themes with correct versions
- download media files

Then, each time there is a change on production website and you need to pull these changes, you have to go through the same steps. And the same thing happens if you want to deploy your local website in production.

Going through these steps is a nightmare and this is why I wrote fabpress: I wanted a command-line tool that would let me mirror a Wordpress installation via a single command.


What is fabpress ?
==================

- a bunch of scripts, written in Python on top of Fabric and WP-CLI, two awesome tools
- a way to pull/push database, media files, themes, plugins from/to your production wordpress website
- a command-line tool, tested on ArchLinux and Debian, that could probably work on Mac OS and other Linux distributions
- free (as in free speech and free beer), open-source, licensed under BSD


What is NOT fabpress ?
======================

- production-ready. I use it on my projects, and it works. There is absolutely no warranty it will work for you, with your setup. Before trying it, please, create backups of your data. I mean it, seriously.


Requirements
============

On local machine
****************

- Python 2.7
- Fabric_ for managing connexion to server and calling commands
- WP-CLI_ for dealing with most of the Wordpress stuff

On remote machine
*****************

- SSH access

On both
*******

- WP-CLI_ for dealing with most of the Wordpress stuff
- A Linux system (fabpress was developped and tested on Archlinux and Debian Wheezy)

Use case
========

For easier explanation, I will assume you have a production Wordpress instance, at URL `http://site.com`. This website works fine, but you need to replace the current theme with your own theme, named `blast`. You want to develop and test this theme locally, on your computer before deploying it on your production website.

Your themes files are located on your computer at `/home/user/projects/blast`, and you've created a directory for your local Wordpress instance at `/var/www/site.com`.

Configuration
=============

First, move into your project directory::

    cd /home/user/projects/blast

Create a file `fabfile.py` in your project directory::

    echo 'from fabpress import tasks as fp' >> /home/user/projects/blast/fabfile.py

Then, generate a config file::
    
    fab fp.config.create

This will create a `fab_settings.py` file in your project directory. Fell free to add it to your VCS ignored files.

After that, you can edit the file (it is heavily commented)::

    nano fab_settings.py

After that, well, you're almost good to go.

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

You can list available commands via `fab -l` and get additionnal informations about a fabpress task, with `fab fp.<command_name>:help`.

Targets
*******

In fabpress, many tasks can be run independantly on remote or local Wordpress instance. For exemple, take the following tasks::

    fab fp.db.sync:local
    fab fp.db.sync:remote

The first one will create a backup of your remote database, download it and import it into your local wordpress instance. The second one will do the opposite: backup your local database, upload it and import it into your remote instance.

When a task require a target argument, which value can be either `remote` or `local`, it usually means data (database, media files, plugins, themes...) will be imported INTO your target wordpress instance. Some tasks do not import data, but still require a target: `fab fp.db.reset:<target>` will reset all database tables of targeted installation. 

Note that fabpress help and documentation sometimes mentions `origin`. This term is a shortcut for designating the opposite of a target. With the following command `fab.main.sync:local` your target is `local`, and `origin` is your remote installation, from where data will be imported. 

If you run `fab.main.sync:remote`, `origin` designate your local Wordpress instance.


Available tasks
===============

Output from `fab -l`::
    
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

- for some reasons, when mirroring a Wordpress installation for the first time, you'll have to manually save the permalinks from the admin, in order to load Custom Posts Types permalinks. Else, accessing a CPT detail page would raise a 404.
- Will only download Themes and Plugins available on wordpress.org

Contribute
==========

Contributions, bug reports, and "thank you" are welcomed. Feel free to contact me at <contact@eliotberriot.com>.

License
=======

The project is licensed under BSD licence.

Links
=====

.. _Fabric: http://docs.fabfile.org
.. _WP-CLI: http://wp-cli.org/