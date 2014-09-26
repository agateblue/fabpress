import base
import os
from fabpress import utils


class WPFilesDrop(base.ConfirmTask, base.TargetTask):
	"""Remove all files of target, including target directory"""

	name = "drop"

	def operation(self, target):
		command = 'find {0}/ -name "*" | xargs rm -rf '.format(os.path.join(utils.setting("path", target)))
		base.subtask(base.run_target, target=target, command=command)

drop = WPFilesDrop()




class WPSymlink(base.BaseTask):
	"""Create a symlink"""

	name = "symlink"

	def operation(self, symlink_target, path):
		self.info("Symlinking {0} to {1}".format(symlink_target, path))
		command = 'local', "ln -s '{0}' '{1}'".format(symlink_target, path)
		try:
			base.subtask(base.run_target, 'local', command)
			self.info("Symlink created")
		except:
			self.info("Cannot create symlink, he probably already exists")

symlink = WPSymlink()

class WPSymlinks(base.BaseTask):
    """Create symlinks to local themes on plugins on local installation"""

    name = "symlinks"

    def operation(self):
        self.info("Symlinking themes...")
        base.subtask(theme_symlinks)

symlinks = WPSymlinks()


class WPThemeSymlinks(base.BaseTask):
	"""Create local symlinks for themes listed in settings.local.symlink_themes"""
	name = "theme_symlinks"

	def operation(self):
		themes = utils.setting("symlink_themes", "local")
		themes_path = os.path.join(utils.setting("path", "local"), "wp-content", "themes")

		for theme_name, theme_path in themes:
			symlink_destination = os.path.join(themes_path, theme_name)
			base.subtask(symlink, theme_path, symlink_destination)

theme_symlinks = WPThemeSymlinks()