lon_min = 13.26699  #13.78696
lon_max = 13.46199     #15.62158
lat_min = 38.05968 #37.76809
lat_max = 38.22250 #38.49400

base_url = 'https://api.opentripmap.com/0.1/en/places/'
api_key = '5ae2e3f221c38a28845f05b656934aef7d36d2c813d4ee1bc9d86b1d'

kind = 'accomodations'

#kinds = ['accomodations', 'adult', 'amusements', 'architecture', 'cultural', 'historic',
         #'industrial_facilities', 'natural', 'other', 'religion', 'sport', 'banks',
         #'foods', 'shops', 'transport']

kinds = ["accomodations", "churches", "museums", "foods"]

page_length = 100  # 300

dict_detailed = {'xid': [],
                 'name': [],
                 'url': [],
                 'stars': [],
                 'wikipedia': [],
                 'image': [],
                 'address': [],
                 'point': [],
                 'kinds': []}
