from neo4j import GraphDatabase
import folium
import os
from JAN23_BDE_INT_Holiday_Itinerary.endpoint.app._queries import query_cluster1, query_cluster2, query_cluster3, \
    query_cluster4, query_start_node, query_end_node, query_all, query_relationship_day, add_start_and_end_node, \
    query_end_node_set, query_start_node_set


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
            query_start_node,
            kind=kind,
            lon=lon,
            lat=lat
        ).values

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
            lon=start_lon
        )

        # set start node itinerary day = 1
        start_node = tx.run(
            query_start_node_set,
            start_node=start_node

        )

        # set end node
        end_node = tx.run(
            query_end_node,
            lat=end_lat,
            lon=end_lon)

        # set end node itinerary day = number days
        end_node = tx.run(
            query_end_node_set,
            end_node=end_node,
            day=number_days

        )

        # create route for each day + routes between days
        itinerary_relationships = tx.run(
            query_relationship_day,
            POI=itinerary_days,
            day=number_days
        )

        # adds start and end point to itinerary
        complete_itinerary = tx.run(
            add_start_and_end_node,
            POI=itinerary_relationships,
            start_node=start_node,
            end_node=end_node,
            day=number_days
        )

        print(complete_itinerary.values)

        # create map
        for x, y in zip(complete_itinerary.values.get('lat'), complete_itinerary.values.get('lon')):
            folium.Marker(([x, y])).add_to(folium.Map(location=[38.05968, 13.26699], zoom_start=13))

        return 'itinerary_map.html'
