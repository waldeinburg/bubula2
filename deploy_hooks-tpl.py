# TEMPLATE FOR deploy_hooks.py
# Hooks to be run as part of next deploy.
# Hooks are named with hook_ followed by the pre and post steps
# (between which steps the hook will be run) separated by two underscores.
# Hooks take dest ('prod' or 'test'; or 'local' for testing) as an argument.
# Example:
#   def hook_syncdb__migrate(dest):
#       cmd = local if dest == 'local' else run
#       cmd(...)
# When adding new hooks be sure to update both _deploy_test and _deploy_prod.
# Available hooks:
#   syncdb__migrate

from fabric.api import env, local, run, cd, lcd
from fabfile import _env

