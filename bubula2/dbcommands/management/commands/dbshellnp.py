import os
import stat
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, DEFAULT_DB_ALIAS

class Command(BaseCommand):
    """A copy of the native dbshell command removing need for password for PostgreSQL"""
    help = ("Runs the command-line client for specified database, or the "
        "default database if none is provided. No password.")

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database onto which to '
                'open a shell.  Defaults to the "default" database.'),
        make_option('--pgpass-file', dest='pgpass_file', default='./.pgpass',
                    help='PostgreSQL only. Name of the temporary '
                        '(unless existing) password file (defaults to ./.pgpass)'),
        make_option('--psql-tmp-script', dest='psql_tmp_script', default='./__dbshellnp_psql.sh',
                    help='PostgreSQL only. Name of the temporary script to '
                        'create if pgpass is temporary'),
    )

    requires_model_validation = False
    pgpass_tmp_created = False

    def handle(self, **options):
        self.db_alias = options.get('database')
        self.pgpass_file = options.get('pgpass_file')
        self.psql_tmp_script = options.get('psql_tmp_script')
        self.connection = connections[self.db_alias]

        engine = self.connection.settings_dict['ENGINE']
        if engine == 'django.db.backends.postgresql_psycopg2' or engine == 'django.db.backends.postgresql':
            self.__runshell_postgresql()
        else:
            self.__runshell()

    def __runshell(self):
        
        try:
            self.connection.client.runshell()
        except OSError:
            # Note that we're assuming OSError means that the client program
            # isn't installed. There's a possibility OSError would be raised
            # for some other reason, in which case this error message would be
            # inaccurate. Still, this message catches the common case.
            raise CommandError('You appear not to have the %r program installed or on your path.' % \
                self.connection.client.executable_name)

    def __runshell_postgresql(self):
        if not os.path.exists(self.pgpass_file):
            umask = os.umask(00066)

            # Create the pgpass file.
            f = open(self.pgpass_file, 'w')
            self.pgpass_tmp_created = True
            settings_dict = self.connection.settings_dict
            host = settings_dict['HOST'] if settings_dict['HOST'] else '*'
            port = settings_dict['PORT'] if settings_dict['PORT'] else '*'
            name = settings_dict['NAME']
            user = settings_dict['USER'] if settings_dict['USER'] else '*'
            password = settings_dict['PASSWORD']
            f.write('{0}:{1}:{2}:{3}:{4}'.format(host, port, name, user, password))
            f.close()

            # Create a script that will delete the temporary pgpass file.
            # This is necessary because runshell will replace the process with os.execvp.
            #umask = os.umask(00077)
            f = open(self.psql_tmp_script, 'w')
            f.write('''#!/bin/bash
                trap "rm -f '{0}' '{1}'" EXIT
                echo "executing psql"
                psql "$@"
            '''.format(self.psql_tmp_script, self.pgpass_file))
            f.close()
            os.chmod(self.psql_tmp_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            self.connection.client.executable_name = self.psql_tmp_script

            os.umask(umask)
        os.environ['PGPASSFILE'] = self.pgpass_file

        self.__runshell()
