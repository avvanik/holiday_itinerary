# Project | Holiday Itinerary in Palermo

/output
- Extraction data as point of interests from opentripmap api
- the data is saved as a simple csv file in /data

/db
- explanation of simple set up for neo4j db
- csv file is loaded into db and cleaned

/endpoint
- endpoints are developed through fastapi
- api and db are deployed in a docker-compose file
- run api through instructions above

- git clone

- cd endpoint/app
docker image build . -t fastapi:latest

- cd ../endpoint
- docker-compose up

- open db on PORT 0.0.0.0:7474

- open fastAPI on Port 0.0.0.0:8000

- /poi : returns all point of interests saved in the db
- /poi/nearest/{kind:str}/{lon:float}/{lat:float} : returns nearest point of interest in a folium map
- /poi/itinerary/start={start_lon:float}/{start_lat:float}/end={end_lon:float}/{end_lat:float}/{"
         "days:int} : suppose to return itinerary with start and end coordinates

