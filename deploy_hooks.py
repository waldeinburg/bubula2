from fabric.api import env, local, run, cd, lcd
from fabfile import _env

def hook_syncdb__migrate(dest):
    cmd = local if dest == 'local' else run
    with cd(env.config.paths[dest].git), _env(dest):
        cmd('./manage.py migrate comics 0001 --fake') # Use migrations for app

