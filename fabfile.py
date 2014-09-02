import sys
from os import chdir
from os.path import exists
from datetime import datetime
import re
import time
import yaml
from fabric.api import env, task, get, local, run, abort, cd, lcd, prefix
from fabric.colors import yellow, red
from fabric.utils import _AttributeDict
from fabric.contrib import files, console
from django.core import management

# Fabric native settings
env.use_ssh_config = True
env.colorize_errors = True

# Other
env.config_file = 'fabconfig.yaml'
env.config_file_tpl = 'fabconfig.tpl.yaml'
env.private_data_dir = 'private'
env.config_data_file = 'fabconfig'
env.templates_dir = 'templates'
env.releaseTS = int(round(time.time()))
env.release = datetime.fromtimestamp(env.releaseTS).strftime('%y%m%d%H%M%S')

def _msg(msg):
    print yellow('>>> ' + msg)


def _env(name):
    path = env.config.paths[name].env
    return prefix('. {0}/bin/activate'.format(path))


def _build_from_template(template, directory, context=None, is_local=False, filename=None):
    """Builds a file from a Jinja2 template either locally or remote
    """
    if not context:
        context = env.config
    if not filename:
        re_filename = re.compile(r'\.tpl((.[^.]+)?)$')
        filename = re_filename.sub(r'\1', template)
    file_path = '{0}/{1}'.format(directory, filename)
    if is_local:
        from jinja2 import Environment, FileSystemLoader
        j_env = Environment(loader=FileSystemLoader(env.templates_dir))
        f = open(file_path, 'w')
        f.write(j_env.get_template(template).render(**context))
        f.close()
    else:
        files.upload_template(template, file_path,
                              context=context, template_dir=env.templates_dir, use_jinja=True, backup=False)


def _build_fabconfig():
    local('./simple-proc-tpl.sh {templates_dir}/{config_file_tpl} {private_data_dir}/{config_data_file} {config_file}'.format(**env))


def _setup():
    def _wrap_dict(d):
        d = _AttributeDict(d)
        for k in d:
            if isinstance(d[k], dict):
                d[k] = _wrap_dict(d[k])
        return d

    def _format_dict(d, top=None):
        if not top:
            top = d
        process_again = True
        while process_again:
            process_again = False
            for k in d:
                if isinstance(d[k], str):
                    d[k] = d[k].format(**top)
                    if d[k].find('{') != -1:
                        process_again = True
                elif isinstance(d[k], dict):
                    _format_dict(d[k], top)
    
    # Load config file
    if not exists(env.config_file):
        _msg('fabconfig.yaml not found. Attempt to build from template ...')
        _build_fabconfig()
    config_file = open(env.config_file, 'r')
    env.config = yaml.safe_load(config_file.read())
    config_file.close()
    # Wrap config recursively
    env.config = _wrap_dict(env.config)

    # Set hosts from config file
    env.hosts = [ env.config.host ]

    # Format paths, allowing references
    _format_dict(env.config.paths)
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
        outpath_components = get_file_base_and_extension(bundle_path)
        minified_path = '{0}.min{1}'.format(outpath_components[0], outpath_components[1])
        local('java -jar {paths.yuicompressor} -v -o "{out_file}" --charset utf-8 "{in_file}"'.format(
                  out_file=minified_path, in_file=bundle_path, **env.config))


@task
def deploy(dest, env_rebuild=False):
    dests = {
        'prod': _deploy_prod,
        'test': _deploy_test
    }
    dests[dest](env_rebuild) # will fail if wrong destination is given


def _deploy_test(env_rebuild):
    # Deploy current branch
    branch = local("git branch | grep '\*' | cut -d' ' -f2", capture=True)
    local('git push {host_git_repo} {branch}'.format(branch=branch, **env.config))
    with cd(env.config.paths.host_git):
        run('export GIT_WORK_TREE={paths.test.git}; git checkout {branch} -f'.format(branch=branch, **env.config))
    # Update environment
    with cd(env.config.paths.test.git):
        if (not env_rebuild and files.exists(env.config.paths.test.env)):
            with _env('test'):
                _msg('updating environment')
                run('pip install -r envreq.txt')
        else:
            if env_rebuild:
                _msg('removing old environment')
                run('rm -rf {paths.test.env}'.format(**env.config))
            _msg('creating environment')
            run('./rebuild_env.sh {paths.test.env}'.format(**env.config))
    # Generate and upload settings files
    build_settings('test')
    # Import prod db from backup
    _msg('importing db')
    with cd(env.config.paths.test.git), _env('test'):
        run('zcat {paths.backup_db_latest} | ./manage.py dbshell'.format(**env.config))
    # Sync media. Faster than using the backup.
    _msg('syncing media from prod')
    run('rsync -av --delete {paths.prod.media}/ {paths.test.media}/'.format(**env.config))
    # Sync static from local
    _msg('syncing static from local. It is assumed that build_static has been run.')
    local('rsync -av --delete {paths.local.static}/ {host}:{paths.test.static}/'.format(**env.config))
    # Update db
    _msg('updating database')
    with cd(env.config.paths.test.git), _env('test'):
        run('./manage.py syncdb') # Non-South
        run('./manage.py migrate') # South
    # Restart apache
    restart('test')


