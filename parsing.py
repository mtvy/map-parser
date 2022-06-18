#/==================================================================\#
#                                                                    #
#\==================================================================/#

#\==================================================================/#
from typing import Dict, List
import requests

from variables import *
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
    
    def __del__(self):
        del self.id         
        del self.name       
        del self.phones
        del self.hours         
        del self.address    
        del self.boundedBy  
        del self.mata_name  
        del self.categories
        del self.description
        del self.coordinates
        del self.availabilities

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

    def __init__(self, categories : List[str] = []) -> None:
        self.__categories = categories
        self.__len = len(categories)

    def __len__(self):
        return self.__len

    def __contains__(self, elem):
        return True if elem in self.__categories else False

    def __getitem__(self, index : int) -> str:
        if len(self.__categories) >= abs(index + 1):
            return self.__categories[index]
        else:
            return False

    def del_item(self, category : str) -> bool:
        if category in self.__categories: 
            self.__categories.remove(category)
            self.__len -= 1
            return True
        return False

    def __delitem__(self, category : str) -> bool:
        if category in self.__categories: 
            self.__categories.remove(category)
            self.__len -= 1
            return True
        return False

    def __add(self, elem) -> List[str]:
        if isinstance(elem, str):
            return self.__categories + (
                [elem] if elem not in self.__categories else []
            )
        elif isinstance(elem, Catalog):
            self.__len += 1
            return self.__categories + list(filter(
                lambda it: it not in self.__categories, 
                elem.__categories
            ))

    def __add__(self, elem) -> object:
        self.__categories = self.__add(elem)
        self.__len = len(self.__categories)
        return self

    def __iadd__(self, elem) -> object:
        self.__categories = self.__add(elem)
        self.__len = len(self.__categories)
        return self
    
    def clear(self):
        self.__categories.clear()
        self.__len = 0
        return self
        
    def __str__(self, out : str = '# Catalog\n') -> str:
        for ind, category in zip(range(len(self.__categories)), self.__categories):
            out += f'|{ind + 1}. {category}\n'
        return out
#\==================================================================/#

#\==================================================================/#
class Directory:

    def __init__(self, catalog    : Catalog    = Catalog(),
                       items      : List[Item] = [], 
                       added      : int        = 0 , 
                       boundedBy  : List[List[int]] = [],
                       properties : List = []) -> None:
                       
        self.catalog    = catalog
        self.items      = items
        self.added      = added
        self.boundedBy  = boundedBy
        self.properties = properties
        self.parsing    = True

    def clear(self):
        for item in self.items:
            del item

        self.items     .clear()
        self.catalog   .clear()
        self.boundedBy .clear()
        self.properties.clear()

        self.added = 0

    def update(self, result = RESULT_LIM, passes = (0, 500)):
        added = []
        for ind in range(len(self.catalog)):
            for skip in passes:
                data = get_data(self.catalog[ind], result, skip)
                
                if ('features' in data.keys()):
                    self.parsing = True

                    added = self.add_items(data['features'])

                    self.properties.append(data['properties'])
                else:
                    self.parsing = False
        
        return added

    def set_items(self, category, result = RESULT_LIM, passes = (0, 500)) -> None:
        self.catalog += category
        
        for skip in passes:
            data = get_data(self.catalog[-1], result, skip)
            
            if ('features' in data.keys()):
                self.parsing = True

                self.add_items(data['features'])

                self.boundedBy = data['properties']['ResponseMetaData']['SearchRequest']['boundedBy']

                self.properties.append(data['properties'])
            else:
                    self.parsing = False

    def add_items(self, new_items) -> None:
        added = []
        for ind in range(len(new_items)):
            succeed = self.add_item(Item(new_items[ind]))
            if succeed: added.append(succeed)
        return added
        

    def add_item(self, new_item) -> bool:
        for item in self.items:
            if item.id == new_item.id:
                return False
        self.items.append(new_item)
        self.added += 1
        return new_item

    def set_directory(self, catalog) -> None:
        if isinstance(catalog, str):
            for category in catalog:
                self.set_items(category)
        elif isinstance(catalog, Catalog):
            for ind in range(len(catalog)):
                self.set_items(catalog[ind])

    def __str__(self) -> str:
        return (
            f'!Directory\n'
            f'|{self.catalog}'
            f'|> Added:      {self.added}     \n'
            f'|> BoundedBy:  {self.boundedBy} \n'
        )
#\==================================================================/#

#\==================================================================/#
def get_data(text, result, skip, type = 'biz', lang = 'ru_RU') -> Dict:
    return requests.get(
        f'{SEARCH_URL}?text={text}'
                    f'&type={type}'
                    f'&lang={lang}'
                 f'&results={result}'
                    f'&skip={skip}'
                  f'&apikey={API_KEY}'
    ).json()
#\==================================================================/#

#\==================================================================/#
if __name__ == '__main__':

    cat = Catalog(['lol', 'lal', 'kok'])

    cat += 'pop'

    print(cat)

    test_cat = Catalog(['1', '3', '2'])
    
    cat += test_cat

    print(cat)


    directory = Directory()

    directory.set_items( 'автомойка Центральный административный округ'      )
    directory.set_items( 'автомойка Северный административный округ'         )

    print(directory)
    print(directory.items[-1])

    print(directory.catalog)
    
    print(directory.catalog[-1])

    print(directory.update())

    directory.catalog.del_item('автомойка Северный административный округ')

    print(directory.catalog)

    directory.catalog += 'test_adding_str'

    print(directory.catalog)

    directory.catalog += cat

    print(directory.catalog)
  #\==================================================================/#
  
