from typing import Dict

import sqlalchemy
from pandas import DataFrame
from sqlalchemy import create_engine

import pandas as pd
from tour_dashboard import utils

def create_mysql_engine(credentials: Dict[str,str]) -> sqlalchemy.engine:
	"""
	Create mysql engine to connect to database
	:param credentials: keys: user, password, host, port, database, table
	:return: sqlalchemy.engine for mysql databases
	"""
	user = credentials["user"]
	password = credentials["password"]
	host = credentials["host"]
	port = credentials["port"]
	database = credentials["database"]
	mysql_dialect = "mysql+pymysql"
	database_url = f"{mysql_dialect}://{user}:{password}@{host}:{port}/{database}"

	engine = create_engine(database_url, echo=False)
	return engine

def create_sqlite_engine(database_path: str) -> sqlalchemy.engine:
	sqlite_database_path = 'sqlite:///' + database_path
	engine = create_engine(sqlite_database_path, echo=False)

	return engine

def load_df_from_database(engine: sqlalchemy.engine, table_name: str) -> DataFrame:
	query = f"SELECT * FROM {table_name}"
	df_table = pd.read_sql_query(query, engine)
	return df_table

def table_exists(engine: sqlalchemy.engine, table_name: str) -> bool:
	# The recommended way to check for existence
	return sqlalchemy.inspect(engine).has_table(table_name)

def write_df_to_database(df: DataFrame, engine: sqlalchemy.engine, table_name: str) -> None:

	if not table_exists(engine, table_name):
		df.to_sql(table_name, con=engine, if_exists='append')
	else:
		# if table exists, load table and check if entry already exists
		df_table = load_df_from_database(engine, table_name)
		entry_exists = utils.entry_exists_in_table_data(df, df_table)

		if entry_exists:
			df.to_sql(table_name, con=engine, if_exists='fail')
		else:
			df.to_sql(table_name, con=engine, if_exists='append')


