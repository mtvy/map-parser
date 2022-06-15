#/==================================================================\#
#                                                                    #
#\==================================================================/#

#\==================================================================/#
from typing import Dict, List, Set
import requests
#\==================================================================/#

#\==================================================================/#
SEARCH_URL = 'https://search-maps.yandex.ru/v1/'

API_KEY = 'f49ce4e7-2f3f-46ba-b33e-da64cfbe94d7'

RESULT_LIM = 500
#\==================================================================/#

#\==================================================================/#
class Item:

    def __init__(self, item : Dict) -> None:

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
#\==================================================================/#

#\==================================================================/#
class Catalog:

    def __init__(self, categories : List[str] = []):
        self.__categories = categories

    def __getitem__(self, index : int) -> str:
        if len(self.__categories) > abs(index):
            return self.__categories[index]
        else:
            return False

    def __delitem__(self, category : str) -> bool:
        if category in self.__categories: 
            self.__categories.remove(category)
            return True
        return False

    def __iadd__(self, category : str):
        self.__categories.append(category)
        
    def __str__(self, out : str = '# Catalog\n') -> str:
        for ind, category in zip(range(len(self.__categories)), self.__categories):
            out += f'{ind}. {category}\n'
        return out
#\==================================================================/#

#\==================================================================/#
class Directory:

    def __init__(self, catalog   : Catalog    = Catalog(),
                       items     : List[Item] = [], 
                       added     : int        = 0 , 
                       boundedBy : List[List[int]] = []) -> None:
                       
        self.catalog   = catalog
        self.items     = items
        self.added     = added
        self.boundedBy = boundedBy

    def set_items(self, category, result = RESULT_LIM, passes = (0, 500, 1000):
        self.catalog += category
        
        for skip in passes:
            data = get_data(self.catalog[-1], result, skip)
            
            self.add_items(data['features'])

            self.boundedBy = data['properties']['ResponseMetaData']['SearchRequest']['boundedBy']

    def add_items(self, new_items):
        for ind in range(len(new_items)):
            self.add_item(Item(new_items[ind]))

    def add_item(self, new_item) -> bool:
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
            f'{self.catalog}'
            f'> Added:     {self.added}    \n'
            f'> BoundedBy: {self.boundedBy}\n'
        )
#\==================================================================/#

#\==================================================================/#
def get_data(text, result, skip, type = 'biz', lang = 'ru_RU'):
    return requests.get(
        f'{SEARCH_URL}?text={text}&type={type}&lang={lang}&results={result}&skip={skip}&apikey={API_KEY}'
    ).json()
#\==================================================================/#

#\==================================================================/#
if __name__ == '__main__':

    directory = Directory()

    directory.set_items( 'автомойка Центральный административный округ'      )
    directory.set_items( 'автомойка Северный административный округ'         )

    print(directory)
    print(directory.items[-1])

    print(directory.catalog)
    
    print(directory.catalog[-1])

    del directory.catalog['автомойка Северный административный округ']

    print(directory.catalog) 
  #\==================================================================/#
  
