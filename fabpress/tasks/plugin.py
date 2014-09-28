#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base
from fabpress import utils


class WPPluginSync(base.TargetTask):
	"""Download and activate origin plugins on target"""
	
	name = "sync"

	def operation(self, target, data=None):
		origin = utils.reverse(target)
		if data is None:
			data = self.subtask(base.collect_data, origin)

		for plugin in data['plugins']:
			if plugin in utils.setting('skip_plugins'):
				self.info("Skipping plugin {0}; it is listed in skip_themes".format(plugin))
			else:
				self.info('Installing plugin {0} ({1})...'.format(plugin.get("name"), plugin.get('version')))
				command = "plugin install {0} --activate --version={1}".format(plugin.get("name"), plugin.get('version'))
				self.subtask(base.wp, target, command)

sync = WPPluginSync()