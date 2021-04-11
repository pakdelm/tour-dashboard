import gpxpy
import matplotlib.pyplot as plt
import datetime
from geopy import distance
from math import sqrt, floor
import numpy as np
import pandas as pd
#import plotly.plotly as py
#import plotly.graph_objs as go
import haversine
from gpxpy.gpx import GPXTrackPoint
from pandas import DataFrame

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

path = 'resources/Rennradtour_03_04_2021_12_06.gpx'

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
    dist_hav = [0]
    dist_vin_no_alt = [0]
    dist_hav_no_alt = [0]
    dist_dif_hav_2d = [0]
    dist_dif_vin_2d = [0]

    for index in range(len(gpx_data)):
        if index == 0:
            pass
        else:
            start = gpx_data[index - 1]

            stop = gpx_data[index]

            distance_vin_2d = distance.geodesic((start.latitude, start.longitude), (stop.latitude, stop.longitude)).m
            dist_dif_vin_2d.append(distance_vin_2d)

            distance_hav_2d = haversine.haversine((start.latitude, start.longitude),
                                                  (stop.latitude, stop.longitude)) * 1000
            dist_dif_hav_2d.append(distance_hav_2d)

            dist_vin_no_alt.append(dist_vin_no_alt[-1] + distance_vin_2d)

            dist_hav_no_alt.append(dist_hav_no_alt[-1] + distance_hav_2d)

            alt_d = start.elevation - stop.elevation

            alt_dif.append(alt_d)

            distance_vin_3d = sqrt(distance_vin_2d ** 2 + (alt_d) ** 2)

            distance_hav_3d = sqrt(distance_hav_2d ** 2 + (alt_d) ** 2)

            time_delta = (stop.time - start.time).total_seconds()

            time_dif.append(time_delta)

            dist_vin.append(dist_vin[-1] + distance_vin_3d)

            dist_hav.append(dist_hav[-1] + distance_hav_3d)

    # add data to dataframe
    df['dis_vin_2d'] = dist_vin_no_alt
    df['dist_hav_2d'] = dist_hav_no_alt
    df['dis_vin_3d'] = dist_vin
    df['dis_hav_3d'] = dist_hav
    df['alt_dif'] = alt_dif
    df['time_dif'] = time_dif
    df['dis_dif_hav_2d'] = dist_dif_hav_2d
    df['dis_dif_vin_2d'] = dist_dif_vin_2d

    print('Vincenty 2D : ', dist_vin_no_alt[-1])
    print('Haversine 2D : ', dist_hav_no_alt[-1])
    print('Vincenty 3D : ', dist_vin[-1])
    print('Haversine 3D : ', dist_hav[-1])
    print('Total Time : ', floor(sum(time_dif) / 60), ' min ', int(sum(time_dif) % 60), ' sec ')

    return df

def calculate_speed(df: DataFrame) -> DataFrame:
    df['spd'] = (df['dis_dif_hav_2d'] / df['time_dif']) * 3.6
    return df

def filter_for_moving_times(df: DataFrame, threshold: float = 0.9)-> DataFrame:
    # choose here the best fit for vincenty or haversine 2d / 3d
    # currently chosen: vincenty 3d
    df['dist_dif_per_sec'] = df['dis_dif_hav_2d'] / df['time_dif']

    # empirically set to 0.9 m/s. Everything below this threshold is considered no movement and will be filtered out.
    df_with_timeout = df[df['dist_dif_per_sec'] > threshold]

    return df_with_timeout

gpx_data = read_gpx_data(path)
df = create_dataframe_from_gpx_data(gpx_data)
df_metrics = compute_tour_distances(df, gpx_data)

# super important step to match speed distribution of app. Implement in speed function
df_drop_small_time_diffs = df_metrics[df_metrics['time_dif'] > 2]

df_speed = calculate_speed(df_drop_small_time_diffs)
df_moving_time = filter_for_moving_times(df_speed)

print(df_moving_time[df_moving_time['spd'] > 40].head(20))

df_moving_time.hist(column='spd', bins=200)
plt.show()

#plt.plot(df['lon'], df['lat'])

#plt.plot(df['time'], df['alt'])

#plt.show()