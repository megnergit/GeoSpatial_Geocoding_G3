# |------------------------------------------------------------------
# | # Geospatial Data Exercise
# |------------------------------------------------------------------
# |
# | This is an exercise notebook for the fourth lesson of the kaggle course
# | ["Geospatial Analysis"](https://www.kaggle.com/learn/geospatial-analysis)
# | offered by Alexis Cook and Jessica Li. The main goal of the lesson is
# | to get used to __Geocoding__ and __Spatial Join__.

# | ## 1. Introduction
# -------------------------------------------------------#
# | Import packages.
# -------------------------------------------------------
import geopandas as gpd
from kaggle_geospatial.kgsp import *
from folium import Choropleth,  Marker, GeoJson
import folium
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import webbrowser
import zipfile
from pathlib import Path
import os
import numpy as np
import pandas as pd
from geopandas.tools import geocode

# | ### Geocoding

# | Geocoding is to convert the names or the addresses of places
# | to the latitudes and the longitude, and vice versa.
# | Here is a quick experiment with 'Marienplatz' in Munich.

result_1 = geocode(["Marienplatz"])

print(type(result_1))
print(result_1.info())
print(result_1['address'])
result_1.head(1)

# | `geocode` returns a GeoDataFrame with Shapely `POINT` object
# | and the address.

# --
result_2 = geocode(["Neuschwanstein"])

print(type(result_2))
print(result_2.info())
print(result_2['address'])
result_2.head(1)

# --
result_3 = geocode(["Augsburger Rathaus"])

print(type(result_3))
print(result_3.info())
print(result_3['address'])
result_3.head(1)

# --
result_4 = geocode(["Rathaus, Altenmuenster"])

print(type(result_4))
print(result_4.info())
print(result_4['address'])
result_4.head(1)

# | Wow!

# | ### Spatial Join
# | See Appendix.
# |
# | ## 2. Task
# |
# | Visualize the distribution of the coffeshops Starbucks in California.
# | Find out the best county to build the next 'Starbucks Reserve Roastery'
# | (flagship atelier/gallery shops of Starbucks) in San Francisco.

# | ## 3. Data
# |
# | 1. Locations of Starbucks in California.
# | 2. General underlying map.
# | 3. Boundaries of counties in California.
# | 4. Statistics of counties in California, such as population,
# |    area in km<sup>2</sup>, and median ages.  Among all, a unique information is
# |    the number of __high earners__ (household with annual income over $150,000).
# |
# |
# | ## 4. Notebook

# -------------------------------------------------------
# | Set up some directories.

CWD = '/Users/meg/git6/geocode/'
DATA_DIR = '../input/geospatial-learn-course-data/'
KAGGLE_DIR = 'alexisbcook/geospatial-learn-course-data'
GEO_DIR = 'geospatial-learn-course-data'

set_cwd(CWD)
set_data_dir(DATA_DIR, KAGGLE_DIR, GEO_DIR, CWD)
show_whole_dataframe(True)

# -------------------------------------------------------
# | Read the starbucks data.

starbucks = pd.read_csv(DATA_DIR + 'starbucks_locations.csv')
print(starbucks.info())
starbucks.head(3)

# -------------------------------------------------------
# | Ancillary data for the state of California.

CA_data_dir = DATA_DIR+'CA_county_boundaries/CA_county_boundaries/'

CA_counties = gpd.read_file(CA_data_dir+'CA_county_boundaries.shp')
CA_pop = pd.read_csv(DATA_DIR + 'CA_county_population.csv', index_col="GEOID")
CA_high_earners = pd.read_csv(
    DATA_DIR + 'CA_county_high_earners.csv', index_col="GEOID")
CA_median_age = pd.read_csv(
    DATA_DIR + 'CA_county_median_age.csv', index_col="GEOID")

print(CA_counties.info())
print(CA_pop.info())
print(CA_high_earners.info())
print(CA_median_age.info())

print(CA_counties.head(3))
print(CA_pop.head(3))
print(CA_high_earners.head(3))
print(CA_median_age.head(3))

# -------------------------------------------------------
# | 'high earners' here means the number of household with annual
# | income of $150,000 or more.

# -------------------------------------------------------
# | Start with Starbucks data.
# | There are 5 missing 'Longitude' and 'Latitude' n the data.

