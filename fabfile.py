import sys
from os import chdir
from os.path import exists
from datetime import datetime
import time
import yaml
from fabric.api import env, task, local, run, cd, abort
from fabric.colors import yellow, red
from fabric.utils import _AttributeDict
from django.core import management

env.colors = True
env.format = True
env.config_file = 'fabconfig.yaml'
env.config_file_tpl = 'fabconfig.tpl.yaml'
env.private_data_file = 'private'
env.settings_tpl = 'settings.tpl.py'
env.settings_dir = 'settings'
env.releaseTS = int(round( time.time() ))
env.release = datetime.fromtimestamp(env.releaseTS).strftime('%y%m%d%H%M%S')
env.optimizeImages = False
env.yuicompressorPath = '/usr/local/bin/yuicompressor-2.4.7.jar'

def _build_fab_conf():
    local('./simple-proc-tpl.sh {config_file_tpl} {private_data_file} {config_file}'.format(**env))


def _setup():
    # Load config file
    if not exists(env.config_file):
        print yellow('>>> fabconfig.yaml not found. Attempt to build from template ...')
        _build_fab_conf()
    config_file = open(env.config_file, 'rb')
    env.config = _AttributeDict(yaml.safe_load(config_file.read()))
    config_file.close()

    # Set hosts from config file
    env.hosts = env.config.hosts

    # Process paths, allowing references
    process_again = True
    while process_again:
        process_again = False
        for p in env.config.paths:
            env.config.paths[p] = env.config.paths[p].format(**env.config.paths)
            if env.config.paths[p].find('{') != -1:
                process_again = True
_setup()


# This is taken from
# https://github.com/tkopczuk/one_second_django_deployment/blob/master/fabfile.py
# Removed S3 and gzipping and adopted to coding style
@task
def build_static():
    print yellow('>>> collecting static')
    local('echo yes | env python manage.py collectstatic', capture=False)
    
    print yellow('>>> building static')
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
                    outfile.write( libfile.read() )
        # this replaces the large code block below for our purposes
        outpathComponents = get_file_base_and_extension(bundle_path)
        minifiedPath = '{0}.min{1}'.format(outpathComponents[0], outpathComponents[1])
        local('java -jar {yuicompressor} -v -o "{outFile}" --charset utf-8 "{inFile}"'.format(
                yuicompressor=env.yuicompressorPath, outFile=minifiedPath, inFile=bundle_path),
              capture=False)


@task#('app-servers')
def deploy():
    print yellow('>>> generating dummy config-file for the public')
    # hack
    print yellow('>>> updating release ID and timestamp')
    local( 'sed -ri "'+r"s/^(release = )'(.*?)'$/\1'{release}'/; s/^(releaseTS = )([0-9]+)$/\1{releaseTS}/"+'" {project}/__init__.py'.format(project=env.config.default['project'], **env) )
    print yellow('>>> creating source tarball')
    srcFile = '{project}-{release}.tgz'.format(project=env.config.default['project'], **env)
    env.srcFile = srcFile
    res = local( 'cd ..; tar -czf {srcFile} --exclude="*.pyc" --exclude="{project}/env" --exclude="{project}/static/*" --exclude="{project}/media/*" --exclude="{project}/settings" --exclude="{project}/{config_file}" --exclude="migrations" {project}'.format(project=env.config.default['project'], **env) )
    if res.failed:
        abort(res.stderr)
    env().multirun(_deploy)
    print yellow('>>> deleting source tarball locally')
    local ( 'rm ../{0}'.format(srcFile) )


def _deploy():
    print yellow('>>> uploading source tarball')
    local( 'scp ../{srcFile} {user}@{host_string}:{media}/src/'.format(**env) )
    print yellow('>>> syncing source')
    local( 'rsync -avuz --delete --exclude="*.pyc" --exclude="/settings.py" --exclude="migrations/" {project}/ {user}@{host_string}:{path}/{project}/{project}/'.format(**env), capture=False )
    print yellow('>>> syncing remote settings')
    local( 'rsync -avuz settings/settings-{host_string}.py {user}@{host_string}:{path}/{project}/{project}/settings.py'.format(**env) )
    print yellow('>>> syncing static')
    local( 'rsync -avuz --delete {static_relative_dir}/ {user}@{host_string}:{static}/'.format(**env), capture=False )


@task#('app-servers')
def restart():
    env().multirun(_restart)


def _restart():
    print yellow('>>> restarting server')
    res = run( env.restart.format(**env) )
    print res.stderr


@task
def recollect_static():
    with cd(env.config.default['static_relative_dir']):
        print yellow('>>> removing all files in static')
        local('rm -r *')
    print yellow('>>> collecting static')
    # FIXME: even when using virtualenv, statics are collected from dist-packages.
    # Find a secure way to sync with server environment
    print red('>>> warning: remember that things will go wrong if local and server environment is not the same!')
    local('echo yes | python manage.py collectstatic')


@task#('app-servers')
def remote_collect_static():
    env().multirun(_remote_collect_static)


def _remote_collect_static():
    print yellow('>>> collecting static')
    with cd( env.path.format(**env) ):
        res = run('. {pyenv}/bin/activate; echo yes | python {project}/manage.py collectstatic')
        print res.stdout


@task
def build_translation():
    # http://blog.brendel.com/2010/09/how-to-customize-djangos-default.html
    chdir(env.config.default['project'])
    print yellow('>>> translating all messages')
    management.call_command('makemessages', all=True)
    print yellow('>>> Removing commented-out manual messages')
    local(r"find locale -name 'django.po' -exec sed s/^\#\~\ // -i {{}} \;")
    print yellow('>>> Compiling messages')
    management.call_command('compilemessages')


@task#('app-servers')
def buildsettings():
    env().multirun(_build_settings)


def _build_settings():
    print yellow('>>> building settings file')
    local('./simple-proc-tpl.sh {settings_tpl} {private_data_file} {settings_dir}/settings-{host_string}.py'.format(**env))


@task
def rebuild_fab_conf():
    # The file private contains lines of the form
    # VARIABLE=value
    print yellow('>>> rebuilding {config_file}'.format(**env))
    _build_fab_conf()


@task
def local_recreate_env():
    print yellow('>>> deleting env')
    # delete env (silent fail)
    # local:
    #   pip install -r envreq.txt --allow-external PIL --allow-unverified PIL
