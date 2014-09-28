
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