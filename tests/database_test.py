import pytest
import pandas as pd
from sqlalchemy import create_engine

from tour_dashboard import data_processing, database

path = "../data/2021-04-11_346102736_Rennradtour 11.04.2021 14 38.gpx"
database_path = '../data/data.db'
table_name = 'tour_data'

def test_write_df_to_database():
	df_to_write = data_processing.prepare_gpx_data_for_database(path)
	database.write_df_to_database(df_to_write, database_path, 'tour_data')

	sqlite_database_path = 'sqlite:///' + database_path
	engine = create_engine(sqlite_database_path, echo=False)

	query = f"SELECT * FROM {table_name}"
	df_table = pd.read_sql_query(query, engine)

	print(df_table.head(50))
	print(len(df_table.index))