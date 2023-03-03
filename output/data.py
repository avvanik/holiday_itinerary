import pandas as pd
from global_ import dict_detailed


def get_address(address_fields):
    address = ''
    for field in address_fields:
        address += field + ' '
    return address


def get_schema(json):

    for key in list(json):
        if key == 'xid':
            dict_detailed['xid'].append(json.get('xid'))
        elif key == 'name':
            dict_detailed['name'].append(json.get('name'))
        elif key == 'url':
            dict_detailed['url'].append(json.get('url'))
        elif key == 'stars':
            dict_detailed['stars'].append(json.get('stars'))
        elif key == 'wikipedia':
            dict_detailed['wikipedia'].append(json.get('wikipedia'))
        elif key == 'image':
            dict_detailed['image'].append(json.get('image'))
        elif key == 'address':
            dict_detailed['address'].append(json.get('address'))
        elif key == 'point':
            dict_detailed['point'].append(json.get('point'))
        elif key == 'kinds':
            dict_detailed['kinds'].append(json.get('kinds'))


class Prepare:

    def __init__(self, df):
        self.df = df

    def clean(self):
        self.df[['lon', 'lat']] = self.df['point'].apply(lambda x: pd.Series(str(x).split(',')))
        df = self.df.drop('point', axis=1)
        df['lon'] = df['lon'].str[8:]
        df['lat'] = df['lat'].str[8:]
        df['lat'] = df['lat'].str[:-1]
        return df

    def address_to_list(self):
        address_list = self.df['address'].values.tolist()
        address = get_address([x for x in address_list if str(x) != 'nan'])
        return address
