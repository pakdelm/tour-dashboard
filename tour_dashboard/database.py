from sqlalchemy import create_engine

from tour_dashboard import data_processing

# TODO: Create function. Create table per user.

engine = create_engine('sqlite:///data/data.db', echo=False)

df = data_processing.prepare_gpx_data_for_database(data_processing.path)

df.to_sql('tour_data', con=engine, if_exists='append')

print(engine.execute("SELECT * FROM tour_data").fetchall())