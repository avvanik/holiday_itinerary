from fastapi import FastAPI
from neo4j import GraphDatabase
import folium
import os


class Neo4jDB:

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")  # "neo4j://neo-db:7687"
        self.user = os.getenv("USER_NAME")  # "neo4j"
        self.password = os.getenv("PASSWORD")   # "Neo4j"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def verify_connection(self):
        with self.driver as driver:
            driver.verify_connectivity()

    def close(self):
        self.driver.close()

    @staticmethod
    def return_data(tx):
        result = tx.run("MATCH (p:POI) return p")
        return result.values()

    @staticmethod
    def nearest_poi(tx, kind, lon, lat):
        result = tx.run("MATCH (p:POI {kind: $kind}) "
                        "WITH p, p.location AS start_node, "
                        "point({latitude: $lat, longitude: $lon}) AS coordinates "
                        "RETURN p, round(point.distance(start_node, coordinates)) AS distance "
                        "ORDER BY distance "
                        "LIMIT 1", kind=kind, lat=lat, lon=lon)
        return result.values()

    @staticmethod
    def itinerary_proposal(tx, kind, lon, lat):
        # get closest poi as start node
        start_node = tx.run("MATCH (p:POI {kind: $kind}) "
                            "WITH p, p.location AS start_node, "
                            "point({latitude: $lat, longitude: $lon}) AS coordinates "
                            "RETURN p, round(distance(start_node, coordinates)) AS distance "
                            "ORDER BY distance "
                            "LIMIT 1", kind=kind, lat=lat, lon=lon)

        # set the closest poi as start node and return itinerary (end node 2be defined)
        result = tx.run("MATCH($start), (e:End), p = shortestPath((s)-[*]-(e)) "
                        "WHERE length(p) > 1 RETURN p ", start=start_node)

        # create map
        itinerary_map = folium.Map(location=[38.05968, 13.26699], zoom_start=13)
        lat = result.get('lat')
        lon = result.get('lon')

        for x, y in zip(lat, lon):
            folium.Marker(([x, y])).add_to(itinerary_map)

        print(result.values)
        return 'output.html'


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
        return session.write_transaction(db.return_data)


@api.get("/poi/nearest/{kind:str}/{lon:float}/{lat:float}")
def return_nearest_poi(kind, lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.nearest_poi, kind, lon, lat)


@api.get("/poi/itinerary/{kind:str}/{lon:float}/{lat:float}")
def return_itinerary(kind, lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.itinerary_proposal, kind, lon, lat)
