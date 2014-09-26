from fabric.tasks import Task
from fabric.contrib import console
from fabric import colors, operations, state, api
from fabric.api import local, run, cd, lcd, env, output, hide, show, warn_only

from fabpress import utils
import os, sys, json



def strtobool(v):
	try:
		v = v.lower()
	except: pass

	if v in ['y', 'yes', True, 1, '1']:
		return True
	return False

class Argument(object):

	parser = None
	checker = None
	helper = ""
	name = ""
	required = True

	def __init__(self, name, required=True, helper=None, parser=None, checker=None):

		self.required = required
		self.helper = helper
		self.parser = parser
		self.checker = checker



class ArgumentError(Exception):
	pass

class AbstractBaseTask(object):
	name = None
	start_message = None
	kwargs = {}
	args = {}
	hide = ['commands']
	show = []
	silent = False
	subtask = False
	expected_args = []

	def __call__(self, *args, **kwargs):

		return self.run(*args, **kwargs)
		
	def get_expected_args(self):
		parents = self.__class__.__bases__
		expected_args = []

		for parent in parents:
			try: 
				expected_args += parent.expected_args
			except: pass


		# put optional args at the end
		required_args = [arg for arg in expected_args if arg[1] == True]
		optional_args = [arg for arg in expected_args if arg[1] == False]

		return required_args + optional_args

	def get_description(self):
		return """Task description:\n\n\t{0}\n""".format(self.__class__.__doc__)

	def get_task_id(self):
		module = self.__module__.split('.')[-1]
		return "{0}.{1}".format(module, self.name)

	def get_usage(self):

		description = self.get_description()

		args = ""

		for arg_name, required, value, parser, checker in self.get_expected_args():
			arg = "{0}=<{1}>".format(arg_name, value)
			if not required:
				arg = "[" + arg + "]"
			args = args + arg + ","

		# remove coma
		args = args[:-1]

		command = "\n" + description + "\nTask usage: \n\n\tfab fp.{0}:{1}\n".format(self.get_task_id(), args)

		return command

	def log(self, message, color=None, bold=False, prefix=True, force=False):
		if force or not self.silent:
			
			if color is not None:
				print(getattr(colors, color)(message, bold=bold))
			else:
				print(message)

	def success(self, message, bold=False, prefix=True):
		if self.subtask:
			self.log(message, None, bold, prefix)
		else:
			self.log(message, "green", bold, prefix)

	def info(self, message, bold=False, prefix=True):
		if self.subtask:
			self.log(message, None, bold, prefix)
		else:
			self.log(message, "yellow", bold, prefix)

	def error(self, message, bold=False, prefix=False):
		self.log(message, "red", bold, prefix=prefix, force=True)


	def pre_run(self):
		
		if not self.subtask:
			message = self.get_start_message()
			if message: 
				self.info(message.capitalize() + "...")

	
	def check_args(self):
		pass

	def setup(self, *args, **kwargs):
		self.kwargs = kwargs
		self.args = list(args)
		self.hide = self.kwargs.pop('hide', self.hide)
		self.show = self.kwargs.pop('show', self.show)
		self.subtask = self.kwargs.pop('subtask', False)
		self.silent = self.kwargs.pop('silent', False)
		try:		
			self.check_args()
		except ArgumentError, e:
			self.error("\nThe task was called with incorrectly: {0}. Please refer to task usage:".format(str(e)))
			self.log(self.get_usage())
			sys.exit()

		if not self.subtask:
			message = self.get_task_description()
			self.log(message)

	def run(self, *args, **kwargs):	
		try:
			assert args[0] == "help"
			self.log(self.get_usage())
			return
		except: pass

		self.setup(*args, **kwargs)
		
		self.pre_run()
		with hide(*self.hide), show(*self.show):
			r = self.operation(*self.args, **self.kwargs)
			
		self.post_run()
		return r		

	def post_run(self):

		with show('everything'):
			self.trigger_hooks()

	def trigger_hooks(self):

		task = self.get_task_id()
		hooks = utils.setting("hooks")
		hooks_to_trigger = [hook for key, hook in hooks.items() if key == task]
		for hook in hooks_to_trigger:
			self.trigger_hook(hook)

	def trigger_hook(self, hook):
		name = ""
		try: name = hook.__name__
		except: name = __hook__.__class__.__name__

		self.log("Triggering {0} hook: {1}...".format(self.get_task_id(), name))
		hook(self)

	def get_task_description(self):
		
		message = self.get_description()
		if self.args or self.kwargs:
			task_arguments = "\nThe task was launched with the following arguments:\n\n"


			for key, value in self.kwargs.items():
				task_arguments += "- {0} : {1}\n".format(key, value)

			message += task_arguments

		return 	message


	def get_start_message(self, *args, **kwargs):
		if self.start_message is not None:
			return self.start_message
		return None

	

