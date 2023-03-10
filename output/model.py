import requests
import pandas as pd
from global_ import api_key, base_url, lon_max, lon_min, lat_max, lat_min, page_length, dict_detailed, kinds
from data import Prepare, get_schema


class Model:

    def __init__(self):
        self.url = f"{base_url}bbox?lon_min={lon_min}&lon_max={lon_max}&lat_min={lat_min}&lat_max={lat_max}&"
        self.key = api_key

    def request_objects(self):

        objects = []

        for kind in kinds:
            request = [requests.get(
                f"{self.url}kinds={kind}&format=json&apikey={api_key}&limit={page_length}&offset={page_length * i}").json()
                       for i in range(2)]

            objects.append(request)

        return objects

    def get_xid(self):

        xid_dict = {'xid': []}
        xid_list = []

        for json in self.request_objects():
            for key in json:
                for value in key:
                    xid_dict['xid'].append(value.get('xid'))

        for value in xid_dict.values():
            for element in value:
                xid_list.append(element)

        return xid_list

    def request_dict_detailed(self):

        for xid in self.get_xid():
            request = f"{base_url}xid/{xid}?apikey" \
                      f"={api_key}"
            json = requests.get(request).json()
            address = Prepare(pd.read_json(request)).address_to_list()
            del json['address']
            json['address'] = address

            for dic_key in dict_detailed.keys():
                if dic_key not in json.keys():
                    json[dic_key] = 'null'
            get_schema(json)

        return dict_detailed

    def create_csv(self):
        df = pd.DataFrame.from_dict(self.request_dict_detailed())
        df = Prepare(df).clean()
        df.to_csv('/data/places_output.csv')
