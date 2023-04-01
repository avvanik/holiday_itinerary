query_all = 'MATCH (p:POI) ' \
            'RETURN p'

query_cluster1 = 'MATCH (p:POI) ' \
                 'WITH p, ' \
                 'rand() AS sortOrder ' \
                 'ORDER BY sortOrder ' \
                 'LIMIT $days ' \
                 'CREATE (d:Day) ' \
                 'SET d.location = p.location, d.iterations = 0 ' \
                 'RETURN *'

query_cluster2 = 'MATCH (d:Day) ' \
                 'WITH collect(d) AS days ' \
                 'UNWIND range(0, 7) AS day ' \
                 'SET (days[day]).itinerary_day = day ' \
                 '+ 1 RETURN days[day]'

query_cluster3 = 'MATCH (p:POI), (d:Day) ' \
                 'WITH p, d ' \
                 'ORDER BY point.distance(p.location, d.location) ' \
                 'WITH p, ' \
                 'collect(d) AS days ' \
                 'SET p.itinerary_day = days[0].itinerary_day'

query_cluster4 = 'MATCH (p:POI), (d:Day) ' \
                 'WHERE p.itinerary_day = d.itinerary_day ' \
                 'WITH d, ' \
                 'AVG(p.location.x) AS newX, ' \
                 'avg(p.location.y) AS newY ' \
                 'SET d.location = point({x:newX, y:newY}), d.iterations = d.iterations + 1'

query_start_node = 'MATCH (p:POI {kind: $kind}) ' \
                   'WITH p, p.location AS start, ' \
                   'point({latitude: $lat, longitude: $lon}) AS location ' \
                   'RETURN p, ' \
                   'ROUND(distance(start, location)) AS distance ' \
                   'ORDER BY distance ' \
                   'LIMIT 1'

query_end_node = 'MATCH (p:POI {kind: $kind}) ' \
                 'WITH p, p.location AS end, ' \
                 'point({latitude: $lat, longitude: $lon}) AS location' \
                 'RETURN p, ' \
                 'ROUND(distance(end, location)) AS distance ' \
                 'ORDER BY distance ' \
                 'LIMIT 1'

query_start_relationship = 'MATCH (s:$start_node) MATCH (p:POI {kind: $kind, itinerary_day: 1}) ' \
                           'WITH point.distance(s.location, p2.location) as distance, s, p ' \
                           'MERGE (s)-[:ROUTE { value: distance }]-(p)'

query_end_relationship = 'MATCH (e:$end_node) MATCH (p:POI {kind: $kind, itinerary_day: $days}) ' \
                         'WITH point.distance(s.location, p2.location) as distance, e, p ' \
                         'MERGE (e)-[:ROUTE { value: distance }]-(p)'

query_relationship_day = 'FOREACH p.itinerary_day' \
                         'MATCH(p1:POI {kind: $accommodation}),' \
                         'MATCH(p2:POI {kind: $cultural})' \
                         'WITH point.distance(p1.location, p2.location) as distance, ' \
                         'p1, p2 MERGE (p1)-[:ROUTE { value: distance }]-(p2) ' \
                         'MATCH(p1:POI {kind: $cultural}), ' \
                         'MATCH(p2:POI {kind: $religion}) ' \
                         'WITH point.distance(p1.location, p2.location) as distance, ' \
                         'p1, p2 MERGE (p1)-[:ROUTE { value: distance }]-(p2) ' \
                         'MATCH(p1:POI {kind: $religion}), ' \
                         'MATCH(p2:POI {kind: $food}) ' \
                         'WITH point.distance(p1.location, p2.location) as distance, ' \
                         'p1, p2 MERGE (p1)-[:ROUTE { value: distance }]-(p2)'

query_relationship_days = ''

query_itinerary = 'MATCH($start), (e:$end), ' \
                  'p = shortestPath((s)-[*]-(e)) ' \
                  'WHERE length(p) > 1 ' \
                  'RETURN p '
