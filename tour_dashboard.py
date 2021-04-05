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

gpx_file = open('resources/Rennradtour_03_04_2021_12_06.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

data = gpx.tracks[0].segments[0].points

## Start Position
start = data[0]
## End Position
finish = data[-1]

df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])

for point in data:
    df = df.append({'lon': point.longitude, 'lat' : point.latitude, 'alt' : point.elevation, 'time' : point.time}, ignore_index=True)

print(df.head(10))

#plt.plot(df['lon'], df['lat'])

plt.plot(df['time'], df['alt'])

plt.show()