class BaseTask(AbstractBaseTask, Task):
	pass


class ConfirmTask(object):
	"""Will ask for user confirmation before doing anything else"""

	confirmed = False
	confirm_message = "This is an important choice. "
	confirm_choice = "Do you want to continue ?"
	default = False

	expected_args = [
		Argument("confirm", False, "yes|y|1", strtobool, lambda v: isinstance(v, bool)),
	]
	def setup(self, *args, **kwargs):
		super(ConfirmTask, self).setup(*args, **kwargs)
		confirm = self.kwargs.pop('confirm', False)
		if not confirm:
			if not self.subtask:
				question = self.confirm_message + self.confirm_choice
				self.confirmed = console.confirm(question, default=self.default)

				if not self.confirmed:
					sys.exit('Cancelling task...')	

class TargetTask(BaseTask):	
	target = None
	expected_args = [
		Argument("target", True, "local|remote", lambda v: v, lambda v: v in ['local', 'remote']),
	]

	def trigger_hooks(self):
		super(TargetTask, self).trigger_hooks()
		task = self.get_task_id()
		hooks = utils.setting("hooks", self.target, {})
		hooks_to_trigger = [hook for key, hook in hooks.items() if key == task]
		for hook in hooks_to_trigger:
			self.trigger_hook(hook)

class RunTarget(AbstractBaseTask):
	"""Run a unix command on the target"""
	name = "run_target"

	def operation(self, target, command, capture=True):
		if utils.is_local(target):
			return local(command, capture=capture)

		if utils.is_remote(target):
			return run(command)

run_target = RunTarget()


def subtask(task, *args, **kwargs):
	return task(*args, subtask=True, **kwargs)
	

class WP(TargetTask):
	"""Execute a wp-cli command on the target. You don't need to prefix it with "wp"""
	name = "wp"

	def setup(self, *args, **kwargs):
		if kwargs.get('subtask', False) is False:
			kwargs['show'] = ["stdout"]
		else:
			kwargs['silent'] = kwargs.get('silent', True)
		super(WP, self).setup(*args, **kwargs)

	def operation(self, target, command):	
		"""run a wpcli command on local or remote"""

		if utils.is_local(target):
			with lcd(utils.setting("path", "local")):
				return local("wp {0}".format(command), capture=True)

		if utils.is_remote(target):
			with cd(utils.setting("path", "remote")):
				return run("wp {0}".format(command))

wp = WP()


class GetFile(TargetTask):
	"""Download a file from remote to local (if target is local) or upload a local file to remote"""
	name = "get_file"
	hide = ['commands', "warnings"]
	def operation(self, target, origin_path, target_path):

		self.log("Downloading from {0}:{1} to {2}:{3}...".format(utils.reverse(target), origin_path, target, target_path))
		if utils.is_local(target):
			operations.get(remote_path=origin_path, local_path=target_path)

		if utils.is_remote(target):
			operations.put(remote_path=target_path, local_path=origin_path)

get_file = GetFile()


class WPCollectData(TargetTask):
	name="collect_data"

	def operation(self, target):
		"""Return a dict of data about the targeted wordpress installation"""
		data = {}
		self.log('Collecting data about {0} Wordpress installation...'.format(target))
		# get wordpress version

		data['version'] = subtask(wp, target, "core version")

		# get wordpress locale
		json_data = subtask(wp, target, "core language list --format=json")
		languages = json.loads(json_data)
		active_languages = [language['language'] for language in languages if language['status'] == "active"]
		data['locales'] = active_languages

		# get plugins data
		json_data = subtask(wp, target, "plugin list --format=json")
		plugins = json.loads(json_data)
		active_plugins = [plugin for plugin in plugins if plugin['status'] == "active"]
		data['plugins'] = active_plugins

		# get themes data
		json_data = subtask(wp, target, "theme list --format=json")
		themes = json.loads(json_data)
		active_themes = [theme for theme in themes if theme['status'] == "active"]
		data['themes'] = active_themes

		return data

collect_data = WPCollectData()

