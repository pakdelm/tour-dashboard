import hashlib

import gpxpy
from geopy import distance
from math import sqrt

import pandas as pd
from gpxpy.gpx import GPXTrackPoint
from pandas import DataFrame

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

path = "data/Rennradtour_03_04_2021_12_06.gpx"

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
    dist_vin = [0]
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

            distance_vin_3d = sqrt(distance_vin_2d ** 2 + (alt_d) ** 2)

            time_delta = (stop.time - start.time).total_seconds()

            time_dif.append(time_delta)

            dist_vin.append(dist_vin[-1] + distance_vin_3d)

    # add data to dataframe
    df['dis_vin_2d'] = dist_vin_no_alt
    df['dis_vin_3d'] = dist_vin
    df['alt_dif'] = alt_dif
    df['time_dif'] = time_dif
    df['dis_dif_vin_2d'] = dist_dif_vin_2d

    #print('Vincenty 2D : ', dist_vin_no_alt[-1])
    #print('Vincenty 3D : ', dist_vin[-1])
    #print('Total Time : ', floor(sum(time_dif) / 60), ' min ', int(sum(time_dif) % 60), ' sec ')

    return df

def calculate_speed(df: DataFrame) -> DataFrame:
    # super important step to match speed distribution of app. Implement in speed function
    df_drop_small_time_diffs = df[df['time_dif'] > 2].copy()
    df_drop_small_time_diffs.loc[:, 'spd'] = (df_drop_small_time_diffs['dis_dif_vin_2d'] /
                                              df_drop_small_time_diffs['time_dif']) * 3.6
    return df_drop_small_time_diffs

def filter_for_moving_times(df: DataFrame, threshold: float = 0.9) -> DataFrame:
    # choose here the best fit for vincenty or haversine 2d / 3d
    # currently chosen: vincenty 3d
    df.loc[:,'dis_dif_per_sec'] = df['dis_dif_vin_2d'] / df['time_dif']

    # empirically set to 0.9 m/s. Everything below this threshold is considered no movement and will be filtered out.
    df_with_timeout = df[df['dis_dif_per_sec'] > threshold].copy()

    return df_with_timeout

def add_hash_id_to_dataframe(df: DataFrame, path: str) -> DataFrame:
    hash_code = create_md5_hash_code(path)
    df["hash_id"] = hash_code
    return df

def prepare_gpx_data_for_database(path:str) -> DataFrame:

    gpx_data = read_gpx_data(path)

    df = create_dataframe_from_gpx_data(gpx_data)

    df_metrics = compute_tour_distances(df, gpx_data)

    df_speed = calculate_speed(df_metrics)

    df_moving_time = filter_for_moving_times(df_speed)

    df_hash_id = add_hash_id_to_dataframe(df_moving_time, path)

    return df_hash_id
#print(df_moving_time.head(20))

#df_moving_time.hist(column='spd', bins=200)
#plt.show()

#plt.plot(df['lon'], df['lat'])

#plt.plot(df_moving_time['time'], df_moving_time['spd'])

#plt.show()