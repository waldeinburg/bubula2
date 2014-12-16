from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.db import connections, DEFAULT_DB_ALIAS
from bubula2.dbcommands.management.sql import sql_drop_all_tables

class Command(NoArgsCommand):
    help = "Returns a list of the SQL statements required to drop all tables in the database."

    option_list = NoArgsCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to print the '
                'SQL for.  Defaults to the "default" database.'),
    )

    output_transaction = True

    def handle_noargs(self, **options):
        return u'\n'.join(sql_drop_all_tables(connections[options.get('database')])).encode('utf-8')
