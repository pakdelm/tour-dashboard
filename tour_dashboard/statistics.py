"""
Functionalities to calculate tour statistics
"""
import math
from typing import Tuple

import pandas as pd


# pylint: disable=C0103


def get_distance_metrics_from_dataframe(df: pd.DataFrame) -> Tuple[float, int, float, float]:
    """
    Return distance metrics from DataFrame containing tour data
    :param df: DataFrame with single tour data
    :return: distance_km, time_min, altitude_gain, altitude_loss
    """
    distance_km = round(df['dis_vin_2d'].iloc[-1] / 1000, 1)
    time = df['time_dif']
    time_min = math.floor(sum(time) / 60)
    altitude_loss = sum(df['alt_dif_loss'])
    altitude_gain = sum(df['alt_dif_gain'])

    return float(distance_km), int(time_min), float(altitude_gain), float(altitude_loss)


def get_average_speed_from_dataframe(df: pd.DataFrame) -> float:
    """
    Compute average speed in km/s in DataFrame containing single tour data
    :param df: DataFrame with single tour data
    :return: Average speed
    """
    average_speed = round(df['spd'].mean(), 2)
    return float(average_speed)


def filter_for_moving_times(df: pd.DataFrame, moving_threshold: float = 0.9) -> pd.DataFrame:
    """
    Filter DataFrame for moving times and drop idle times during tour. Moving times are empirically
    defined as distance difference per second > 0.9 m. This delivered the closest results to
    Komoot statistics.
    :param df: DataFrame with tour data
    :param moving_threshold: default 0.9 m/s
    :return: DataFrame with moving times above threshold.
    """
    # Choose here the best fit for vincenty 3d or haversine 2d / 3d
    # Vincenty 3d delivered the best results close to Komoot statistics
    df.loc[:, 'dis_dif_per_sec'] = df['dis_dif_vin_2d'] / df['time_dif']

    # Empirically set to 0.9 m/s. Everything below this threshold is considered no movement and
    # will be filtered out.
    df_with_timeout = df[df['dis_dif_per_sec'] > moving_threshold].copy()

    return df_with_timeout


def truncate_to_date(df: pd.DataFrame, timestamp_col: str, date_col: str) -> pd.DataFrame:
    """
    Truncate timestamp column of input DataFrame to date
    :param df: DataFrame with timestamp column
    :param timestamp_col: Column containing timestamp
    :param date_col: output column
    :return: DataFrame with truncated date
    """
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df[date_col] = df[timestamp_col].dt.floor('d') # type: ignore
    return df

# def create_df_statistics():