starbucks.isna().sum()
starbucks.loc[starbucks['Longitude'].isna(), :]
starbucks.loc[starbucks['Latitude'].isna(), :]
missing_locations = starbucks.loc[starbucks['Latitude'].isna(), :]

# -------------------------------------------------------
# | The shops with missing 'Longitude' and 'Latitude' are
# | all in Berkeley. We will use `geocode` to find out
# | the coordinates of these shops from their
# | addresses.

x = pd.concat([geocode(r['Address'])
               for i, r in missing_locations.iterrows()], axis=0)

missing_locations[['Longitude', 'Latitude']] = [
    [p['geometry'].x, p['geometry'].y] for i, p in x.iterrows()]

starbucks = starbucks.combine_first(missing_locations)
starbucks[starbucks['City'] == 'Berkeley']

# -------------------------------------------------------
# | `.combine_first` is to fill `None` with the second
# | DataFrame. Make sure that the index is aligned [two DataFrames
# | use the same (=consistent) index].
# | Let us take a look at the locations we just found.
# | Visualize the tuple (latitude, longitude) in Berkeley
# | in the OpenStreetMap.

# -------------------------------------------------------
# | Now we have a complete table.

starbucks['Address'].str.contains('CA').mean()

# | All shops are in California.

# -------------------------------------------------------
# | We will start visualization the locations of the cafes.
# | First, setup the center of the map, tiles, and the zoom factor.

center = [starbucks['Latitude'].mean(), starbucks['Longitude'].mean()]
tiles = 'openstreetmap'
zoom = 8


# -------------------------------------------------------
m_1 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)

dump = [Marker((r['Latitude'], r['Longitude']),
               tooltip=r['Address']).add_to(m_1)
        for i, r in starbucks.iterrows()]

embed_map(m_1, './html/m_1.html')
# --
show_on_browser(m_1, CWD + './html/m_1b.html')

# -------------------------------------------------------
# | Okay, now we start working with the ancillary data.
# | Combine all of them on the index `GEOID`.
# | Make sure that the one with the geometry column
# | is the left most DataFrame.
# |

CA_stats = CA_counties.merge(CA_pop, on='GEOID')
CA_stats = CA_stats.merge(CA_high_earners, on='GEOID')
CA_stats = CA_stats.merge(CA_median_age, on='GEOID')
# CA_stats.set_index('GEOID', inplace=True)
# -------------------------------------------------------
# | Check CRS.
CA_stats.crs

# -------------------------------------------------------
# | It looks like the order of latitude and longitude in `geometry`
# | is not correct. Check it by plotting it.


def style_function(x):
    #    return {'fillColor': 'coral', 'stroke': False}
    return {'fillColor': 'teal', 'stroke': True}


m_2 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
GeoJson(data=CA_stats.__geo_interface__,
        style_function=style_function).add_to(m_2)
embed_map(m_2, './html/m_2.html')
# --
show_on_browser(m_2, CWD + './html/m_2b.html')

# -------------------------------------------------------
# | Okay somehow GeoJson handles the coordinates correctly.

# -------------------------------------------------------
# | Add population-density, and fraction of high earners.

CA_stats['density'] = CA_stats['population'] / CA_stats['area_sqkm']
CA_stats['fraction_HE'] = CA_stats['high_earners'] / CA_stats['population']

# -------------------------------------------------------
# | Create a couple of choropleths to see
# | the demographic and the economic landscape of California

tiles = 'Stamen Terrain'
m_3 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)

Choropleth(geo_data=CA_stats.__geo_interface__,
           name='choropleth',
           data=CA_stats,
           columns=['name', 'median_age'],
           key_on='feature.properties.name',
           fill_color='YlGnBu',
           bins=[25, 30, 35, 40, 45, 50, 55, 60],
           legend_name='Median Age of Counties in CA').add_to(m_3)

embed_map(m_3, './html/m_3.html')
# --
show_on_browser(m_3, CWD + './html/m_3b.html')

# -------------------------------------------------------
# | __`Choropleth`__ summary.
# |  - `columns`: two columns of 'CA_stats' for statistics to shwo.
# |  - `key_on` : which one of the two above to use to match with 'geo_data'.

# -------------------------------------------------------
# | 1. In the counties far away from the coast line toward the western hills
# | of Sierra Nevada, the median ages are high, sometimes over 50.
# |
# | 2. In and nare the two metropolises, Los Angeles and San Francisco,
# | the median ages are in between 35-45.
# |
# | 3. In between the cities along the coast and Sierra Nevada, in Great Valley
# |  and Mohave Desert, the median ages are younger than 35.
# |
# -------------------------------------------------------

