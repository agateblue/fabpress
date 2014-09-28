#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, fs, db, plugin, media as med, theme
from base import wp
import os, sys, ntpath, datetime
from fabpress import utils
from fabric.contrib import console
from fabric.api import warn_only


class SyncMediaTask(object):
	"""A task that involve media synchronisation. As it his a heavy and bandwith intensive operation,
	it adds a `sync_media` arguments to disable it when needed""" 

	expected_args = [
		base.Argument("sync_media", False, "no|n|0", base.strtobool, lambda v: isinstance(v, bool)),
	]


class WPDrop(base.ConfirmTask, base.TargetTask):
	"""Delete target files and database. Will also delete the installation parent directory."""
	name = "drop"

	def operation(self, target):
		self.subtask(db.reset, target=target)
		self.subtask(fs.drop, target=target)

wp_drop = WPDrop()

class WPDownload(base.ConfirmTask, base.TargetTask):
	"""Download at target a copy of origin Wordpress files (version and languages preserved)"""
	name ="download"

	def operation(self, target, data=None):
		origin = utils.reverse(target)
		if data is None:
			data = self.subtask(base.collect_data, origin)

		# create directory if needed
		self.subtask(base.run_target, target, "mkdir -p '{0}'".format(utils.setting('path', target)))
		download_command = "core download --locale={0} --path='{1}' --version='{2}'".format(
			data.get('locales')[0], utils.setting('path', target), data.get('version'))

		# fix permissions
		self.log('Changing permissions of {0} to {1}'.format(utils.setting('path', target), utils.setting("default_chmod")))
		self.subtask(base.run_target, target, "chmod {0} -R '{1}'".format(utils.setting("default_chmod"), utils.setting('path', target)))

		with warn_only():
			output = self.subtask(base.wp, target, download_command)

		# install additionnal languages
		for locale in data.get('locales')[1:]:
			self.subtask(wp,target, "core language install {0}".format(locale))

		# check if wp-config.php exists:
		wp_config_path = os.path.join(utils.setting("path", target), "wp-config.php")
		command = """[ -f '{0}' ] && echo '1' 2>&1 || echo '0' 2>&1""".format(wp_config_path)
		output = self.subtask(base.run_target, target, command)
		wp_config_exists = int(output)
		# "${EDITOR:-vi}"
		edit_command = "{0} {1}".format("nano", wp_config_path)

		if wp_config_exists:
			self.log("Existing wp-config.php file found")

		else:
			# copy the sample
			command = "mv '{0}' '{1}'".format(os.path.join(utils.setting("path", target), "wp-config-sample.php"), wp_config_path)
			self.subtask(base.run_target, target, command)
			edit = console.confirm("wp-config.php was copied from sample. Do you want to edit it ?")
			if edit:
				# edit the wp-config.php
				sys.exit('Edit your file located at {0} then relaunch this command'.format(wp_config_path))

download  = WPDownload()

class WPMirror(base.ConfirmTask, base.TargetTask):
	"""Create at target an exact mirror of origin wordpress installation"""
	name="mirror"

	def operation(self, target):
		origin = utils.reverse(target)

		# get informations about installation we need to mirror, such as wp version, locale, themes, plugins...
		data = self.subtask(base.collect_data, origin)

		# download wordpress files
		self.subtask(download, target, data=data)

		# sync
		self.subtask(sync, target, data=data)

wp_mirror = WPMirror()


class WPPull(SyncMediaTask, base.ConfirmTask, base.BaseTask):
	"""Sync database, themes, plugins and media files from remote to local installation"""

	name="pull"

	def operation(self, *args, **kwargs):
		self.subtask(sync, "local", *args, **kwargs)

pull = WPPull()


class WPPush(SyncMediaTask, base.ConfirmTask, base.BaseTask):
	"""Sync database, themes, plugins and media files from local to remote installation"""

	name="push"

	def operation(self, *args, **kwargs):
		self.subtask(sync, "remote", *args, **kwargs)

push = WPPush()


class WPSync(SyncMediaTask, base.ConfirmTask, base.TargetTask):
	"""Pull origin database, themes, plugins and media files to target"""

	name = "sync"
	
	def operation(self, target, sync_media=True, data=None):

		origin = utils.reverse(target)
		if data is None:
			data = self.subtask(base.collect_data, origin)

		# import the database
		self.subtask(db.sync, target)

		# download plugins and themes
		self.subtask(theme.sync, target, data)
		self.subtask(plugin.sync, target, data)

		if base.strtobool(sync_media):
			# download media files
			self.subtask(med.sync, target)

sync = WPSync()


class WPHelp(base.BaseTask):
	"""Get some help"""

	name = "help"
	def operation(self):
		print('fab -l to list available commands.\nfab fp.<command>:help to get help about a given command')
		
help = WPHelp()

	