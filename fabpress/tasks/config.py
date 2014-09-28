import base
from fabric.api import local
from fabpress import sample_settings
import os

class ConfigCreate(base.BaseTask):
    """Create a config file from fabpress sample"""

    expected_args = [
        base.Argument(
            "path", 
            False, 
            "/path/to/store/fab_settings.py (default is './fab_settings.py')", 
            lambda v: v, 
            lambda v: v),
    ]

    def operation(self, path="./fab_settings.py"):

        # check if the file does not ealready exist
        command = "[ -f '{0}' ] && echo 1 || echo 0".format(path)
        result = int(local(command, capture=True))
        if result == 1:
            self.error("A file already exists at {0}. Please move/delete it before running this task.".format(path))
            return

        copy_from = os.path.dirname(sample_settings.__file__) + "/sample_settings.py"
        self.log('Creating config file at {0}, from {1}...'.format(path, copy_from))

        # copy the file, but do not overwrite an existing file
        command = "cp '{0}' '{1}' -n".format(copy_from, path)
        local(command)

create = ConfigCreate()