tiles = 'Stamen Terrain'
m_4 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)

Choropleth(geo_data=CA_stats.__geo_interface__,
           name='choropleth',
           data=CA_stats,
           columns=['name', 'high_earners'],
           key_on='feature.properties.name',
           fill_color='YlGnBu',
           bins=10 ** np.array([1, 2, 3, 4, 5, 6]),
           legend_name='Number of Household with Annual Income > $150k in CA').add_to(m_4)

embed_map(m_4, './html/m_4.html')
# --
show_on_browser(m_4, CWD + './html/m_4b.html')

# -------------------------------------------------------
tiles = 'Stamen Terrain'
m_5 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)

Choropleth(geo_data=CA_stats.__geo_interface__,
           name='choropleth',
           data=CA_stats,
           columns=['name', 'fraction_HE'],
           key_on='feature.properties.name',
           fill_color='YlGnBu',
           bins=[0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16],
           legend_name='Fraction of Household with Annual Income > $150k in CA').add_to(m_5)

embed_map(m_5, './html/m_5.html')
# --
show_on_browser(m_5, CWD + './html/m_5b.html')

# -------------------------------------------------------
# | 1. Northern part of San Francisco Bay Area has the highest
# | fraction of high earners.
# -------------------------------------------------------
# | Let us look at the number of Starbucks stores for each county.

starbucks = gpd.GeoDataFrame(starbucks,
                             geometry=gpd.points_from_xy(
                                 starbucks['Longitude'], starbucks['Latitude']))

starbucks.crs = {'init': 'epsg:4326'}

number_of_sb = []
for i, c in CA_stats.iterrows():
    number_of_sb.append(sum([c['geometry'].contains(s)
                             for s in starbucks['geometry']]))

CA_stats['number_of_sb'] = number_of_sb

# -------------------------------------------------------
tiles = 'cartodbpositron'
m_6 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)

Choropleth(geo_data=CA_stats.__geo_interface__,
           name='choropleth',
           data=CA_stats,
           columns=['name', 'number_of_sb'],
           key_on='feature.properties.name',
           fill_color='YlGnBu',
           bins=[0, 10, 50, 100, 200, 400, 800],
           legend_name='Number of Starbucks Cafes').add_to(m_6)

embed_map(m_6, './html/m_6.html')
# --
show_on_browser(m_6, CWD + './html/m_6b.html')

# -------------------------------------------------------
CA_stats['sb_per_pop'] = CA_stats['number_of_sb'] / \
    CA_stats['population'] * 10**5

# -------------------------------------------------------
tiles = 'cartodbpositron'
m_7 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
Choropleth(geo_data=CA_stats.__geo_interface__,
           name='choropleth',
           data=CA_stats,
           columns=['name', 'sb_per_pop'],
           key_on='feature.properties.name',
           fill_color='YlGnBu',
           bins=[0, 2, 4, 6, 8, 10, 12, 14, 16],
           legend_name='Number of Starbucks Cafes per 100,000 People').add_to(m_7)

embed_map(m_7, './html/m_7.html')
# --
show_on_browser(m_7, CWD + './html/m_7b.html')
# -------------------------------------------------------
# |  1. Highest number of Starbucks cafes per capita
# | was Mono County in Sierra Nevada.
# -------------------------------------------------------
CA_stats['sb_per_HE'] = CA_stats['high_earners'] / \
    CA_stats['population']

# -------------------------------------------------------
tiles = 'cartodbpositron'
m_8 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
Choropleth(geo_data=CA_stats.__geo_interface__,
           name='choropleth',
           data=CA_stats,
           columns=['name', 'sb_per_HE'],
           key_on='feature.properties.name',
           tooltip=folium.features.GeoJsonTooltip(fields=['name']),
           fill_color='YlGnBu',
           bins=[0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16],
           legend_name='Number of Starbucks Cafes per HE').add_to(m_8)

embed_map(m_8, './html/m_8.html')
# --
show_on_browser(m_8, CWD + './html/m_8b.html')
# -------------------------------------------------------
# | To see all of the above in Scatter plot and Bar plots.
# -------------------------------------------------------

