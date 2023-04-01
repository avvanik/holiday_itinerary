from neo4j import GraphDatabase
import folium
import os
from JAN23_BDE_INT_Holiday_Itinerary.endpoint.app._queries import query_cluster1, query_cluster2, query_cluster3, \
    query_cluster4, query_start_node, query_end_node, query_itinerary, query_all, query_start_relationship, \
    query_end_relationship


class Neo4jDB:

    def __init__(self):
        self.driver = GraphDatabase.driver(os.getenv("NEO4J_URI"),
                                           auth=(os.getenv("USER_NAME"),
                                                 os.getenv("PASSWORD")))

    def verify_connection(self):
        with self.driver as driver:
            driver.verify_connectivity()

    def close(self):
        self.driver.close()

    @staticmethod
    def return_all_pois(tx):
        return tx.run(query_all).values()

    @staticmethod
    def nearest_poi(tx, kind, lon, lat):
        return tx.run(query_start_node, kind=kind, lat=lat, lon=lon).values

    @staticmethod
    def itinerary_proposal(tx, kind, start_lon, start_lat, end_lon, end_lat, days):
        # define clusters for itinerary days
        cluster1 = tx.run(query_cluster1, days=days)
        cluster2 = tx.run(query_cluster2)
        cluster3 = tx.run(query_cluster3)
        cluster4 = tx.run(query_cluster4)

        # set start node
        start_node = tx.run(query_start_node, kind=kind, lat=start_lat, lon=start_lon)

        # set end node
        end_node = tx.run(query_end_node, kind=kind, lat=end_lat, lon=end_lon)

        # create relationships

        # create first relationship
        start_relationship = tx.run(query_start_relationship, start_node=start_node, kind='accommodation')

        # create last relationship
        end_relationship = tx.run(query_end_relationship, end_node=end_node, kind='food')

        # set start + end node and create itinerary
        itinerary = tx.run(query_itinerary, start=start_node, end=end_node)

        print(itinerary.values)

        # create map
        for x, y in zip(itinerary.get('lat'), itinerary.get('lon')):
            folium.Marker(([x, y])).add_to(folium.Map(location=[38.05968, 13.26699], zoom_start=13))

        return 'itinerary_map.html'
