"""
Pipeline functions to load gpx file and process data to calculate time series statistics and create
tour meta data and return as DataFrame
"""
from datetime import datetime
from typing import List
import hashlib

import pandas as pd
import numpy as np

import gpxpy
import geopy  # type: ignore


# pylint: disable=C0103

def create_md5_hash_code(path: str, chunk_size: int = 1024) -> str:
    """
    Function which takes a file name and returns md5 checksum of the file
    :param path: Path to file to create hash code
    :param chunk_size: Chunk size of hash
    :return: Hex checksum of file
    """
    hash_code = hashlib.md5()
    with open(path, "rb") as f:
        # Read the 1st block of the file
        chunk = f.read(chunk_size)
        # Keep reading the file until the end and update hash
        while chunk:
            hash_code.update(chunk)
            chunk = f.read(chunk_size)

    # Return the hex checksum
    return hash_code.hexdigest()


def read_gpx_data(path: str) -> List[gpxpy.gpx.GPXTrackPoint]:
    """
    Parse gpx data from file path
    :param path: Path to gpx file
    :return: GPXTrackPoint class containing elements of gps coordinate information
    """
    with open(path, 'r', encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = gpx.tracks[0].segments[0].points

    return data


def get_tour_name_from_gpx_data(path: str) -> str:
    """
    Return metadata tour name from gpx file
    :param path: Path to gpx file
    :return: Tour name of gpx file
    """
    with open(path, 'r', encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    tour_name = gpx.tracks[0].name

    if tour_name is None:
        raise TypeError(f"Could not extract tour name in gpx file under path: {path}")

    return str(tour_name)



def create_dataframe_from_gpx_data(gpx_data: List[gpxpy.gpx.GPXTrackPoint]) -> pd.DataFrame:
    """
    Convert gpx data to pandas DataFrame
    :param gpx_data: GPXTrackPoint class containing elements of gps coordinate information
    :return: DataFrame with longitude, latitude, altitude and timestamp columns from gpx data
    """

    tmp = []
    for point in gpx_data:
        df_tmp = pd.DataFrame(
            {'lon': [point.longitude],
             'lat': [point.latitude],
             'alt': [point.elevation],
             'time': [point.time.replace(tzinfo=None, microsecond=0)]})  # type: ignore
        tmp.append(df_tmp)

    df_concat = pd.concat(tmp).reset_index(drop=True)
    df_concat['data_row'] = df_concat.index

    return df_concat


def compute_tour_distances(df: pd.DataFrame, gpx_data: List[gpxpy.gpx.GPXTrackPoint]) \
        -> pd.DataFrame:
    """
    Compute distances from gps coordinates for time series gps tour data. Also calculate
    altitude gain and loss.
    :param df: DataFrame with time series tour data
    :param gpx_data: GPXTrackPoint class containing elements of gps coordinate information
    :return: DataFrame with tour data and with dinstances, altitude and time differences per each
    coordinate
    """
    alt_dif = [0]
    time_dif = [0]
    dist_vin_no_alt = [0]
    dist_dif_vin_2d = [0]

    for index in len(range(gpx_data)): # type: ignore
        if index == 0:
            pass
        else:
            start = gpx_data[index - 1]

            stop = gpx_data[index]

            distance_vin_2d = geopy.distance.geodesic(
                (start.latitude, start.longitude),
                (stop.latitude, stop.longitude)
            ).m

            dist_dif_vin_2d.append(distance_vin_2d)

            dist_vin_no_alt.append(dist_vin_no_alt[-1] + distance_vin_2d)

            alt_d = start.elevation - stop.elevation  # type: ignore

            alt_dif.append(alt_d)  # type: ignore

            time_delta = (stop.time - start.time).total_seconds()  # type: ignore

            time_dif.append(time_delta)  # type: ignore

    # add data to dataframe
    df['dis_vin_2d'] = dist_vin_no_alt
    df['alt_dif'] = alt_dif
    df['time_dif'] = time_dif
    df['dis_dif_vin_2d'] = dist_dif_vin_2d

    # calculate altitude gain and loss. Sum to get total gain and loss in meters. Note: alt_dif
    # col might be misleading as negative differences for n-1 indicate alt gain and vice verca.
    df['alt_dif_loss'] = np.where(df['alt_dif'] > 0, df['alt_dif'], 0)
    df['alt_dif_gain'] = np.where(df['alt_dif'] < 0, abs(df['alt_dif']), 0)

    return df


def calculate_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute speed per data point
    :param df: DataFrame with tour data
    :return: DataFrame with spd column in km/h
    """

    df.loc[:, 'spd'] = (df['dis_dif_vin_2d'] / df['time_dif']) * 3.6

    return df


def add_hash_id_to_dataframe(df: pd.DataFrame, path: str) -> pd.DataFrame:
    """
    Add hash id metadata to DataFrame for unique identifier of gpx file
    :param df: DataFrame with tour data
    :param path: path to gpx file
    :return: DataFrame with new column hash_id containing hash_id for all rows
    """
    hash_code = create_md5_hash_code(path)
    df["hash_id"] = hash_code
    return df


def add_tour_name_to_dataframe(df: pd.DataFrame, path: str) -> pd.DataFrame:
    '''
    Calls get_tour_name_from_gpx_data to get tour name from gpx data and adds it as col to
    DataFrame.
    :param df: DataFrame
    :param path: Path to gpx file
    :return: DataFrame with new col tour_name for entire tour partition
    '''

    tour_name = get_tour_name_from_gpx_data(path)
    df['tour_name'] = tour_name
    return df


def enrich_metadata(df: pd.DataFrame, tour_name: str, user_name: str, time_of_receipt: datetime) \
        -> pd.DataFrame:
    """
    Enrich meta data for tour data
    :param df: DataFrame with tour data
    :param tour_name: Tour name extracted from gpx file
    :param user_name: User name of tour owner
    :param time_of_receipt: Time data was processed
    :return: DataFrame enriched with metadata
    """
    df['tour_name'] = tour_name
    df['user_name'] = user_name
    df['time_of_receipt'] = time_of_receipt

    return df


def prepare_gpx_data_for_database(path: str, user_name: str) -> pd.DataFrame:
    """
    Pipeline function that combines all data processing steps in one wrapper function.
    gpx data load, computation of distances, speed and metadata enrichment
    :param path: Path to gpx file
    :param user_name: User name as meta data
    :return: DataFrame with computed tour data metrics and meta data suitable to write to database
    """

    gpx_data = read_gpx_data(path)

    df = create_dataframe_from_gpx_data(gpx_data)

    df_metrics = compute_tour_distances(df, gpx_data)

    # df_moving_time = filter_for_moving_times(df_metrics)

    df_speed = calculate_speed(df_metrics)

    df_hash_id = add_hash_id_to_dataframe(df_speed, path)

    # collect meta data
    tour_name = get_tour_name_from_gpx_data(path)

    # enrich meta data
    df_meta_data = enrich_metadata(df_hash_id, tour_name, user_name, datetime.now())

    return df_meta_data