trace = go.Scatter(x=CA_stats['median_age'],
                   y=CA_stats['fraction_HE'],
                   mode='markers',
                   marker=dict(color='coral',
                               size=20),
                   #                   textfont=dict(size=32),
                   hovertext=CA_stats['name'],
                   hoverinfo='text',
                   opacity=0.8)

data = [trace]

layout = go.Layout(height=1024, width=1024,
                   font=dict(size=20),
                   xaxis=dict(title=dict(text='Median Age')),
                   yaxis=dict(title=dict(text='Fraction of High Earners')),
                   showlegend=False)

fig = go.Figure(data=data, layout=layout)
# --
embed_plot(fig, './html/p_1.html')
# --
fig.show()
# -------------------------------------------------------
# | 1. There is a cluster at the median age between 36 and 43
# | and the fraction of high earner over 0.06.

# -------------------------------------------------------
CA_HE = CA_stats[(CA_stats['fraction_HE'] >= 0.06)
                 & (CA_stats['median_age'] >= 36)
                 & (CA_stats['median_age'] <= 43)]
len(CA_HE)
CA_HE.head(3)

n_rows = 5
n_cols = 1
fig = make_subplots(rows=n_rows, cols=n_cols,
                    vertical_spacing=0.02,
                    subplot_titles=[
                        #                                    'Population',
                        'Population Density',
                        'Median Age',
                        'Number of Starbucks',
                        'Number of Starbucks per 100,000 People',
                        'Number of Starbucks per High Earner'])

trace_density = go.Bar(y=CA_HE.sort_values('sb_per_HE')['name'],
                       x=CA_HE.sort_values('sb_per_HE')['density'],
                       #                       x=CA_HE.sort_values('sb_per_HE')['population'],
                       xaxis='x', yaxis='y', orientation='h')

trace_med_age = go.Bar(y=CA_HE.sort_values('sb_per_HE')['name'],
                       x=CA_HE.sort_values('sb_per_HE')['median_age'],
                       xaxis='x2', yaxis='y2', orientation='h')

trace_sb = go.Bar(y=CA_HE.sort_values('sb_per_HE')['name'],
                  x=CA_HE.sort_values('sb_per_HE')['number_of_sb'],
                  xaxis='x3', yaxis='y3', orientation='h')

trace_sb_pop = go.Bar(y=CA_HE.sort_values('sb_per_HE')['name'],
                      x=CA_HE.sort_values('sb_per_HE')['sb_per_pop'],
                      xaxis='x4', yaxis='y4', orientation='h')

trace_sb_HE = go.Bar(y=CA_HE.sort_values('sb_per_HE')['name'],
                     x=CA_HE.sort_values('sb_per_HE')['sb_per_HE'],
                     xaxis='x5', yaxis='y5', orientation='h')

data = [trace_density, trace_med_age, trace_sb, trace_sb_pop, trace_sb_HE]

layout = go.Layout(height=640 * 5, width=1024,
                   font=dict(size=20),
                   showlegend=False)

layout = fig.layout.update(layout)
fig = go.Figure(data=data, layout=layout)
# --
embed_plot(fig, './html/p_2.html')
# -
fig.show()

# -------------------------------------------------------
# | ## 5. Conclusion
# | Where to locate the next Starbucks Reserve Roastery in California?
# |
# | 1. The customer segmentation would be young, professional, and early adapter
# |  with the priority in this order.
# |
# | 2. The strategy depends on how we see the number of Starbucks per capita.
# |    The presence of many Starbucks in a county is a sign of success? Or
# |    a sign of saturation?
# |
# | 3. A bit younger median ages among Starbucks-dense counties,
# |  Santa Clara and Alameda stand out.  My pick is __Alameda__.
# |
# |

# -------------------------------------------------------
# | ## 6. Appendix
# | ### Spatial Join
# | 'Spatial join' joins two GeoDataFrames according to their geometrical matchning.
# | Suppose that the first GeoDataFrames has `POINT` object in 'geometry' column
# | and the second GeoDataFrames has `POLYGON`. One can join two GeoDataFrame so that
# | the `POINT` is included in `POLYGON`.
# |
# | We assigned the total number of Starbucks in `starbucks` to each county
# | in `CA_stats` above. Let us the other way around, and add county information
# | to `starbucks`.

starbucks.head(3)
CA_stats.head(3)

x = starbucks.sjoin(CA_stats)
x.head(3)

# -------------------------------------------------------
# | END
