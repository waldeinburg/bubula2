import sys
from os import chdir
from os.path import exists
from datetime import datetime
import time
import yaml
from fabric.api import env, task, get, local, run, abort, cd, lcd, prefix
from fabric.colors import yellow, red
from fabric.utils import _AttributeDict
from fabric.contrib import files
from django.core import management

# Fabric native settings
env.use_ssh_config = True
env.colorize_errors = True

# Other
env.config_file = 'fabconfig.yaml'
env.config_file_tpl = 'fabconfig.tpl.yaml'
env.private_data_dir = 'private'
env.releaseTS = int(round(time.time()))
env.release = datetime.fromtimestamp(env.releaseTS).strftime('%y%m%d%H%M%S')

def _msg(msg):
    print yellow('>>> ' + msg)


def _env(env_paths_key):
    return prefix('. {0}/bin/activate'.format(env.config.paths[env_paths_key]))


def _build_fabconfig():
    local('./simple-proc-tpl.sh {config_file_tpl} {private_data_dir}/fabconfig {config_file}'.format(**env))


def _setup():
    # Load config file
    if not exists(env.config_file):
        _msg('fabconfig.yaml not found. Attempt to build from template ...')
        _build_fabconfig()
    config_file = open(env.config_file, 'rb')
    env.config = _AttributeDict(yaml.safe_load(config_file.read()))
    config_file.close()

    # Set hosts from config file
    env.hosts = [ env.config.host ]

    # Wrap some lists
    env.config.local = _AttributeDict(env.config.local)
    paths = _AttributeDict(env.config.paths) # set back below

    # Process paths, allowing references
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
    recollect_static('local')
    
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
        outpath_components = get_file_base_and_extension(bundle_path)
        minified_path = '{0}.min{1}'.format(outpath_components[0], outpath_components[1])
        local('java -jar {paths.yuicompressor} -v -o "{out_file}" --charset utf-8 "{in_file}"'.format(
                  out_file=minified_path, in_file=bundle_path, **env.config),
              capture=False)


@task
def deploy(dest):
    dests = {
        'prod': _deploy_prod,
        'test': _deploy_test
    }
    dests[dest]() # will fail if wrong destination is given


def _deploy_test():
    # Deploy current branch
    branch = local("git branch | grep '\*' | cut -d' ' -f2", capture=True)
    local('git push {host_git_repo} {branch}'.format(branch=branch, **env.config))
    with cd(env.config.paths.host_git):
        run('export GIT_WORK_TREE={paths.test_git}; git checkout {branch} -f'.format(branch=branch, **env.config))
    # Update environment
    with cd(env.config.paths.test_git):
        if (files.exists(env.config.paths.test_env)):
            with _env('test_env'):
                _msg('updating environment')
                run('pip install -r envreq.txt')
        else:
            _msg('creating environment')
            run('./rebuild_env.sh {paths.test_env}'.format(**env.config))
    # Generate and upload settings file
    build_settings('test')
    _msg('uploading settings file')
    local('scp {local.settings_dir}/settings_test.py {host}:{paths.test_project}/settings.py'.format(
              **env.config))
    #TODO: Import prod db
    #_msg('importing db')
    #_backup_db()
    # Sync media
    _msg('syncing media from prod')
    run('rsync -av --delete {paths.media}/ {paths.test_media}/'.format(**env.config))
    # Sync static (to make sure test is a mirror of prod)
    _msg('syncing static from local. It is assumed that build_static has been run.')
    local('rsync -av --delete {local.static}/ {host}:{paths.test_static}/'.format(**env.config))
    # Update db
    _msg('updating database')
    with cd(env.config.paths.test_git), _env('test_env'):
        run('./manage.py syncdb') # Non-South
        run('./manage.py migrate') # South
    # Restart apache
    restart('test')


