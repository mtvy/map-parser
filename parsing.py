
import requests

SEARCH_URL = 'https://search-maps.yandex.ru/v1/'

API_KEY = 'f49ce4e7-2f3f-46ba-b33e-da64cfbe94d7'


def is_valid(elem):
    return elem if elem else None


class Item:

    def __init__(self, item) -> None:

        prts = item[  'properties'   ]
        meta = prts['CompanyMetaData']

        self.coordinates = item[ 'geometry' ]['coordinates']
        self.name        = prts[   'name'    ]
        self.description = prts['description']
        self.boundedBy   = prts[ 'boundedBy' ]
        self.id          = meta['id']
        self.mata_name   = meta['name']
        self.address     = meta['address']
        self.categories  = meta['Categories']

        try:
            self.hours          = meta['Hours']['text']
            self.availabilities = meta['Hours']['Availabilities']
        except:
            self.hours = self.availabilities = None

    def __str__(self) -> str:
        return (
            f'# id:          {self.id}         \n'
            f'> name:        {self.name}       \n'
            f'> description: {self.description}\n'
            f'> categories:  {self.categories} \n'
            f'> address:     {self.address}    \n'
        )


class Directory:

    def __init__(self, search, items, found, added) -> None:
        self.search = search
        self.items = items
        self.found = found
        self.added = added

    def add_item(self, new_item):
        for item in self.items:
            if item.id == new_item.id:
                return False
        self.items.append(new_item)
        self.added += 1
        return True

    def __str__(self) -> str:
        return (
            f'# Search: {self.search}\n'
            f'> Found:  {self.found} \n'
            f'> Added:  {self.added} \n'
        )



def get_data(text, result, skip, type = 'biz', lang = 'ru_RU'):
    return requests.get(
        f'{SEARCH_URL}?text={text}&type={type}&lang={lang}&results={result}&skip={skip}&apikey={API_KEY}'
    ).json()


def pars(items = []):

    data1 = get_data('автомойка москва', 1000, 0)

    items = [Item(data1['features'][ind]) for ind in range(len(data1['features']))]

    found = data1['properties']['ResponseMetaData']['SearchResponse']['found']

    search = data1['properties']['ResponseMetaData']['SearchRequest']['request']

    directory = Directory(search, items, found, len(items))

    data1 = get_data('автомойка москва', 1000, 500)

    for ind in range(len(data1['features'])):
        directory.add_item(Item(data1['features'][ind]))

    data1 = get_data('автомойка москва', 1000, 1000)

    for ind in range(len(data1['features'])):
        directory.add_item(Item(data1['features'][ind]))

    directory.found = data1['properties']['ResponseMetaData']['SearchResponse']['found']

    print(directory)

    print(directory.items[0])


if __name__ == '__main__':
    pars()

