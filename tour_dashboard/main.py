from tour_dashboard import utils, data_processing, database
import pandas as pd

pd.set_option("display.max_columns", None)


directory = "../data"
gpx_extension = ".gpx"
database_path = '../data/data_concat.db'

resources = "../resources"
credentials_path = f"{resources}/mysql_credentials.json"

table_name = 'test_table_v01'
user_name = "user1"

write_to_table = True
print_table = True

if __name__ == "__main__":

	credentials = utils.parse_json(credentials_path)
	mysql_engine = database.create_mysql_engine(credentials)

	if write_to_table:
		gpx_files = utils.create_file_paths_with_extension(directory, gpx_extension)

		for file_path in gpx_files:
			df_to_write = data_processing.prepare_gpx_data_for_database(file_path, user_name)

			print(df_to_write.head(50))

			database.write_df_to_database(df_to_write, mysql_engine, table_name)

	if print_table:
		df_table = database.load_df_from_database(mysql_engine, table_name)

		print(df_table.head(50))
		print(len(df_table.index))
		print(df_table.tour_name.unique())
