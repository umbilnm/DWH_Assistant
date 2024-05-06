from typing import List, Dict
import os
from dotenv import load_dotenv
import psycopg2 as pg2
import pandas as pd
load_dotenv()

def execute_sql_query(sql_query:str) -> Dict[pd.DataFrame, str]:
    """
    Executes an SQL query in Postgres database and returns the results in a dictionary.

    Parameters
    ----------
    sql_query : str
        SQL query string.

    Returns
    -------
    dict
        A dictionary with two keys 
        - 'result' as a pandas DataFrame containing the query results, 
        - 'error' with an error message if the execution failed.
    """
    host = os.getenv("PG_STUDENT_HOST")
    port = os.getenv("PG_STUDENT_PORT")
    dbname = os.getenv("PG_STUDENT_DBNAME")
    user = os.getenv("PG_STUDENT_USER")
    password = os.getenv("PG_STUDENT_PASSWORD")
    conn = pg2.connect(dbname=dbname, user=user, password=password, \
                       host=host, port=port)
    try:
        df = pd.read_sql_query(sql_query, conn)
        return {'result': df, 'error': None}
    except Exception as e:
        print(e)
        return {'result': None, 'error': e}


def build_dbml_schema(table_names:List[str]) -> str:
    """
    Generates a DBML schema for specified tables 
    in a PostgreSQL database schema using a static SQL query. 
    This version formats the output as per the provided DBML schema example,
    replacing 'double precision' data type with 'double' 
    for dbdiagram.io compatibility.

    Parameters
    ----------
    table_names : list
        List of table names for which the DBML schema should be generated.

    Returns
    -------
    str
        DBML schema as a string for the specified tables in the schema.
    """
    types_dict = {'double precision': 'double', 'character varying':'varchar',
                  'integer' : 'int', 'timestamp without time zone':'timestamp'}
    query = '''
            SELECT 
                table_name, 
                column_name, 
                data_type
            FROM information_schema.columns
            WHERE 
                table_schema = 'public'
                AND table_name IN ({table_names_str})
            ORDER BY table_name, ordinal_position;
            '''
    dbml_scheme = ''    
    result = execute_sql_query(query.format(table_names_str=str(table_names)[1:-1]))
    df, error = result['result'], result['error']
    tables = df['table_name'].unique()
    if error:
        return error

    for table in tables:
        dbml_scheme += f'Table {table} {{\n'
        cur_df_list = df[df['table_name'] == table][['column_name', 'data_type']].values
        for row in cur_df_list:
            val = types_dict.get(row[1], row[1])
            dbml_scheme += f'   {row[0]} {val}\n'
        dbml_scheme += '}\n\n'
    return dbml_scheme