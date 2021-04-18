from tour_dashboard import utils

def test_create_os_independent_path():
    input = "../data/data.db"
    expected = "..\\data\\data.db"
    assert utils.create_os_independent_path(input) == expected