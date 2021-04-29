from datetime import datetime

import gpxpy
from gpxpy.gpxfield import SimpleTZ

from tour_dashboard import data_processing, statistics

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

path = "../data/Rennradtour_03_04_2021_12_06.gpx"

df = data_processing.prepare_gpx_data_for_database(path)

distance_km, time_min, altitude_gain, altitude_loss = statistics.get_distance_metrics_from_dataframe(df)

print(distance_km, time_min, altitude_gain, altitude_loss)
print(df.head(50))
print(df.hash_id.unique())

df_write_id = df.hash_id.unique()
df_table_id = ["f5612ec0c11bf663b7ad749bd2e61e83", "f5612ec0c11bf663b7ad749bd2e61e83", "99999"]

check = any(item in df_write_id for item in df_table_id)
print(check)