from fabpress import tasks as fp
import fab_settings
from fabric.decorators import task

@task
def hello():
    test