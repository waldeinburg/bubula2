from fabric.api import env, local, run, cd, lcd
from fabfile import _env

def hook_syncdb__migrate(dest):
    with cd(env.config.paths[dest].git), _env(dest):
        run('./manage.py migrate comics 0001 --fake') # Use migrations for app
        run('./manage.py migrate comics') # Rest of migrations

