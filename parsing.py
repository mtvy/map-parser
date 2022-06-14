
import requests

SEARCH_URL = 'https://search-maps.yandex.ru/v1/'

API_KEY = 'f49ce4e7-2f3f-46ba-b33e-da64cfbe94d7'

RESULT_LIM = 500


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
        
        try:
            self.phones = meta['Phones']
        except:
            self.phones = None



    def __str__(self) -> str:
        return (
            f'# id: {self.id}                            \n'
            f'>     name:           {self.name}          \n'
            f'>     description:    {self.description}   \n'
            f'>     categories:     {self.categories}    \n'
            f'>     address:        {self.address}       \n'
            f'>     phone:          {self.phones}        \n'
            f'>     availabilities: {self.availabilities}\n'
            f'>     boundedBy:      {self.boundedBy}     \n'
        )


class Directory:

    def __init__(self, search = [], items = [], added = 0, boundedBy = []) -> None:
        self.search = search
        self.items = items
        self.added = added
        self.boundedBy = boundedBy

    def set_items(self, search, result = RESULT_LIM):
        self.search.append(search)
        
        for skip in (0, 500, 1000):
            data = get_data(self.search[-1], result, skip)
            
            self.add_items(data['features'])

            self.boundedBy = data['properties']['ResponseMetaData']['SearchRequest']['boundedBy']

    def add_items(self, new_items):
        for ind in range(len(new_items)):
            self.add_item(Item(new_items[ind]))

    def add_item(self, new_item):
        for item in self.items:
            if item.id == new_item.id:
                return False
        self.items.append(new_item)
        self.added += 1
        return True

    def set_directory(self, catalog):
        for category in catalog:
            self.set_items(category)

    def __str__(self) -> str:
        return (
            f'# Search:    {self.search}   \n'
            f'> Added:     {self.added}    \n'
            f'> BoundedBy: {self.boundedBy}\n'
        )



def get_data(text, result, skip, type = 'biz', lang = 'ru_RU'):
    return requests.get(
        f'{SEARCH_URL}?text={text}&type={type}&lang={lang}&results={result}&skip={skip}&apikey={API_KEY}'
    ).json()



if __name__ == '__main__':
    directory = Directory()

    directory.set_items( 'автомойка Центральный административный округ'      )
    directory.set_items( 'автомойка Северный административный округ'         )
    directory.set_items( 'автомойка Северо-Восточный административный округ' )
    directory.set_items( 'автомойка Восточный административный округ'        )
    directory.set_items( 'автомойка Юго-Восточный административный округ'    )
    directory.set_items( 'автомойка Южный административный округ'            )
    directory.set_items( 'автомойка Юго-Западный административный округ'     )
    directory.set_items( 'автомойка Западный административный округ'         )
    directory.set_items( 'автомойка Северо-Западный административный округ'  )
    
    print(directory)
    



