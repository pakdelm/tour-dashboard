from sqlalchemy import create_engine

from gpx_data_processing import path, prepare_gpx_data_for_database

engine = create_engine('sqlite:///data.db', echo=False)

df = prepare_gpx_data_for_database(path)

df.to_sql('tour_data', con=engine, if_exists='append')

print(engine.execute("SELECT * FROM tour_data").fetchall())