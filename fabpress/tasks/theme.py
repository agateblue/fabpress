import base
from fabpress import utils
import os

class WPThemeSync(base.TargetTask):
    """Download and activate origin themes on target"""
    
    name = "sync"

    def operation(self, target, data=None):
        origin = utils.reverse(target)
        if data is None:
            data = base.subtask(base.collect_data, origin)

        for theme in data['themes']:

            if theme.get('name') in utils.setting('skip_themes'):
                self.info("Skipping theme {0}: it is listed in skip_themes".format(theme.get('name')))
            else:
                self.info('Installing theme {0} ({1})...'.format(theme.get("name"), theme.get('version')))
                command = "theme install {0} --activate --version={1}".format(theme.get("name"), theme.get('version'))
                base.subtask(base.wp, target, command)


sync = WPThemeSync()