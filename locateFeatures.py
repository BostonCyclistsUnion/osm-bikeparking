'''
Find which city and neighborhood POIs are in
'''
import geopandas

from fetch import main as fetch

CRS = 'EPSG:2805'
AREA_CONVERT = 3.861022e-7 # Convert from m^2 to mi^2

def locate():
    # %% Read and pre-process OSM data
    pts = geopandas.read_file('data_bikeParking.geojson')
    city = geopandas.read_file('data_cities.geojson')
    hood = geopandas.read_file('data_neighborhoods.geojson')
    council = geopandas.read_file('Boston_city_council_districts_2023_2032.json')

    # Pre-process city data
    city['population'] = city['population'].str.replace(r'\D', '', regex=True).astype(float) # Remove non-digit values from populations, e.g. commas
    city.rename(columns={'name': 'city'}, inplace=True)
    city['population'] = city['population'].fillna(-1)
    city = city.astype({"population": "int"})
    city['area_sqmi'] = city.to_crs(CRS).area * AREA_CONVERT # https://spatialreference.org/ref/epsg/2805/

    # Pre-process neighborhood data
    hood.rename(columns={'name': 'neighborhood'}, inplace=True)
    hood['area_sqmi'] = hood.to_crs(CRS).area * AREA_CONVERT # https://spatialreference.org/ref/epsg/2805/

    hoodCentroid = hood[['neighborhood', 'geometry']]
    hoodCentroid['geometry'] = hood.centroid
    hoodCentroid = hoodCentroid.sjoin(city[['city','geometry']], how='inner', predicate='intersects')
    hoodCentroid.set_index('neighborhood', inplace=True)
    hood = hood.join(hoodCentroid['city'], on='neighborhood')
    # hood = hood.join(hoodCentroid['city'], on='neighborhood', lsuffix='suf')

    # Pre-process city council districts data
    council['area_sqmi'] = council.to_crs(CRS).area * AREA_CONVERT # https://spatialreference.org/ref/epsg/2805/

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
    ptsLocatedCoun = pts[tags].sjoin(council[['Councilor','geometry']], how='inner', predicate='intersects')

    # Count number of bike parking within bounds
    parkingCountsCity = ptsLocatedCity.groupby(['city'])['capacity'].sum().sort_values(ascending=False)
    parkingCountsHood = ptsLocatedHood.groupby(['neighborhood'])['capacity'].sum().sort_values(ascending=False)    
    parkingCountsCoun = ptsLocatedCoun.groupby(['Councilor'])['capacity'].sum().sort_values(ascending=False)

    cityParking = city[['city','population', 'area_sqmi']].sort_values(by='population', ascending=False)
    cityParking.set_index('city', inplace=True)
    cityParking['capacity'] = parkingCountsCity
    cityParking['perCapita'] = cityParking['capacity'] / cityParking['population'] * 10000
    cityParking['perSqmi'] = cityParking['capacity'] / cityParking['area_sqmi']

    hoodParking = hood[['neighborhood', 'area_sqmi', 'city']]
    hoodParking.set_index('neighborhood', inplace=True)
    hoodParking['capacity'] = parkingCountsHood
    hoodParking['perSqmi'] = hoodParking['capacity'] / hoodParking['area_sqmi']

    councilParking = council[['Councilor', 'LONGNAME', 'area_sqmi']]
    councilParking.set_index('Councilor', inplace=True)
    councilParking['capacity'] = parkingCountsCoun
    councilParking['perSqmi'] = councilParking['capacity'] / councilParking['area_sqmi']

    # Save dataframe to csv
    cityParking.to_csv('parking_city.csv')
    hoodParking.to_csv('parking_neighborhood.csv')
    councilParking.to_csv('parking_council.csv')

    # Save to formatted table for website
    cityParking = cityParking.reset_index()
    # print(cityParking.columns)
    cityParking = cityParking.dropna(subset=['capacity'])
    cityParking = cityParking.astype({"capacity": "int"})
    cityParking = cityParking[['city', 'capacity', 'perCapita', 'perSqmi', 'population', 'area_sqmi']]
    cityParking.sort_values(by=['perCapita'], ascending=False, inplace=True)
    cityParking = cityParking.round({"area_sqmi": 2, "perSqmi": 1, 'perCapita':1})
    cityParking.rename(columns={'area_sqmi': 'Area (sq.mi.)', 'perSqmi': 'Capacity per sq.mi.', 'perCapita': 'Capacity per 10k residents'}, inplace=True)
    cityParking.to_html('parking_city.html', classes='sortable', index=False)

    hoodParking = hoodParking.reset_index()
    # print(hoodParking.columns)
    hoodParking = hoodParking[['neighborhood', 'city', 'capacity', 'perSqmi', 'area_sqmi']]
    hoodParking.sort_values(by=['perSqmi'], ascending=False, inplace=True)
    hoodParking = hoodParking.round({"area_sqmi": 2, "perSqmi": 1, 'capacity': 0})
    hoodParking.rename(columns={'area_sqmi': 'Area (sq.mi.)', 'perSqmi': 'Capacity per sq.mi.'}, inplace=True)
    hoodParking.to_html('parking_neighborhood.html', classes='sortable', index=False)

    councilParking = councilParking.reset_index()
    # print(councilParking.columns)
    councilParking = councilParking[['LONGNAME', 'Councilor', 'capacity', 'perSqmi', 'area_sqmi']]
    councilParking.sort_values(by=['capacity'], ascending=False, inplace=True)
    councilParking = councilParking.round({"area_sqmi": 2, "perSqmi": 1, 'capacity': 0})
    councilParking.rename(columns={'area_sqmi': 'Area (sq.mi.)', 'perSqmi': 'Capacity per sq.mi.', 'LONGNAME': 'District'}, inplace=True)
    councilParking.to_html('parking_council.html', classes='sortable', index=False)


def update_data():
    fetch('query_cities.overpassql', 'data_cities.geojson')
    fetch('query_neighborhoods.overpassql', 'data_neighborhoods.geojson')
    fetch('query_bikeParking.overpassql', 'data_bikeParking.geojson')

if __name__ == "__main__":
    # update_data()
    locate()