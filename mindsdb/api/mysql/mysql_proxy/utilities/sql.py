import duckdb
from mindsdb_sql import parse_sql
from mindsdb_sql.parser.ast import Select, Identifier, BinaryOperation, OrderBy


def _remove_table_name(root):
    if isinstance(root, BinaryOperation):
        _remove_table_name(root.args[0])
        _remove_table_name(root.args[1])
    elif isinstance(root, Identifier):
        root.parts = [root.parts[-1]]


def query_df(df, query):
    """ Perform simple query ('select' from one table, without subqueries and joins) on DataFrame.

        Args:
            df (pandas.DataFrame): data
            query (mindsdb_sql.parser.ast.Select | str): select query

        Returns:
            pandas.DataFrame
    """

    query = parse_sql(str(query), dialect='mysql')
    if isinstance(query, Select) is False or isinstance(query.from_table, Identifier) is False:
        raise Exception("Only 'SELECT from TABLE' statements supported for internal query")

    query.from_table.parts = ['df_table']
    for identifier in query.targets:
        if isinstance(identifier, Identifier):
            identifier.parts = [identifier.parts[-1]]
    if isinstance(query.order_by, list):
        for orderby in query.order_by:
            if isinstance(orderby, OrderBy) and isinstance(orderby.field, Identifier):
                orderby.field.parts = [orderby.field.parts[-1]]
    _remove_table_name(query.where)

    res = duckdb.query_df(df, 'df_table', str(query))
    result_df = res.df()
    return result_df
