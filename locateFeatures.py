'''
Find which city and neighborhood POIs are in
'''
import geopandas

# import pandas as pd
from fetch import main as fetch


def locate():
    # %% Read and pre-process OSM data
    pts = geopandas.read_file('data_bikeParking.geojson')
    city = geopandas.read_file('data_cities.geojson')
    hood = geopandas.read_file('data_neighborhoods.geojson')

    # Pre-process city data
    city['population'] = city['population'].str.replace(r'\D', '', regex=True).astype(float) # Remove non-digit values from populations, e.g. commas
    city.rename(columns={'name': 'city'}, inplace=True)
    city['population'] = city['population'].fillna(-1)
    city = city.astype({"population": "int"})
    city['area_sqmi'] = city.to_crs('EPSG:2805').area * 3.861022e-7 # https://spatialreference.org/ref/epsg/2805/

    # Pre-process neighborhood data
    hood.rename(columns={'name': 'neighborhood'}, inplace=True)
    hood['area_sqmi'] = hood.to_crs('EPSG:2805').area * 3.861022e-7 # https://spatialreference.org/ref/epsg/2805/

    hoodCentroid = hood[['neighborhood', 'geometry']]
    hoodCentroid['geometry'] = hood.centroid
    hoodCentroid = hoodCentroid.sjoin(city[['city','geometry']], how='inner', predicate='intersects')
    hoodCentroid.set_index('neighborhood', inplace=True)
    hood = hood.join(hoodCentroid['city'], on='neighborhood')
    # hood = hood.join(hoodCentroid['city'], on='neighborhood', lsuffix='suf')

    # Pre-process bike parking data
    pts['capacity'] = pts['capacity'].fillna(1)
    pts['capacity'] = [x.split(';')[0] if ';' in str(x) else x for x in pts['capacity']]
    pts = pts.astype({"capacity": "int"})

    # %% Locate bike parking within bounds
    # Reduce which tags to keep in bike parking
    tags = ['access', 'amenity', 'bicycle_parking', 'bicycle_parking:rack',
        'bike_ride', 'capacity', 'capacity:cargo_bike', 'cargo_bike', 
        'covered', 'description', 'fixme', 'image', 'indoor',
        'location', 'lockable', 'locked', 'mapillary', 'name',
        'note',  'panoramax', 'parking', 'spaces',  'wikimedia_commons', 
        '@id', '@type', 'geometry']

    ptsLocatedCity = pts[tags].sjoin(city[['city','geometry']], how='inner', predicate='intersects')
    ptsLocatedHood = pts[tags].sjoin(hood[['neighborhood','geometry']], how='inner', predicate='intersects')

    parkingCountsCity = ptsLocatedCity.groupby(['city'])['capacity'].sum().sort_values(ascending=False)
    parkingCountsHood = ptsLocatedHood.groupby(['neighborhood'])['capacity'].sum().sort_values(ascending=False)

    cityParking = city[['city','population', 'area_sqmi']].sort_values(by='population', ascending=False)
    cityParking.set_index('city', inplace=True)
    cityParking['capacity'] = parkingCountsCity
    cityParking['perCapita'] = cityParking['capacity'] / cityParking['population'] * 10000
    cityParking['perSqmi'] = cityParking['capacity'] / cityParking['area_sqmi']

    hoodParking = hood[['neighborhood', 'area_sqmi', 'city']]
    hoodParking.set_index('neighborhood', inplace=True)
    hoodParking['capacity'] = parkingCountsHood
    hoodParking['perSqmi'] = hoodParking['capacity'] / hoodParking['area_sqmi']

    cityParking.to_csv('parking_city.csv')
    hoodParking.to_csv('parking_neighborhood.csv')
    hoodParking.to_html('parking_neighborhood.html')

def update_data():
    fetch('query_cities.overpassql', 'data_cities.geojson')
    fetch('query_neighborhoods.overpassql', 'data_neighborhoods.geojson')
    fetch('query_bikeParking.overpassql', 'data_bikeParking.geojson')

if __name__ == "__main__":
    # update_data()
    locate()