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
    def return_data(tx):
        result = tx.run("MATCH (p:POI) return p")
        return result.values()

    @staticmethod
    def nearest_poi(tx, lon, lat):
        return tx.run("MATCH (p:POI) WITH p, point.distance(point({latitude: $lat, longitude: $lon, "
                      "crs: 'wgs-84}) as distance ORDER BY distance ASC LIMIT 1", lon=lon, lat=lat)

    @staticmethod
    def itinerary_proposal(tx, lon, lat):
        # get closest poi as start node
        start_node = tx.run("MATCH (p:POI) WITH p, point.distance(point({latitude: $lat, longitude: $lon, "
                            "crs: 'wgs-84}) as distance ORDER BY distance ASC LIMIT 1", lon=lon, lat=lat)

        # set the closest poi as start node and return itinerary (end node 2be defined)
        result = tx.run("MATCH($start), (e:End), p = shortestPath((s)-[*]-(e)) "
                        "WHERE length(p) > 1 RETURN p ", start=start_node)

        # create map
        itinerary_map = folium.Map(location=[38.05968, 13.26699], zoom_start=13)
        lat = result.get('lat')
        lon = result.get('lon')

        for x, y in zip(lat, lon):
            folium.Marker(([x, y])).add_to(itinerary_map)

        print(result)
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


@api.get("/poi/nearest/{lon:float}/{lat:float}")
def return_nearest_poi(lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.nearest_poi, lon, lat)


@api.get("/poi/itinerary/{lon:float}/{lat:float}")
def return_itinerary(lon, lat):
    with db.driver.session() as session:
        return session.write_transaction(db.itinerary_proposal, lon, lat)
