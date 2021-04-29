from pandas import DataFrame
from sqlalchemy import create_engine

from tour_dashboard import data_processing, utils

val = 'sqlite:///data/data.db'

def write_df_to_database(df: DataFrame, database_path: str) -> None:

	engine = create_engine(database_path, echo=False)

	hash_id_input =

	entry_already_exists = utils.value_exists_in_dataframe(df, )

# TODO: Validate to write only new data and drop already existing data via hash id
df.to_sql('tour_data', con=engine, if_exists='append')

print(engine.execute("SELECT * FROM tour_data").fetchall())