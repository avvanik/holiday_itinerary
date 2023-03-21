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


api = FastAPI(
    title="POI in Palermo",
    description="API returns specified POI in chosen area"
)

obj = Neo4jDB()


@api.get("/")
def read_root():
    return {"DB": "NEO4J"}


@api.get("/data")
def read_item():
    with obj.driver.session() as session:
        result = session.write_transaction(obj.return_data)
        return result


@api.get("/{kind:str}")
def read_item(kind):

    with obj.driver.session() as session:
        result = session.write_transaction(obj.return_data)

        try:
            poi_data = list(filter(lambda x: x.get('kind') == kind, result))

            return poi_data

        except IndexError:
            return print(f"no {kind} in this area")

