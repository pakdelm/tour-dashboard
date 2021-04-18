# content of test_sample.py
import pytest

from tour_dashboard import data_processing, utils

@pytest.mark.parametrize("input_path, expected", [
    (utils.create_os_independent_path(r"..\data\Rennradtour_03_04_2021_12_06.gpx"),
     "F5612EC0C11BF663B7AD749BD2E61E83".lower()),
    (utils.create_os_independent_path(r"..\data\Rennradtour_04_04_2021_15_43.gpx"),
     "0DF3D75C72379F98125ADC40DDBDE092".lower())
])
def test_create_md5_hash_code(input_path, expected):
    assert data_processing.create_md5_hash_code(input_path) == expected

gpx_test_path = "test_resources/gpx_test.gpx"
gpx_test_data = data_processing.read_gpx_data(gpx_test_path)

print(gpx_test_data)
print(type(gpx_test_data))