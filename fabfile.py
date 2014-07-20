import sys
from os import chdir
from os.path import exists
from datetime import datetime
import time
import yaml
from fabric.api import env, task, local, run, abort
from fabric.context_managers import cd, lcd
from fabric.colors import yellow, red
from fabric.utils import _AttributeDict
from django.core import management

env.colors = True
env.format = True
env.config_file = 'fabconfig.yaml'
env.config_file_tpl = 'fabconfig.tpl.yaml'
env.private_data_dir = 'private'
env.settings_tpl = 'settings.tpl.py'
env.settings_dir = 'settings'
env.releaseTS = int(round(time.time()))
env.release = datetime.fromtimestamp(env.releaseTS).strftime('%y%m%d%H%M%S')

def _msg(msg):
    print yellow('>>> ' + msg)


def _build_fab_conf():
    local('./simple-proc-tpl.sh {config_file_tpl} {private_data_dir}/fabconfig {config_file}'.format(**env))


def _setup():
    # Load config file
    if not exists(env.config_file):
        _msg('fabconfig.yaml not found. Attempt to build from template ...')
        _build_fab_conf()
    config_file = open(env.config_file, 'rb')
    env.config = _AttributeDict(yaml.safe_load(config_file.read()))
    config_file.close()

    # Set hosts from config file
    env.hosts = env.config.hosts

    # Process paths, allowing references
    paths = _AttributeDict(env.config.paths)
    process_again = True
    while process_again:
        process_again = False
        for p in paths:
            paths[p] = paths[p].format(**paths)
            if paths[p].find('{') != -1:
                process_again = True
    env.config.paths = paths
_setup()


# This is taken from
# https://github.com/tkopczuk/one_second_django_deployment/blob/master/fabfile.py
# Removed S3 and gzipping and adopted to coding style
@task
def build_static():
    recollect_static()
    
    _msg('building static')
    def get_file_base_and_extension(filename):
        if filename.count('.'):
            return '.'.join(filename.split('.')[:-1]), '.{0}'.format(filename.split('.')[-1])
        else:
            return filename, ''
    
    # bundle
    for bundle_path in env.config.bundle_and_minify:
        with open(bundle_path, 'w') as outfile:
            for libpath in env.config.bundle_and_minify[bundle_path]:
                with open(libpath, 'r') as libfile:
                    outfile.write(libfile.read())
        # this replaces the large code block below for our purposes
        outpath_components = get_file_base_and_extension(bundle_path)
        minified_path = '{0}.min{1}'.format(outpath_components[0], outpath_components[1])
        local('java -jar {yuicompressor} -v -o "{out_file}" --charset utf-8 "{in_file}"'.format(
                yuicompressor=env.config.paths.yuicompressor_path, out_file=minified_path, in_file=bundle_path),
              capture=False)


@task#('app-servers')
def deploy():
    _msg('generating dummy config-file for the public')
    # hack
    _msg('updating release ID and timestamp')
    local('sed -ri "'+r"s/^(release = )'(.*?)'$/\1'{release}'/; s/^(releaseTS = )([0-9]+)$/\1{releaseTS}/"+'" {project}/__init__.py'.format(project=env.config.default['project'], **env))
    _msg('creating source tarball')
    src_file = '{project}-{release}.tgz'.format(project=env.config.default['project'], **env)
    env.src_file = src_file
    res = local('cd ..; tar -czf {src_file} --exclude="*.pyc" --exclude="{project}/env" --exclude="{project}/static/*" --exclude="{project}/media/*" --exclude="{project}/settings" --exclude="{project}/{config_file}" --exclude="migrations" {project}'.format(project=env.config.default['project'], **env))
    if res.failed:
        abort(res.stderr)
    env().multirun(_deploy)
    _msg('deleting source tarball locally')
    local('rm ../{0}'.format(src_file))


def _deploy():
    _msg('uploading source tarball')
    local('scp ../{src_file} {user}@{host_string}:{media}/src/'.format(**env))
    _msg('syncing source')
    local('rsync -avuz --delete --exclude="*.pyc" --exclude="/settings.py" --exclude="migrations/" {project}/ {user}@{host_string}:{path}/{project}/{project}/'.format(**env), capture=False)
    _msg('syncing remote settings')
    local('rsync -avuz settings/settings-{host_string}.py {user}@{host_string}:{path}/{project}/{project}/settings.py'.format(**env))
    _msg('syncing static')
    local('rsync -avuz --delete {static_relative_dir}/ {user}@{host_string}:{static}/'.format(**env), capture=False)


@task#('app-servers')
def restart():
    env().multirun(_restart)


def _restart():
    _msg('restarting server')
    res = run(env.restart.format(**env))
    print res.stderr


@task
def recollect_static():
    with lcd(env.config.static_relative_dir):
        _msg('removing all files in static')
        local('rm -rf *')
    _msg('collecting static')
    #print red('>>> warning: remember that things will go wrong if local and server environment is not the same!')
    local('echo yes | env python manage.py collectstatic', capture=False)


@task#('app-servers')
def remote_collect_static():
    env().multirun(_remote_collect_static)


def _remote_collect_static():
    _msg('collecting static')
    with cd(env.path.format(**env)):
        res = run('. {pyenv}/bin/activate; echo yes | python {project}/manage.py collectstatic')
        print res.stdout


@task
def build_translation():
    # http://blog.brendel.com/2010/09/how-to-customize-djangos-default.html
    chdir(env.config.default['project'])
    _msg('translating all messages')
    management.call_command('makemessages', all=True)
    _msg('Removing commented-out manual messages')
    local(r"find locale -name 'django.po' -exec sed s/^\#\~\ // -i {{}} \;")
    _msg('Compiling messages')
    management.call_command('compilemessages')


@task#('app-servers')
def build_settings():
    env().multirun(_build_settings)


def _build_settings():
    _msg('building settings file')
    local('./simple-proc-tpl.sh {settings_tpl} {private_data_dir}/settings_prod {settings_dir}/settings-{host_string}.py'.format(**env))


@task
def rebuild_fab_conf():
    _msg('rebuilding {config_file}'.format(**env))
    _build_fab_conf()