def _deploy_prod():
    #TODO: ask!
    # Deploy master
    local('git push {host_git_repo} master'.format(**env.config))
    with cd(env.config.paths.host_git):
        run('export GIT_WORK_TREE={paths.git}; git checkout master -f'.format(**env.config))
    # Update environment
    with cd(env.config.paths.git):
        if (files.exists(env.config.paths.env)):
            with _env('env'):
                _msg('updating environment')
                run('pip install -r envreq.txt')
        else:
            _msg('creating environment')
            run('./rebuild_env.sh {paths.env}'.format(**env.config))
    # Generate and upload settings file
    build_settings('prod')
    _msg('uploading settings file')
    local('scp {local.settings_dir}/settings_prod.py {host}:{paths.project}/settings.py'.format(
              **env.config))
    # Update db
    _msg('updating database')
    with cd(env.config.paths.test_git), _env('env'):
        run('./manage.py syncdb') # Non-South
        run('./manage.py migrate') # South
    # Restart apache
    restart('prod')
    
    return
    #TODO: tag and release, also on github
    _msg('updating release ID and timestamp')
    local('sed -ri "'+r"s/^(release = )'(.*?)'$/\1'{release}'/; s/^(releaseTS = )([0-9]+)$/\1{releaseTS}/"+'" {project}/__init__.py'.format(project=env.config.default['project'], **env))


@task
def restart(dest):
    dests = {
        'prod': env.config.paths.restart,
        'test': env.config.paths.test_restart
    }
    _msg('restarting {0} server'.format(dest))
    # Run restart command and sleep for one second.
    # The start seemed to fail because of the disconnect for some reason.
    run('{0} && sleep 1'.format(dests[dest]))


@task
def stop_test():
    _msg('stopping test server')
    run(env.config.paths.test_stop)


@task
def recollect_static(dest='local'):
    # TODO: for test (and prod) we should probably force build_static instead
    dests = {
        'local': _recollect_static_local,
        'test': _recollect_static_test
    }
    dests[dest]()


def _recollect_static_local():
    with lcd(env.config.local.static):
        _msg('removing all files in static')
        local('rm -rf *')
    _msg('collecting static')
    local('echo yes | ./manage.py collectstatic', capture=False)


def _recollect_static_test():
    print red('not implemented!')
    return
    _msg('collecting static')
    with cd(env.path.format(**env)):
        res = run('. {pyenv}/bin/activate; echo yes | python {project}/manage.py collectstatic')
        print res.stdout


@task
def backup():
    #run db backup, media backup and download
    print red('not implemented!')


def _backup_db():
    with cd(env.config.paths.git):
        #run('. {paths.env}/bin/activate && ./manage.py dbdump 
        pass


@task
def download_fixtures():
    """Download fixtures from prod for making the dev db mirror the prod db
    """
    dump_filename = 'dump.gz'
    with cd(env.config.paths.git), _env('env'):
        run('./manage.py dumpdata | gzip - > {0}'.format(dump_filename))
        get('{0}/{1}'.format(env.config.paths.git, dump_filename),
            local_path=env.config.local.db_dir)
        run('rm {0}'.format(dump_filename))


@task
def reset_db():
    """Resets database to the state in the master branch.
    """
    print red('not implemented!')
    return
    # Checkout to a temporary directory, run syncdb and migrate, move, delete
    tmp_work_tree = 'tmp_wt'
    local('git clone --depth=1 --branch=master file://$PWD {0}'.format(tmp_work_tree))
    with lcd(tmp_work_tree):
        pass
        #create environment
    #zcat db/dump.gz | ./manage.py loaddata /dev/stdin


@task
def sync_media():
    _msg('Syncing media from prod')
    local('rsync -avuz --delete {host}:{paths.media}/ {local.media}/'.format(**env.config))


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


@task
def build_settings(dest=False):
    if (dest):
        _build_settings(dest)
    else:
        _build_settings('prod')
        _build_settings('test')


def _build_settings(dest):
    _msg('building settings file for {dest}'.format(dest=dest))
    local('./simple-proc-tpl.sh {local.settings_tpl} {local.private}/settings_{dest}\
           {local.settings_dir}/settings_{dest}.py'.format(
            dest=dest, **env.config))


@task
def build_fabconfig():
    _msg('building {0}'.format(env.config_file))
    _build_fabconfig()


@task
def build_requirements():
    _msg('building requirements file, excluding developer entries')
    local('pip freeze > envreq.txt.tmp && combine envreq.txt.tmp xor envreq-dev.txt > envreq.txt && rm -f envreq.txt.tmp')


@task
def reset_comic_index():
    print red('not implemented')
#SELECT setval('comics_comic_id_seq', max(id)) FROM comics_comic;
#SELECT setval('comics_comic_translation_id_seq', max(id)) FROM comics_comic_translation;
#SELECT setval('comics_normalcomic_id_seq', max(id)) FROM comics_normalcomic;
#SELECT setval('comics_normalcomic_translation_id_seq', max(id)) FROM comics_normalcomic_translation;
