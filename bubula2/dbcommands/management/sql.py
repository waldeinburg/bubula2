def sql_drop_all_tables(connection):
    tables = connection.introspection.table_names()
    qn = connection.ops.quote_name
    statements = ['DROP TABLE {0} CASCADE'.format(qn(t)) for t in tables]
    return statements
