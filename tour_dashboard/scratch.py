from datetime import datetime

import gpxpy
from gpxpy.gpxfield import SimpleTZ

from tour_dashboard import data_processing, statistics, utils, database

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# path = "../data/Rennradtour_03_04_2021_12_06.gpx"
#
# df = data_processing.prepare_gpx_data_for_database(path)
#
# distance_km, time_min, altitude_gain, altitude_loss = statistics.get_distance_metrics_from_dataframe(df)
#
# print(distance_km, time_min, altitude_gain, altitude_loss)
# print(df.head(50))
# print(df.hash_id.unique())
#
# df_write_id = df.hash_id.unique()
# df_table_id = ["f5612ec0c11bf663b7ad749bd2e61e83", "f5612ec0c11bf663b7ad749bd2e61e83", "99999"]
#
# check = any(item in df_write_id for item in df_table_id)
# print(check)

directory = "../data"
gpx_extension = ".gpx"
database_path = '../data/data.db'
table_name = 'tour_data'

df = database.load_df_from_database(database_path, table_name)
df_date = statistics.truncate_to_date(df, 'time', 'date')

hash_ids = df_date.hash_id.unique()

#for id in hash_ids:
df_filtered = df_date[df_date['hash_id'] == "f5612ec0c11bf663b7ad749bd2e61e83"].copy()

distance_km, time_min, altitude_gain, altitude_loss = statistics.get_distance_metrics_from_dataframe(df_filtered)
avg_speed = statistics.get_average_speed_from_dataframe(df_filtered)
date = df_filtered['date'].iloc[0]

print(date)
print(type(date))
# create empty rows_list for dataframe creation
rows_list = []
# initialise an empty dict
row_dict = {}
# row_dict.update({'created': file_created_ts})
#
# rows_list.append(row_dict)
# # create dataframe from rows_list
# df_stats = pd.DataFrame(rows_list, columns=['created','file','size','path','hash'])

print(distance_km, time_min, altitude_gain, altitude_loss, avg_speed)

print(df_filtered.head(50))
# print(df_filtered.hash_id.unique())