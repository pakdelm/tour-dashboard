import hashlib

import gpxpy
from geopy import distance
from math import sqrt

import pandas as pd
import numpy as np
from gpxpy.gpx import GPXTrackPoint
from pandas import DataFrame

def create_md5_hash_code(path: str, chunk_size:int=1024) -> str:
    """
    Function which takes a file name and returns md5 checksum of the file
    """
    hash = hashlib.md5()
    with open(path, "rb") as f:
        # Read the 1st block of the file
        chunk = f.read(chunk_size)
        # Keep reading the file until the end and update hash
        while chunk:
            hash.update(chunk)
            chunk = f.read(chunk_size)

    # Return the hex checksum
    return hash.hexdigest()

def read_gpx_data(path: str) -> [GPXTrackPoint]:
    gpx_file = open(path, 'r')
    gpx = gpxpy.parse(gpx_file)

    data = gpx.tracks[0].segments[0].points

    return data

def get_tour_name_from_gpx_data(path: str) -> str:
    gpx_file = open(path, 'r')
    gpx = gpxpy.parse(gpx_file)

    tour_name = gpx.tracks[0].name

    return tour_name

def create_dataframe_from_gpx_data(gpx_data: [GPXTrackPoint]) -> DataFrame:

    df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])

    for point in gpx_data:
        df = df.append({'lon': point.longitude,
                        'lat' : point.latitude,
                        'alt' : point.elevation,
                        'time' : point.time.replace(tzinfo=None, microsecond=0)},
                        ignore_index=True)
    return df

def compute_tour_distances(df: DataFrame, gpx_data: [GPXTrackPoint]) -> DataFrame:

    alt_dif = [0]
    time_dif = [0]
    dist_vin_no_alt = [0]
    dist_dif_vin_2d = [0]

    for index in range(len(gpx_data)):
        if index == 0:
            pass
        else:
            start = gpx_data[index - 1]

            stop = gpx_data[index]

            distance_vin_2d = distance.geodesic((start.latitude, start.longitude), (stop.latitude, stop.longitude)).m

            dist_dif_vin_2d.append(distance_vin_2d)

            dist_vin_no_alt.append(dist_vin_no_alt[-1] + distance_vin_2d)

            alt_d = start.elevation - stop.elevation

            alt_dif.append(alt_d)

            time_delta = (stop.time - start.time).total_seconds()

            time_dif.append(time_delta)

    # add data to dataframe
    df['dis_vin_2d'] = dist_vin_no_alt
    df['alt_dif'] = alt_dif
    df['time_dif'] = time_dif
    df['dis_dif_vin_2d'] = dist_dif_vin_2d

    # calculate altitude gain and loss. Sum to get total gain and loss in meters.
    # Note: alt_dif col might be misleading as negative differences for n-1 indicate alt gain and vice verca.
    df['alt_dif_loss'] = np.where(df['alt_dif'] > 0, df['alt_dif'], 0)
    df['alt_dif_gain'] = np.where(df['alt_dif'] < 0, abs(df['alt_dif']), 0)

    return df

def calculate_speed(df: DataFrame) -> DataFrame:
    # super important step to match speed distribution of app. Implement in speed function
    #df_drop_small_time_diffs = df[df['time_dif'] > 2].copy()
    df_drop_small_time_diffs = df
    df_drop_small_time_diffs.loc[:, 'spd'] = (df_drop_small_time_diffs['dis_dif_vin_2d'] /
                                              df_drop_small_time_diffs['time_dif']) * 3.6
    return df_drop_small_time_diffs



def add_hash_id_to_dataframe(df: DataFrame, path: str) -> DataFrame:
    hash_code = create_md5_hash_code(path)
    df["hash_id"] = hash_code
    return df

def add_tour_name_to_dataframe(df: DataFrame, path:str) -> DataFrame:
    '''
    Calls get_tour_name_from_gpx_data to get tour name from gpx data and adds it as col to DataFrame.
    :param df: DataFrame
    :param path: Path to gpx file
    :return: DataFrame with new col tour_name for entire tour partition
    '''

    tour_name = get_tour_name_from_gpx_data(path)
    df['tour_name'] = tour_name
    return df

def prepare_gpx_data_for_database(path:str) -> DataFrame:

    gpx_data = read_gpx_data(path)

    df = create_dataframe_from_gpx_data(gpx_data)

    df_metrics = compute_tour_distances(df, gpx_data)

    #df_moving_time = filter_for_moving_times(df_metrics)

    df_speed = calculate_speed(df_metrics)

    df_hash_id = add_hash_id_to_dataframe(df_speed, path)

    df_tour_name = add_tour_name_to_dataframe(df_hash_id, path)

    return df_tour_name