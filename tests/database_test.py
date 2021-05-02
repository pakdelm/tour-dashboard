import pytest
from tour_dashboard import data_processing, database

path = "../tests/test_resources/gpx_distances.gpx"
database_path = '../tests/test_resources/test_data.db'
table_name = 'tour_data'

def test_write_df_to_database():
	df_to_write = data_processing.prepare_gpx_data_for_database(path)

	# repeat data writing 3 x to ensure that duplicate assertion is correct
	for i in range(0, 3):
		database.write_df_to_database(df_to_write, database_path, table_name)

	df_table = database.load_df_from_database(database_path, table_name)

	assert len(df_to_write.index) == len(df_table.index)