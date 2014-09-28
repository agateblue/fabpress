#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base
import os, sys, ntpath, datetime
from fabpress import utils


class WPDBSync(base.ConfirmTask, base.TargetTask):

	"""Sync target database with origin"""

	name="sync"

	def get_start_message(self):
		return "Syncing databases (from {0} to {1})".format(utils.reverse(self.target), self.target)

	def operation(self, target):
		origin = utils.reverse(target)	

		# create the backup	
		backup_path = self.subtask(export, target=origin)

		# import it
		self.subtask(imp, target=target, path=backup_path)

		# update permalinks
		self.subtask(permalink_fix, target=target)

sync = WPDBSync()


class WPDBExport(base.TargetTask):

	"""Export the database from target installation to the given path"""

	name="export"

	def operation(self, target):	
		backup_name = "{0}-{1}.sql".format(target, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
		backup_path = os.path.join(utils.setting("dumps_path", target), backup_name)
		self.log("Exporting {0} database to {1}...".format(target, backup_path))
		self.subtask(base.wp, target=target, command="db export '{0}'".format(backup_path))
		return backup_path

export = WPDBExport()


class WPDBImport(base.ConfirmTask, base.TargetTask):

	"""Import the database dump at origin path to the target"""

	name="import"

	def operation(self, target, path):

		# Create a backup just in case
		self.subtask(
			export, 
			target=target, 
			start_message='Creating a safety backup of {0} database, juste in case'.format(target))

		# download or upload the dump to the target
		target_dump_path = os.path.join(utils.setting('dumps_path', target), ntpath.basename(path))
		self.subtask(
			base.get_file, 
			target=target, 
			origin_path=path, 
			target_path=target_dump_path, 
			start_message="Downloading backup from {0}".format(utils.reverse(target)))

		self.log("Importing {0} into {1} database...".format(target_dump_path, target))
		self.subtask(base.wp,target=target, command="db import '{0}'".format(target_dump_path))

		# remove the backup file locally and remotely
		self.log("Deleting useless SQL backups...", indentation=1)
		self.subtask(base.run_target, utils.reverse(target), "rm '{0}'".format(path))
		self.subtask(base.run_target, target, "rm '{0}'".format(target_dump_path))

imp = WPDBImport()


class WPClearBackups(base.ConfirmTask, base.TargetTask):
	"""Remove backup files on target"""

	name = "clear_backups"

	def operation(self, target):
		command = "rm -rf '{0}/'{1}".format(utils.setting('dumps_path', target), "remote-*.sql")
		self.subtask(base.run_target, target, command)
		command = "rm -rf '{0}/'{1}".format(utils.setting('dumps_path', target), "local-*.sql")
		self.subtask(base.run_target, target, command)

clear_backups = WPClearBackups()


class WPPermalinkFix(base.TargetTask):

	"""Search and replace all occurence of origin domain with target domain"""

	name = "fix_permalinks"

	def operation(self, target):

		# replace permalink
		search_url = utils.setting("url", utils.reverse(target))
		replace_url = utils.setting("url", target)
		command = "search-replace '{0}' '{1}' --precise".format(search_url, replace_url)
		self.log("Updating URL(s) from {0} to {1}...".format(search_url, replace_url))
		output = self.subtask(base.wp, target=target, command=command)

		# update structure
		self.log("Updating permalinks structure to {0}...".format(utils.setting("permalinks")))
		self.subtask(base.wp, target=target, command="rewrite flush --hard")
		self.subtask(base.wp, target=target, command="rewrite structure '{0}'".format(utils.setting("permalinks")))


permalink_fix = WPPermalinkFix()


class WPDBReset(base.ConfirmTask, base.TargetTask):
	"""Delete all tables in target database"""

	name = "reset"

	def operation(self, target):
		self.subtask(base.wp, target=target, command="db reset --yes")

reset = WPDBReset()