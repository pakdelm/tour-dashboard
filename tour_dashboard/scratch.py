from datetime import datetime

from gpxpy.gpxfield import SimpleTZ

from tour_dashboard import data_processing

import pandas as pd

gpx_test_path = "../tests/test_resources/gpx_read_data.gpx"
gpx_test_data = data_processing.read_gpx_data(gpx_test_path)

df = data_processing.create_dataframe_from_gpx_data(gpx_test_data)

df_expected = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
df_expected = df_expected.append({'lon': 10.1,
                    'lat' : 10.1,
                    'alt' : 510.0,
                    'time' : datetime(2021, 4, 18, 20, 0, tzinfo=SimpleTZ("Z")).replace(tzinfo=None, microsecond=0)},
                    ignore_index=True)

print(df_expected.head(10))