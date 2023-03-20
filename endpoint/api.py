from fastapi import FastAPI

# connect to neo4j
todo = "todo"

api = FastAPI(
    title="POI in Palermo",
    description="API returns specified POI in chosen area"
)


@api.get('/poi/{kind:str}/{lon:float}/{lat:float}', name="returns poi of specified kind and coordinates")
def get_questions(kind, lon, lat):
    point = lon * lat  # todo right calculation

    try:
        filter_kind = list(filter(lambda x: x.get('kind') == kind, todo))

        try:
            filter_point = list(filter(lambda x: x.get('point') == point, filter_kind))
            return filter_point

        except IndexError:
            return print(f"no poi at this coordinate: {point}")

    except IndexError:
        return print(f"no {kind} in this area")
