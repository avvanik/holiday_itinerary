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
                 'SET (days[day]).itinerary_day = day + 1 ' # check

query_cluster3 = 'MATCH (p:POI), (d:$Day) ' \
                 'WITH p, d ' \
                 'ORDER BY distance(p.location, d.location) ' \
                 'WITH p, ' \
                 'collect(d) AS days ' \
                 'SET p.itinerary_day = days[0].itinerary_day' \
                 'RETURN p'

query_cluster4 = 'MATCH (p:$POI), (d:$Day) ' \
                 'WHERE p.itinerary_day = d.itinerary_day ' \
                 'WITH d, ' \
                 'AVG(p.location.x) AS newX, ' \
                 'AVG(p.location.y) AS newY ' \
                 'SET d.location = point({x:newX, y:newY}), d.iterations = d.iterations + 1' # check

query_start_node = 'WITH point({ longitude: $longitude, latitude: $latitude }) AS location' \
                   'MATCH (p:POI {kind: $kind})' \
                   'WITH p, distance(p.point, location) AS dist' \
                   'ORDER BY dist' \
                   'LIMIT 1' \
                   'WITH h, point({ longitude: $longitude, latitude: $latitude }) AS location' \
                   'CREATE (s:Start)' \
                   'SET s = p' \
                   'SET s.itinerary_day=1' \
                   'SET s.point = location' \
                   'RETURN s'

query_end_node = 'WITH point({ longitude: $longitude, latitude: $latitude }) AS location' \
                 'MATCH (p:POI {kind: $kind})' \
                 'WITH p, distance(p.point, location) AS dist' \
                 'ORDER BY dist' \
                 'LIMIT 1' \
                 'WITH h, point({ longitude: $longitude, latitude: $latitude }) AS location' \
                 'CREATE (e:End)' \
                 'SET e = h' \
                 'SET e.itinerary_day=$days' \
                 'SET e.point = location' \
                 'RETURN e'

# pass number days as parameter and create relationships for each day
query_relationships = 'MATCH (p:$poi {itinerary_day: $days}) ' \
                      'FOREACH (day in p.itinerary_day | ' \
                      'CREATE (a:POI {kind: $accommodation, itinerary_day: day})-[:ROUTE]-> ' \
                      '(b:POI {kind: [$cultural, $religion],' \
                      'itinerary_day: day})-[:ROUTE]-> ' \
                      '(c:POI {kind: $food, itinerary_day: day})' \
                      'CREATE (c)-[:ROUTE]->(a2:POI {kind: $accommodation, ' \
                      'itinerary_day: day+1}))'

# find the shortest path between the start node and the end node
query_itinerary = 'MATCH (start:$start_node), (p1:POI {kind: $accommodation, itinerary_day: 1}), ' \
                  '(p2:POI {kind: $accommodation, itinerary_day: $days}), (end:$end_node)' \
                  'MATCH path = shortestPath((start)-[:START]->(p1)-[:ROUTE*]->(p2)-[:ROUTE*]->(end))' \
                  'RETURN path'
