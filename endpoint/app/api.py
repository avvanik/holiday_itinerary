from connector import Neo4jDB
from fastapi import FastAPI

# define api
api = FastAPI(
    title="POI in Palermo",
    description="API returns specified POI in chosen area"
)

# define db object
db = Neo4jDB()


# connect to root api
@api.get("/")
def read_root():
    return {"DB": "NEO4J"}


# returns complete db
@api.get("/poi",
         name='all available points of interest')
def read_item():
    with db.driver.session() as session:
        return session.write_transaction(db.return_all_pois)


# returns the nearest poi
# user adds kind and coordinates to endpoint
# api returns the nearest poi from coordinates of added kind
@api.get("/poi/nearest/{kind:str}/{lon:float}/{lat:float}",
         name='nearest point of interest (functions as start node '
              'in next endpoint)')
def return_nearest_poi(kind, lon, lat):
    with db.driver.session() as session:
        poi = session.write_transaction(db.nearest_poi, kind, lon, lat)
    return db.create_map(poi)


# proposes an itinerary with the nearest poi for start and end node
# user adds desired days of visit
@api.get("/poi/itinerary/start={start_lon:float}/{start_lat:float}/end={end_lon:float}/{end_lat:float}/{"
         "days:int}",
         name='Itinerary visualized in a folium map.',
         description='Proposes an itinerary with the nearest poi for start and end node. The user adds desired days '
                     'of visit')
def return_itinerary(start_lon, start_lat, end_lon, end_lat, number_days):
    with db.driver.session() as session:
        poi = session.write_transaction(db.itinerary_proposal, start_lon, start_lat, end_lon, end_lat, number_days)

    return db.create_map(poi, map_type='multiple')
