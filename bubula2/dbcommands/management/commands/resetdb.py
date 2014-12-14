from optparse import make_option

from django.db import connections, transaction, DEFAULT_DB_ALIAS
from django.core.management.base import NoArgsCommand, CommandError
from django.core.management.color import no_style
from bubula2.dbcommands.management.sql import sql_drop_all_tables

# Based on flush.
class Command(NoArgsCommand):
    """Reset database (drop all tables)!"""
    help = ("Reset (drop/create database if allowed, else drop all tables) the specified database,"
        " or the default database if none is provided. ONLY IMPLEMENTED WITH DROP ALL TABLES!")

    option_list = NoArgsCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to reset. '
                'Defaults to the "default" database.'),
    )

    def handle(self, **options):
        db = options.get('database')
        connection = connections[db]
        interactive = options.get('interactive')

        sql_list = sql_drop_all_tables(connection)

        if interactive:
            confirm = raw_input("""You have requested a reset of the database.
This will IRREVERSIBLY DESTROY all data currently in the {0} database.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """.format(connection.settings_dict['NAME']))
        else:
            confirm = 'yes'
            # To check for DROP/CREATE DATABASE priviledges in PostGreSQL, probably do:
            # (for DROP:) SELECT has_database_privilege(user, database, 'create');
            # (for CREATE:) SELECT has_schema_privilege(user, 'pg_catalog', 'create');
            # Could also do DROP SCHEMA public CASCADE if one had priviledges.
            # Other approach: just try, but what if one has DROP but not CREATE priviledges?

        if confirm == 'yes':
            try:
                cursor = connection.cursor()
                for sql in sql_list:
                    cursor.execute(sql)
            except Exception, e:
                transaction.rollback_unless_managed(using=db)
                raise CommandError("""Database {0} couldn't be reset. Possible reasons:
  * The database isn't running or isn't configured correctly.
  * The SQL was invalid.
Hint: Look at the output of 'django-admin.py sqlresetdb'. That's the SQL this command wasn't able to run.
The full error: {1}""".format(connection.settings_dict['NAME'], e))
            transaction.commit_unless_managed(using=db)
        else:
            print "Reset cancelled."
 
