from tour_dashboard import utils

def test_create_os_independent_path():
    path = "../data/data.db"
    utils.create_os_independent_path(path) == path