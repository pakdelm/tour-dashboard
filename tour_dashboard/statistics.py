from math import floor

from pandas import DataFrame

def get_distance_metrics_from_dataframe(df: DataFrame) -> (float, int, float, float):
    '''

    :param df:
    :return: distance_km, time_min, altitude_gain, altitude_loss
    '''
    distance_km = round(df['dis_vin_2d'].iloc[-1] / 1000, 1)
    time = df['time_dif']
    time_min = floor(sum(time) / 60)
    altitude_loss = sum(df['alt_dif_loss'])
    altitude_gain = sum(df['alt_dif_gain'])

    return distance_km, time_min, altitude_gain, altitude_loss


def get_average_speed_from_dataframe(df: DataFrame) -> float:
    average_speed = round(df['spd'].mean(), 2)
    return average_speed

def filter_for_moving_times(df: DataFrame, threshold: float = 0.9) -> DataFrame:
    # choose here the best fit for vincenty or haversine 2d / 3d
    # currently chosen: vincenty 3d
    df.loc[:,'dis_dif_per_sec'] = df['dis_dif_vin_2d'] / df['time_dif']

    # empirically set to 0.9 m/s. Everything below this threshold is considered no movement and will be filtered out.
    df_with_timeout = df[df['dis_dif_per_sec'] > threshold].copy()

    return df_with_timeout