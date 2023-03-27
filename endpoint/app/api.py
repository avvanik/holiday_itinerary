from fastapi import FastAPI
from neo4j import GraphDatabase
import folium

url = "https://raw.githubusercontent.com/DataScientest/JAN23_BDE_INT_Holiday_Itinerary/main/data/places_output.csv" \
      "?token=GHSAT0AAAAAAB55ARCIPXI334SUJP4GCPVWZBBHS4A"


class Neo4jDB:

    def __init__(self):
        self.uri = "neo4j+s://359dfc7f.databases.neo4j.io:7687"
        self.user = "neo4j"
        self.password = "Y$zulDtAvM3q"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def verify_connection(self):
        with self.driver as driver:
            driver.verify_connectivity()

    def close(self):
        self.driver.close()

    @staticmethod
    def generate_data(tx):
        result = tx.run("LOAD CSV WITH HEADERS FROM $url AS row CREATE (:POI {id: row.xid, name:row.name, "
                        "url: row.url, stars: row.stars, wikipedia: row.wikipedia, image: row.image, "
                        "address: row.address, kind: row.kinds,  location: point({latitude: toFloat(row.lat), "
                        "longitude: toFloat(row.lon)})}) RETURN p", url=url)

        return result

    # @staticmethod
    # def return_data(tx):
    #     result = tx.run("MATCH (p:POI) return p")
    #     return result.values()

    @staticmethod
    def return_kind(tx, kind):
        result = tx.run("MATCH (p:POI {kind: $kind}) RETURN p", kind=kind)
        return result.values

    @staticmethod
    def nearest_poi(tx, kind, lon, lat):
        result = tx.run("MATCH (p:POI {kind: $kind, longitude: $lon, latitude: $lat}) "
                        " SET location: point({latitude: toFloat(p.lat), longitude: toFloat(p.lon)}"
                        "RETURN p", kind=kind, lon=lon, lat=lat)
        return result

    @staticmethod
    def create_map(poi):
        itinerary_map = folium.Map(location=[38.05968, 13.26699], zoom_start=13)
        lat = poi.get('lat')
        lon = poi.get('lon')

        for x, y in zip(lat, lon):
            folium.Marker(([x, y])).add_to(itinerary_map)

        return 'output.html'

    @staticmethod
    def itinerary_proposal(tx, lon, lat):

        # get closest poi
        nearest_poi = tx.run("MATCH (p:POI) WITH p, point.distance(point({latitude: $lat, longitude: $lon, "
                             "crs: 'wgs-84}) as distance ORDER BY distance ASC LIMIT 1", lon=lon, lat=lat)

        # set the closest poi as start node and return itinerary (end node 2be defined)
        result = tx.run("MATCH($nearest_poi), (e:End), p = shortestPath((s)-[*]-(e)) "
                        "WHERE length(p) > 1 RETURN p ", nearest_poi=nearest_poi)

        return result


api = FastAPI(
    title="POI in Palermo",
    description="API returns specified POI in chosen area"
)

db = Neo4jDB()


@api.get("/")
def read_root():
    return {"DB": "NEO4J"}


@api.get("/poi")
def read_item():
    with db.driver.session() as session:
        return session.write_transaction(db.generate_data)


@api.get("/poi/{kind:str}/{lon:float}/{lat:float}")
def return_nearest_poi(kind, lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.nearest_poi, kind, lon, lat)


@api.get("/poi/itinerary/{lon:float}/{lat:float}")
def return_itinerary(lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.itinerary_proposal, lon, lat)


@api.get("/poi/itinerary/map/{poi:str}")
def return_itinerary_as_map(poi):
    with db.driver.session() as session:
        return session.write_transaction(db.create_map, poi)
