import requests
import pandas as pd
from src.global_ import api_key, base_url, lon_max, lon_min, lat_max, lat_min, page_length, kind
from src.data import Prepare
import json as j


class Model:

    def __init__(self):
        self.url = f"{base_url}bbox?lon_min={lon_min}&lon_max={lon_max}&lat_min={lat_min}&lat_max={lat_max}&kinds" \
                   f"={kind}&format=json&"
        self.key = api_key

    def request_objects(self):
        request = [requests.get(
            f"{self.url}&apikey={api_key}&limit={page_length}&offset={page_length * i}").json()
                   for i in range(10)]
        return request

    def get_xid(self):

        xid_dict = {'xid': []}
        xid_list = []

        for request in self.request_objects():
            for key in request:
                xid_dict['xid'].append(key.get('xid'))

        for value in xid_dict.values():
            for element in value:
                xid_list.append(element)

        return xid_list

    def request_dict_detailed(self):

        collection = []

        for xid in self.get_xid():
            request = f"{base_url}xid/{xid}?apikey" \
                      f"={api_key}"
            json = requests.get(request).json()
            # address = Prepare(pd.read_json(request)).address_to_list()
            # del json['address']
            # json['address'] = address

            # for dic_key in dict_detailed.keys():
            # if dic_key not in json.keys():
            # json[dic_key] = 'null'

            collection.append(json)

            with open('output_test.json', 'w') as f:
                j.dump(collection, f)

            # get_schema(json)

        return collection  # dict_detailed

    # def create_csv(self):
    #     df = pd.DataFrame.from_dict(self.request_dict_detailed())
    #     df = Prepare(df).clean().set_index(['xid'])
    #     df.to_csv('places_output.csv')
    #     print("csv saved")
    #
    #     return df
