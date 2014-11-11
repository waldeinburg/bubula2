import sys
import os
from os import chdir
from os.path import exists
from datetime import datetime
import re
import time
import yaml

from fabric.api import env, task, get, local, run, abort, cd, lcd, prefix
from fabric.colors import yellow, red, green
from fabric.utils import _AttributeDict
from fabric.contrib import files, console, project

from django.core import management
from bubula2 import version as current_project_version

# Allow import of deploy_hooks.py
sys.path.append(os.path.dirname(__file__))

# Fabric native settings
env.use_ssh_config = True
env.colorize_errors = True

# Other
env.config_file = 'fabconfig.yaml'
env.config_file_tpl = 'fabconfig.tpl.yaml'
env.private_data_dir = 'private'
env.config_data_file = 'fabconfig'
env.templates_dir = 'templates'

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


def _run_deploy_hook(dest, hook_str):
    """Run a deploy hook defined in releade_hooks.py if existing
    """
    try:
        import deploy_hooks
    except ImportError:
        return
    try:
        hook_fn = getattr(deploy_hooks, 'hook_' + hook_str)
    except AttributeError:
        return
    _msg('running hook {0}'.format(hook_str))
    hook_fn(dest)


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
    # Compile messages
    with cd(env.config.paths.test.project):
        run('../manage.py compilemessages')
    # Import prod db from backup
    _msg('importing db')
    with cd(env.config.paths.test.git), _env('test'):
        run('zcat {paths.backup_db_latest} | ./manage.py dbshellnp'.format(**env.config))
    # Sync media. Faster than using the backup.
    _msg('syncing media from prod')
    run('rsync -av --delete {paths.prod.media}/ {paths.test.media}/'.format(**env.config))
    # Sync static from local
    _msg('syncing static from local. It is assumed that build_static has been run.')
    project.rsync_project(local_dir=env.config.paths.local.static+'/',
                          remote_dir=env.config.paths.test.static+'/',
                          delete=True,
                          exclude='/.gitignore')
    # Update db
    _msg('updating database')
    with cd(env.config.paths.test.git), _env('test'):
        run('./manage.py syncdb') # Non-South
        _run_deploy_hook('test', 'syncdb__migrate')
        run('./manage.py migrate') # South
    # Restart apache
    restart('test')


def _deploy_prod(env_rebuild, interactive=True):
    if interactive and not console.confirm('Are you sure you want to deploy master branch to production?'):
        return
    # Deploy master
    _msg('deploying master branch to production')
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
    # Compile messages
    with cd(env.config.paths.prod.project):
        run('../manage.py compilemessages')
    # Backup db and media
    backup(False)
    # Update db
    _msg('updating database')
    with cd(env.config.paths.test.git), _env('prod'):
        run('./manage.py syncdb') # Non-South
        _run_deploy_hook('prod', 'syncdb__migrate')
        run('./manage.py migrate') # South
    # Build and upload static files
    build_static()
    _msg('syncing static')
    project.rsync_project(local_dir=env.config.paths.local.static+'/',
                          remote_dir=env.config.paths.prod.static+'/',
                          delete=True,
                          exclude='/.gitignore')
    # Restart apache
    restart('prod')


@task
def release(version, env_rebuild=False):
    """Release: Update version, deploy and push to GitHub master
    """
    print green('Current version is {0}'.format(current_project_version))
    if not console.confirm('Are you sure you want to release version {0}?'.format(version)):
        return
    local('git checkout master')
    _msg('updating version number')
    version_file = '{project}/__init__.py'.format(**env.config)
    local("sed -ri \"s/^version = .*/version = '{version}'/\" {version_file}"
          .format(version=version, version_file=version_file)) 
    local("git commit {version_file} -m 'Updated version to {version}.'"
          .format(version=version, version_file=version_file)) 
    _msg('git tagging with version number')
    local("git tag -a '{0}'".format(version))
    _deploy_prod(env_rebuild, False)
    _msg('pushing master and tag to github')
    repo = env.config.github_repo
    local('git push {0} master'.format(repo))
    local('git push {0} {1}'.format(repo, version))


