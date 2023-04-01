from fastapi import FastAPI
from connector import Neo4jDB

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


# returns nearest poi
@api.get("/poi/nearest/{kind:str}/{lon:float}/{lat:float}",
         name='nearest point of interest (functions as start node '
              'in next endpoint)')
def return_nearest_poi(kind, lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.nearest_poi, kind, lon, lat)


# proposes an itinerary with the nearest poi as start node
@api.get("/poi/itinerary/{kind:str}/start={start_lon:float}/{start_lat:float}/end={end_lon:float}/{end_lat:float}",
         name='itinerary visualized in a folium map')
def return_itinerary(kind, start_lon, start_lat, end_lon, end_lat):
    with db.driver.session() as session:
        return session.write_transaction(db.itinerary_proposal, kind, start_lon, start_lat, end_lon, end_lat)
