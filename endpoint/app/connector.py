from datetime import time
from neo4j import GraphDatabase
import folium
import os
from _queries import query_cluster1, query_cluster2, query_cluster3, \
    query_cluster4, query_start_node, query_end_node, query_all, query_relationships, query_itinerary, query_nearest_poi
from selenium import webdriver


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
        return tx.run(
            query_all
        ).values()

    @staticmethod
    def nearest_poi(tx, kind, lon, lat):

        return tx.run(
            query_nearest_poi,
            kind=kind,
            lon=lon,
            lat=lat
        ).values()

    @staticmethod
    def itinerary_proposal(tx, start_lon, start_lat, end_lon, end_lat, number_days):
        # create clusters for number_days
        cluster1 = tx.run(
            query_cluster1,
            days=number_days
        )

        cluster2 = tx.run(
            query_cluster2,
            Day=cluster1,
            days=number_days
        )

        # assign each node to the closest cluster
        cluster3 = tx.run(
            query_cluster3,
            Day=cluster2
        )

        itinerary_days = tx.run(
            query_cluster4,
            POI=cluster3,
            Day=cluster2
        )

        # set start node
        start_node = tx.run(
            query_start_node,
            lat=start_lat,
            lon=start_lon,
            kind="accommodation"
        )

        # set end node
        end_node = tx.run(
            query_end_node,
            lat=end_lat,
            lon=end_lon,
            days=number_days,
            kind="accommodation"
        )

        # create route for each day + routes between days
        itinerary_relationships = tx.run(
            query_relationships,
            POI=itinerary_days,
            days=number_days,
            accommodation="accommodation",
            cultural="cultural",
            religion="religion",
            food="food"
        )

        # adds start and end point to itinerary and gets shortest path
        complete_itinerary = tx.run(
            query_itinerary,
            POI=itinerary_relationships,
            start_node=start_node,
            end_node=end_node,
            days=number_days
        )

        print(complete_itinerary.values)

        # create map
        for x, y in zip(complete_itinerary.values.get('lat'), complete_itinerary.values.get('lon')):
            folium.Marker(([x, y])).add_to(folium.Map(location=[38.05968, 13.26699], zoom_start=13))

        return 'itinerary_map.html'
