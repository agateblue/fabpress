import base, fs, db, plugin, media as med, theme
import os, sys, ntpath, datetime
from fabpress import utils
from fabric.contrib import console
from fabric.api import warn_only

class WPDrop(base.ConfirmTask, base.TargetTask):
	"""Delete target files and database"""
	name = "drop"

	def operation(self, target):
		base.subtask(db.reset, target=target)
		base.subtask(fs.drop, target=target)

wp_drop = WPDrop()

class WPDownload(base.ConfirmTask, base.TargetTask):
	"""Download at target a copy of origin Wordpress files (version and languages preserved)"""
	name="download"

	def operation(self, target, data=None):
		origin = utils.reverse(target)
		if data is None:
			data = base.subtask(base.collect_data, origin)

		# create directory if needed
		base.subtask(base.run_target, target, "mkdir -p '{0}'".format(utils.setting('path', target)))
		download_command = "core download --locale={0} --path='{1}' --version='{2}'".format(
			data.get('locales')[0], utils.setting('path', target), data.get('version'))

		# fix permissions
		self.log('Changing permissions of {0} to {1}'.format(utils.setting('path', target), utils.setting("default_chmod")))
		base.subtask(base.run_target, target, "chmod {0} -R '{1}'".format(utils.setting("default_chmod"), utils.setting('path', target)))

		with warn_only():
			output = base.subtask(base.wp, target, download_command)

		# install additionnal languages
		for locale in data.get('locales')[1:]:
			base.subtask(wp,target, "core language install {0}".format(locale))

		# check if wp-config.php exists:
		wp_config_path = os.path.join(utils.setting("path", target), "wp-config.php")
		command = """[ -f '{0}' ] && echo '1' 2>&1 || echo '0' 2>&1""".format(wp_config_path)
		output = base.subtask(base.run_target, target, command)
		wp_config_exists = int(output)
		# "${EDITOR:-vi}"
		edit_command = "{0} {1}".format("nano", wp_config_path)

		if wp_config_exists:
			self.log("Existing wp-config.php file found")

		else:
			# copy the sample
			command = "mv '{0}' '{1}'".format(os.path.join(utils.setting("path", target), "wp-config-sample.php"), wp_config_path)
			base.subtask(base.run_target, target, command)
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
		data = base.subtask(base.collect_data, origin)

		# download wordpress files
		base.subtask(download, target, data=data)

		# sync
		base.subtask(sync, target, data=data)



wp_mirror = WPMirror()

class WPPull(base.ConfirmTask, base.BaseTask):
	"""Sync database, themes, plugins and media files from remote to local installation"""

	name="pull"

	def operation(self, **kwargs):
		base.subtask(sync, "local", **kwargs)

pull = WPPull()


class WPPush(base.ConfirmTask, base.BaseTask):
	"""Sync database, themes, plugins and media files from local to remote installation"""

	name="push"

	def operation(self, **kwargs):
		base.subtask(sync, "remote", **kwargs)

push = WPPush()

class WPSync(base.ConfirmTask, base.TargetTask):
	"""Sync target with origin database, themes, plugins and media files"""

	name = "sync"
	expected_args = [
		("sync_media", False, "no|n|0"),
	]
	def operation(self, target, sync_media=True, data=None):

		origin = utils.reverse(target)
		if data is None:
			data = base.subtask(base.collect_data, origin)

		# import the database
		base.subtask(db.sync, target)

		# download plugins and themes
		base.subtask(theme.sync, target, data)
		base.subtask(plugin.sync, target, data)

		if self.parse_boolean(sync_media):
			# download media files
			base.subtask(med.sync, target)

		# create required symlinks
		base.subtask(fs.symlinks)

sync = WPSync()

class WPHelp(base.BaseTask):
	"""Get some help"""

	name = "help"
	def operation(self):
		print('fab -l to list available commands.\nfab fp.<command>:help to get help about a given command')
		
help = WPHelp()

	