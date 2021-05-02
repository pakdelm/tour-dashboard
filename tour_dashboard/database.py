import sqlalchemy
from pandas import DataFrame
from sqlalchemy import create_engine

import pandas as pd
from tour_dashboard import utils

def create_sqlite_engine(database_path: str) -> sqlalchemy.engine:
	sqlite_database_path = 'sqlite:///' + database_path
	engine = create_engine(sqlite_database_path, echo=False)

	return engine

def load_df_from_database(database_path: str, table_name: str) -> DataFrame:
	engine = create_sqlite_engine(database_path)
	query = f"SELECT * FROM {table_name}"
	df_table = pd.read_sql_query(query, engine)
	return df_table

def write_df_to_database(df: DataFrame, database_path: str, table_name: str) -> None:

	engine = create_sqlite_engine(database_path)

	if utils.file_exists(database_path):
		df_table = load_df_from_database(database_path, table_name)
		entry_already_exists = utils.entry_exists_in_table_data(df, df_table)
	else:
		# if database does not exist, entry does not exist either and is False
		entry_already_exists = False

	if entry_already_exists:
		pass
	else:
		# write to table
		df.to_sql(table_name, con=engine, if_exists='append')