@task
def rollback(version=None, restore_db='ask', restore_media='ask', backup='latest'):
    """Roll back to previous version (git tag) or a specific one if stated

    Argument 'backup' can be YYMMDD-hhmm (must exist) if latest will not work.
    """
    # Most of this is copied from deploy, sometimes with small modifications
    if not version:
        # List tags and get second last line
        version = local("git tag -l | sed -n '$! h; $ {g; p}' |  tr -d '\\n'", capture=True)
    print green('Current version is {0}'.format(current_project_version))
    if not console.confirm('Are you sure you want to roll back to version {0}?'.format(version),
                           default=False):
        return
    if restore_db == 'ask':
        restore_db = console.confirm('Restore database?', default=False)
    if restore_media == 'ask':
        restore_media = console.confirm('Restore media?', default=False)
    # Get current branch. We'll change back to it in the last step.
    branch = local("git branch | grep '\*' | cut -d' ' -f2", capture=True)
    # Check out tag, also locally for generating settings and static
    _msg('checking out the specified branch')
    local('git checkout {0}'.format(version))
    with cd(env.config.paths.host_git):
        run('export GIT_WORK_TREE={paths.prod.git}; git checkout {version} -f'
            .format(version=version, **env.config))
    # Force rebuild of environment
    with cd(env.config.paths.prod.git):
        _msg('removing old environment')
        run('rm -rf {paths.prod.env}'.format(**env.config))
        _msg('creating environment')
        run('./rebuild_env.sh {paths.prod.env}'.format(**env.config))
    # Generate and upload settings files
    build_settings('prod')
    # Compile messages
    with cd(env.config.paths.prod.project):
        run('../manage.py compilemessages')
    # Restore from backup db and media. 
    if restore_db:
        with cd(env.config.paths.prod.git), _env('prod'):
            run('zcat {paths.backup_db_latest} | ./manage.py dbshellnp'.format(**env.config))
    if restore_media:
        print red('Media restore not implemented!') # TODO; better fix the path in the tarball first
    # We don't need to update db afterwards because it was made in the previous version.
    # Build and upload static files
    build_static()
    _msg('syncing static')
    project.rsync_project(local_dir=env.config.paths.local.static+'/',
                          remote_dir=env.config.paths.prod.static+'/',
                          delete=True,
                          exclude='/.gitignore')
    # Restart apache
    restart('prod')
    # Change back to the branch used
    local('git checkout {0}'.format(branch))


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
    with lcd(env.config.paths.local.static):
        _msg('removing all files in static')
        local('rm -rf *')
    _msg('collecting static')
    local('echo yes | ./manage.py collectstatic')


@task
def backup(download=False):
    """Run db backup, media backup and download if specified
    """
    with cd(env.config.paths.prod.git):
        run('./backup.sh')
    if download:
        download_latest_backup()


@task
def download_latest_backup():
    get(env.config.paths.backup_db_latest, env.config.paths.local.backup_dir)
    get(env.config.paths.backup_media_latest, env.config.paths.local.backup_dir)


@task
def sync_with_prod(from_local_backup=False):
    """Shortcut to import_db_from_prod and sync_media_with_prod
    """
    import_db_from_prod(from_local_backup)
    sync_media_with_prod()


@task
def import_db_from_prod(from_local_backup=False):
    """Import backup to database
    If argument from_local is False (default), import from server, else import from local backup.
    """
    _msg('importing database')
    if from_local_backup:
        local('zcat {paths.local.backup_dir}/{paths.backup_db_latest_filename} | ./manage.py dbshellnp'
              .format(**env.config))
    else:
        # No obvious way of using native run().
        local("ssh {host} 'cat {paths.backup_db_latest}' | gunzip | ./manage.py dbshellnp"
              .format(hostname=env.host, **env.config))


@task
def sync_media_with_prod():
    """Sync local media folder with prod
    Changes will be overwritten (no update).
    """
    _msg('syncing media with prod')
    project.rsync_project(upload=False,
                          remote_dir=env.config.paths.prod.media+'/',
                          local_dir=env.config.paths.local.media+'/',
                          delete=True,
                          exclude='/.gitignore')


@task
def build_translation():
    # http://blog.brendel.com/2010/09/how-to-customize-djangos-default.html
    chdir(env.config.paths.local.project)
    _msg('translating all messages')
    management.call_command('makemessages', all=True)
    _msg('Removing commented-out manual messages')
    local(r"find locale -name 'django.po' -exec sed s/^\#\~\ // -i {} \;")
    _msg('Compiling messages')
    management.call_command('compilemessages')


@task
def build_settings(dest='local'):
    _msg('building settings files for {dest}'.format(dest=dest))
    is_local = (dest == 'local')
    context = dict(env.config, dest=dest)
    _build_from_template('settings.tpl.py', env.config.paths[dest].project, context, is_local=is_local)
    _build_from_template('backup_settings.inc.tpl.sh', env.config.paths[dest].git, context, is_local=is_local)


@task
def build_fabconfig():
    _msg('building {0}'.format(env.config_file))
    _build_fabconfig()


@task
def build_requirements():
    _msg('building requirements file, excluding developer entries')
    local('pip freeze > {paths.env_req}.tmp && combine {paths.env_req}.tmp xor {paths.env_req_dev} > {paths.env_req} && rm -f {paths.env_req}.tmp'
          .format(**env.config))
    # Check for conflicts. Git lines ('-e git+...) will not work but not fail.
    _msg('Checking conflicts (normal packages only). Conflicts will result in two errors.')
    main_file = open(env.config.paths.env_req)
    dev_file = open(env.config.paths.env_req_dev)
    for d_ln in dev_file:
        d_pkg = d_ln[:d_ln.find('=')]
        for m_ln in main_file:
            m_pkg = m_ln[:m_ln.find('=')]
            if (m_pkg == d_pkg):
                print red('Conflict: {0} - {1}'.format(d_ln[:-1], m_ln[:-1]))
        main_file.seek(os.SEEK_SET)


@task
def reset_comic_index():
    print red('not implemented')
# Can we just use sqlsequencereset?
#SELECT setval('comics_comic_id_seq', max(id)) FROM comics_comic;
#SELECT setval('comics_comic_translation_id_seq', max(id)) FROM comics_comic_translation;
#SELECT setval('comics_normalcomic_id_seq', max(id)) FROM comics_normalcomic;
#SELECT setval('comics_normalcomic_translation_id_seq', max(id)) FROM comics_normalcomic_translation;