def _deploy_prod(env_rebuild):
    if not console.confirm('Are you sure you want to deploy master branch to production?'):
        return
    # Deploy master
    local('git push {host_git_repo} master'.format(**env.config))
    with cd(env.config.paths.host_git):
        run('export GIT_WORK_TREE={paths.prod.git}; git checkout master -f'.format(**env.config))
    # Update environment
    with cd(env.config.paths.prod.git):
        if (not env_rebuild and files.exists(env.config.paths.prod.env)):
            with _env('prod'):
                _msg('updating environment')
                run('pip install -r envreq.txt')
        else:
            if env_rebuild:
                _msg('removing old environment')
                run('rm -rf {paths.prod.env}'.format(**env.config))
            _msg('creating environment')
            run('./rebuild_env.sh {paths.prod.env}'.format(**env.config))
    # Generate and upload settings files
    build_settings('prod')
    # Backup db and media
    backup(False)
    # Update db
    _msg('updating database')
    with cd(env.config.paths.test.git), _env('prod'):
        run('./manage.py syncdb') # Non-South
        run('./manage.py migrate') # South
    # Build and upload static files
    build_static()
    _msg('syncing static')
    local('rsync -av --delete {paths.local.static}/ {host}:{paths.proc.static}/'.format(**env.config))
    # Restart apache
    restart('prod')
    
    return
    #TODO: tag and release, also on github
    _msg('updating release ID and timestamp')
    local('sed -ri "'+r"s/^(release = )'(.*?)'$/\1'{release}'/; s/^(releaseTS = )([0-9]+)$/\1{releaseTS}/"+'" {project}/__init__.py'.format(project=env.config.default['project'], **env))


@task
def restart(dest):
    _msg('restarting {0} server'.format(dest))
    # Run restart command and sleep for one second.
    # The start seemed to fail because of the disconnect for some reason.
    run('{0} && sleep 1'.format(env.config.paths[dest].restart))


@task
def stop_test():
    _msg('stopping test server')
    run(env.config.paths.test.stop)


@task
def recollect_static():
    # This only makes sense to do on local.
    # On remote we should sync with a build.
    with lcd(env.config.local.static):
        _msg('removing all files in static')
        local('rm -rf *')
    _msg('collecting static')
    local('echo yes | ./manage.py collectstatic')


def _recollect_static_test():
    print red('not implemented!')
    return
    _msg('collecting static')
    with cd(env.path.format(**env)):
        res = run('. {pyenv}/bin/activate; echo yes | python {project}/manage.py collectstatic')
        print res.stdout


@task
def backup(download=False):
    """Run db backup, media backup and download if specified
    """
    with cd(env.config.paths.prod.git):
        run('./backup.sh')
    if download:
        get(env.config.paths.backup_db_latest, env.config.paths.local.backup_dir)
        get(env.config.paths.backup_media_latest, env.config.paths.local.backup_dir)


@task
def sync_media():
    _msg('Syncing media from prod')
    local('rsync -avuz --delete {host}:{paths.prod.media}/ {paths.local.media}/'.format(**env.config))


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
def build_settings(dest='local'):
    _msg('building settings files for {dest}'.format(dest=dest))
    is_local = (dest == 'local')
    context = dict(env.config, dest=dest)
    if is_local:
        _build_from_template('settings_local.tpl.py', env.config.project, is_local=True)
    else:
        _build_from_template('settings.tpl.sh', env.config.paths[dest].project, context)
    _build_from_template('backup_settings.inc.tpl.sh', env.config.paths[dest].git, context, is_local=is_local)


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
