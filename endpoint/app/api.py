from fastapi import FastAPI
from neo4j import GraphDatabase


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
    def return_kind(tx, kind):
        result = tx.run("MATCH (p:POI {kind: $kind}) RETURN p", kind=kind)
        return result.values

    @staticmethod
    def return_poi(tx, kind, lon, lat):
        result = tx.run("MATCH (p:POI {kind: $kind, longitude: $lon, latitude: $lat}) "
                        " SET location: point({latitude: toFloat(p.lat), longitude: toFloat(p.lon)}"
                        "RETURN p", kind=kind, lon=lon, lat=lat)
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
        result = session.write_transaction(db.return_data)
        return result


@api.get("/poi/{kind:str}/{lon:float}/{lat:float}")
def read_item(kind, lon, lat):
    with db.driver.session() as session:
        result = session.write_transaction(db.return_poi(kind, lon, lat))
        return result


