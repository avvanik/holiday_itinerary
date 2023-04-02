"""POI refers to each point of interest as node in database Clusters create additional nodes named as Day for each
itinerary day The nearest POI is calculated for start and end node which refers to nodes as start_node and end_node
Itinerary for each day is being created by connecting each kind with ROUTE relationship Route between days is being
created by connecting the accommodations of each day with accommodations of next day Start point for itinerary is
created by adding start node as first route to accommodations of itinerary day = 1 End point for itinerary is created
by adding end node as last route from accommodations of itinerary day = number of chosen days"""


query_all = 'MATCH (p:POI) ' \
            'RETURN p'

query_cluster1 = 'MATCH (p:POI) ' \
                 'WITH p, ' \
                 'rand() AS sortOrder ' \
                 'ORDER BY sortOrder ' \
                 'LIMIT $days ' \
                 'CREATE (d:Day) ' \
                 'SET d.location = p.location, d.iterations = 0 ' \
                 'RETURN d'

query_cluster2 = 'MATCH (d:$Day) ' \
                 'WITH collect(d) AS days ' \
                 'UNWIND range(0, $days) AS day ' \
                 'SET (days[day]).itinerary_day = day + 1 ' \
                 'RETURN d'

query_cluster3 = 'MATCH (p:POI), (d:$Day) ' \
                 'WITH p, d ' \
                 'ORDER BY point.distance(p.location, d.location) ' \
                 'WITH p, ' \
                 'collect(d) AS days ' \
                 'SET p.itinerary_day = days[0].itinerary_day' \
                 'RETURN p'

query_cluster4 = 'MATCH (p:$POI), (d:$Day) ' \
                 'WHERE p.itinerary_day = d.itinerary_day ' \
                 'WITH d, ' \
                 'AVG(p.location.x) AS newX, ' \
                 'AVG(p.location.y) AS newY ' \
                 'SET d.location = point({x:newX, y:newY}), d.iterations = d.iterations + 1' \
                 'RETURN p'

query_start_node = 'MATCH (p:POI {kind: accommodation}) ' \
                   'WITH p, p.location AS start, ' \
                   'point({latitude: $lat, longitude: $lon}) AS location ' \
                   'RETURN p, ' \
                   'ROUND(distance(start, location)) AS distance ' \
                   'ORDER BY distance ' \
                   'LIMIT 1'

query_start_node_set = 'MATCH(s:$start_node)' \
                       'SET itinerary_day=1' \
                       'RETURN s'

query_end_node = 'MATCH (p:POI {kind: accommodation}) ' \
                 'WITH p, p.location AS end, ' \
                 'point({latitude: $lat, longitude: $lon}) AS location' \
                 'RETURN p, ' \
                 'ROUND(distance(end, location)) AS distance ' \
                 'ORDER BY distance ' \
                 'LIMIT 1'

query_end_node_set = 'MATCH(e:$end_node)' \
                     'SET itinerary_day=$day' \
                     'RETURN e'

# pass number days as parameter and create relationships for each day
query_relationship_day = 'MATCH (p:$POI {itinerary_day: $days}) ' \
                         'FOREACH (day in p.itinerary_day) ' \
                         'CREATE (p:POI {kind: accommodation})-[:ROUTE]->(p:POI {kind: cultural}) ' \
                         'CREATE (p:POI {kind: cultural})-[:ROUTE]->(p:POI {kind: religion}) ' \
                         'CREATE (p:POI {kind: religion})-[:ROUTE]->(p:POI {kind: food})' \
                         'CREATE (p:POI {kind: accommodation})-[:ROUTE]->(p:POI {kind: accommodation, itinerary_day; ' \
                         '$days+1})'

add_start_and_end_node = 'MATCH(s:$start_node)' \
                         'MATCH(e:$end_node)' \
                         'MATCH(p:$POI)' \
                         'CREATE (s)-[:ROUTE]->(p {kind: accommodation, itinerary_day:1})' \
                         'CREATE (p {kind: accommodation, itinerary_day:$day})[:ROUTE]->(e)'

query_itinerary = 'MATCH($start), (e:$end), ' \
                  'p = shortestPath((s)-[*]-(e)) ' \
                  'WHERE length(p) > 1 ' \
                  'RETURN p '
