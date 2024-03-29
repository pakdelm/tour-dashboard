# content of test_sample.py

import pytest
from gpxpy.gpx import GPXTrackPoint
import datetime
import pandas as pd
from gpxpy.gpxfield import SimpleTZ
from pandas._testing import assert_frame_equal

from tour_dashboard import data_processing, utils, statistics

# test case read_gpx_data and create_dataframe
read_data_path = "../tests/test_resources/gpx_read_data.gpx"
gpx_data_source = data_processing.read_gpx_data(read_data_path)
df_create_from_gpx = data_processing.create_dataframe_from_gpx_data(gpx_data_source)

# test case compute tour distances and speed
path = "../tests/test_resources/gpx_distances.gpx"
gpx_data = data_processing.read_gpx_data(path)
df_input = data_processing.create_dataframe_from_gpx_data(gpx_data)
df_distances = data_processing.compute_tour_distances(df_input, gpx_data)

@pytest.mark.parametrize("input_path, expected", [
    (utils.create_os_independent_path(r"..\data\Rennradtour_03_04_2021_12_06.gpx"),
     "F5612EC0C11BF663B7AD749BD2E61E83".lower()),
    (utils.create_os_independent_path(r"..\data\Rennradtour_04_04_2021_15_43.gpx"),
     "0DF3D75C72379F98125ADC40DDBDE092".lower())
])
def test_create_md5_hash_code(input_path, expected):
    assert data_processing.create_md5_hash_code(input_path) == expected

def test_read_gpx_data():
    expected = type([GPXTrackPoint(10.1,
                                   10.1,
                                   elevation=510.0,
                                   time=datetime.datetime(2021, 4, 18, 20, 0, tzinfo=SimpleTZ("Z")))])

    assert type(gpx_data_source) == expected

def test_create_dataframe_from_gpx_data():
    df_expected = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
    df_expected = df_expected.append({'lon': 10.1,
                    'lat' : 10.1,
                    'alt' : 510.0,
                    'time' : datetime.datetime(2021, 4, 18, 20, 0, tzinfo=SimpleTZ("Z"))\
                                     .replace(tzinfo=None, microsecond=0)},
                                      ignore_index=True)

    assert_frame_equal(df_create_from_gpx, df_expected)

def test_compute_tour_distances():
    distance_km, time_min, altitude_gain, altitude_loss = statistics.\
                                                            get_distance_metrics_from_dataframe(df_distances)

    assert(distance_km) == 22.6
    assert(time_min) == 69
    assert(altitude_loss) == pytest.approx(40, 1)
    assert(altitude_gain) == pytest.approx(110, 5)

def test_calculate_speed():
    df_moving = statistics.filter_for_moving_times(df_distances)
    df_speed = data_processing.calculate_speed(df_moving)

    average_speed = statistics.get_average_speed_from_dataframe(df_speed)
    print(average_speed)
    assert(average_speed) == pytest.approx(22, 0.3)

def test_get_tour_name_from_gpx_data():
    tour_name = data_processing.get_tour_name_from_gpx_data(read_data_path)
    assert(tour_name) == 'GPX Test 18.04.2021 20:20'