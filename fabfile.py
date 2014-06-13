from fabric.api import env, task, local, run, cd, abort
from fabric.colors import yellow, red
from datetime import datetime
import time

env.colors = True
env.format = True
env.config_file = 'fabconfig.yaml'
env.releaseTS = int(round( time.time() ))
env.release = datetime.fromtimestamp(env.releaseTS).strftime('%y%m%d%H%M%S')
env.optimizeImages = False
env.yuicompressorPath = '/usr/local/bin/yuicompressor-2.4.7.jar'

# This is taken from
# https://github.com/tkopczuk/one_second_django_deployment/blob/master/fabfile.py
# Removed S3 and gzipping and adopted to coding style
@task
def buildstatic():
    print yellow('>>> collecting static')
    local('echo yes | env python manage.py collectstatic', capture=False)
    
    print yellow('>>> building static')
    def get_file_base_and_extension(filename):
        if filename.count('.'):
            return '.'.join( filename.split('.')[:-1] ), '.{0}'.format( filename.split('.')[-1] )
        else:
            return filename, ''
    
    # bundle
    for bundlePath in env.config.default['bundle_and_minify']:
        with open(bundlePath, 'w') as outfile:
            for libpath in env.config.default['bundle_and_minify'][bundlePath]:
                with open(libpath, 'r') as libfile:
                    outfile.write( libfile.read() )
        # this replaces the large code block below for our purposes
        outpathComponents = get_file_base_and_extension(bundlePath)
        minifiedPath = '{0}.min{1}'.format(outpathComponents[0], outpathComponents[1])
        local('java -jar {yuicompressor} -v -o "{outFile}" --charset utf-8 "{inFile}"'.format(yuicompressor=env.yuicompressorPath, outFile=minifiedPath, inFile=bundlePath), capture=False )

        # The following from Ask The Pony will minify all js and css in static.
        # But what is the point of this without altering apps to include them?
        # Outcomment for now.
#    interestingExtensions = set(['.js', '.css'])
#    if env.optimizeImages:
#        interestingExtensions.update(set(['.png', '.jpg', '.jpeg']))
#
#    # get list of files to handle
#    dirList = list( os.walk(env.config.default['staticRelativeDir']) )
#    filesSet = set()
#    for directory in dirList:
#        filesSet.update(set([
#            get_file_base_and_extension( os.path.join(directory[0], d) )
#                for d in directory[2]
#                    if get_file_base_and_extension(d)[1] in interestingExtensions
#                        and not get_file_base_and_extension(d)[0][-4:] == '.min' # .count('.min') is inaccurate. This method does not yield errors on short strings.
#        ]))
#
#    # compress files
#    filesNo = len(filesSet)
#    for index, (fileBasename, fileExtension) in enumerate(filesSet):
#        print green( '{part:.1%} done ({index}/{filesNo})'.format( part=(index+1.)/filesNo, index=index+1, filesNo=filesNo) )
#        originalPath = '{0}{1}'.format(fileBasename, fileExtension)
#        minifiedPath = '{0}.min{1}'.format(fileBasename, fileExtension)
#
#        if fileExtension in ['.png']:
#            local( 'pngcrush -rem gAMA -rem cHRM -rem iCCP -rem sRGB -rem alla -rem text -reduce -brute "{0}" "{1}"'.format(originalPath, minifiedPath) )
#            try:
#                print yellow( '\tcompressed {0}'.format(os.path.getsize(originalPath)) + ' => {0}'.format(os.path.getsize(minifiedPath)) + " => {0:.0%}".format(os.path.getsize(minifiedPath) / os.path.getsize(originalPath)) )
#            except OSError:
#                print red( 'File {0} is not a PNG file.'.format(originalPath) )
#        elif fileExtension in ['.jpg', '.jpeg']:
#            local( 'jpegtran -outfile "{outFile}" -optimize -copy none "{inFile}"'.format(outFile=minifiedPath, inFile=originalPath) )
#            try:
#                print yellow( '\tcompressed {0}'.format(os.path.getsize(originalPath)) + ' => {0}'.format(os.path.getsize(minifiedPath)) + " => {0:.0%}" % (os.path.getsize(minifiedPath) / os.path.getsize(originalPath)) )
#            except OSError:
#                print red( 'File {0} is not a JPEG file.'.format(originalPath) )
#        elif fileExtension in ['.js', '.css']:
#            local('java -jar {yuicompressor} -v -o "{outFile}" --charset utf-8 "{inFile}"'.format(yuicompressor=env.yuicompressorPath, outFile=minifiedPath, inFile=originalPath) )


@task('app-servers')
def deploy():
    print yellow('>>> generating dummy config-file for the public')
    # hack
    local(r'sed -r "s/ [a-z0-9]+.webfaction.com/ my_server/; s/(( +)(user|appsPath|password))\:.*/\1: my_\3/" {config_file} > fabconfig-dummy.yaml')
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
    local( 'rsync -avuz --delete {staticRelativeDir}/ {user}@{host_string}:{static}/'.format(**env), capture=False )


@task('app-servers')
def restart():
    env().multirun(_restart)


def _restart():
    print yellow('>>> restarting server')
    res = run( env.restart.format(**env) )
    print res.stderr


@task
def recollectstatic():
    with cd(env.config.default['staticRelativeDir']):
        print yellow('>>> removing all files in static')
        local('rm -r *')
    print yellow('>>> collecting static')
    # FIXME: even when using virtualenv, statics are collected from dist-packages.
    # Find a secure way to sync with server environment
    print red('>>> warning: remember that things will go wrong if local and server environment is not the same!')
    local('echo yes | python manage.py collectstatic')


@task('app-servers')
def remotecollectstatic():
    env().multirun(_remote_collect_static)


def _remote_collect_static():
    print yellow('>>> collecting static')
    with cd( env.path.format(**env) ):
        res = run('. {pyenv}/bin/activate; echo yes | python {project}/manage.py collectstatic')
        print res.stdout
