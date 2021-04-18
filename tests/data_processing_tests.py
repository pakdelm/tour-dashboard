# content of test_sample.py
import pytest
from gpxpy.gpx import GPXTrackPoint
import datetime
import pandas as pd
from gpxpy.gpxfield import SimpleTZ
from pandas._testing import assert_frame_equal

from tour_dashboard import data_processing, utils

TEST_DATA_PATH = "../tests/test_resources/gpx_read_data.gpx"
GPX_DATA_SOURCE = data_processing.read_gpx_data(TEST_DATA_PATH)
CREATE_DF_SOURCE = data_processing.create_dataframe_from_gpx_data(GPX_DATA_SOURCE)

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

    assert type(GPX_DATA_SOURCE) == expected

def test_create_dataframe_from_gpx_data():
    df_expected = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
    df_expected = df_expected.append({'lon': 10.1,
                    'lat' : 10.1,
                    'alt' : 510.0,
                    'time' : datetime.datetime(2021, 4, 18, 20, 0, tzinfo=SimpleTZ("Z"))\
                                     .replace(tzinfo=None, microsecond=0)},
                                      ignore_index=True)

    assert_frame_equal(CREATE_DF_SOURCE, df_expected)