#/==================================================================\#
#                                                                    #
#\==================================================================/#

#\==================================================================/#
from typing import Dict, List, Tuple
import requests, sys

from CustomSet import *

from variables import *
#\==================================================================/#

#\==================================================================/#
SEARCH_URL = 'https://search-maps.yandex.ru/v1/'

API_KEY = 'f49ce4e7-2f3f-46ba-b33e-da64cfbe94d7'

API_KEY_SET = [API_KEY, '604bc3ff-6e7a-4400-bf1d-0b5a10ff24b8']

RESULT_LIM = 500
#\==================================================================/#

#\==================================================================/#
class Item:
    """### Special class for Yandex Dictionary Item ###"""

    def __init__(self, item : Dict) -> None:

        buffer = item['properties']['CompanyMetaData']

        self.__name        = item['properties'][   'name'    ]
        self.__description = item['properties']['description']

        self.__id          = int(buffer['id'])

        self.__address     = buffer['address'   ]
        self.__categories  = buffer['Categories']

        self.__available = self.__phones = self.__hours = None
        

        if 'Hours' in buffer.keys():
            if 'Availabilities' in buffer['Hours'].keys():
                self.__available = buffer['Hours']['Availabilities']

            if 'text' in buffer['Hours'].keys():
                self.__hours = buffer['Hours']['text']
            
        if 'Phones' in buffer.keys():
            self.__phones = buffer['Phones']

        del buffer

    def __str__(self) -> str:
        return (
            f'# id: {self.__id}                        \n'
            f'>     name:           {self.__name}       \n'
            f'>     description:    {self.__description} \n'
            f'>     categories:     {self.__categories}   \n'
            f'>     address:        {self.__address}       \n'
            f'>     phone:          {self.__phones}         \n'
            f'>     hours:          {self.__hours}           \n'
            f'>     availabilities: {self.__available}        \n'
        )
    
    def __del__(self) -> None:
        del self.__id ,   self.__phones    , self.__categories    
        del self.__name,   self.__address   , self.__description   
        del self.__hours,   self.__available
    
    @property
    def id(self) -> int:
        return self.__id
#\==================================================================/#

#\==================================================================/#
class Catalog(CustomSet):
    """### Special set for unique categories (str elements)"""
    def __init__(self, _categories : List[str] = []):
        super().__init__(_categories)

    def __str__(self) -> str:
        return super().__str__('# Catalog\n')
#\==================================================================/#

#\==================================================================/#
class ItemsList(CustomSet):
    """List for Item Object"""

    def __init__(self, _items : List[Item] = []) -> None:
        self.__ids = []
        super().__init__(self.__init_ids(_items))

    def __init_ids(self, _items : List[Item]) -> List[Item]:
        items = []
        for item in _items:
            if item.id not in self.__ids:
                self.__ids.append(item.id)
                items.append(item)
        return items

    def __set_ids(self, _items : List[Item]) -> List[int]:
        return [_item.id for _item in _items]

    def __contains__(self, item : Item) -> bool:
        return True if item.id in self.__ids else False

    def __get_ids_inds(self, _items):
        """Pushes unique id index"""
        _ids = self.__set_ids(_items)
        return ([ind for ind in range(len(_ids)) 
                    if _ids[ind] not in self.__ids], _ids)
    
    def __add(self, elem) -> List:
        """
        ItemsList:
            get elem ids and 
        """
        if isinstance(elem, ItemsList):
            aval_ids_inds, _ids = self.__get_ids_inds(elem)
            for ind in aval_ids_inds:
                self.elems.append(elem[ind])
                self.__ids.append(_ids[ind])

        elif isinstance(elem, Item):
            if elem.id not in self.__ids:
                self.__ids.append(elem.id)
                self.elems.append(elem)

        return self.elems

    def __add__(self, elem) -> object:
        self.elems = self.__add(elem)
        self.len = len(self.elems)
        return self

    def __iadd__(self, elem) -> object:
        self.elems = self.__add(elem)
        self.len = len(self.elems)
        return self
    
    def __str__(self) -> str:
        return super().__str__('# ItemsList\n')
    
    def __del__(self) -> None:
        super().__del__()
        del self.__ids
    
    @property
    def ids(self) -> List[int]:
        return self.__ids
#\==================================================================/#

#\==================================================================/#
class Directory:

    def __init__(self, _tag : str = 'Directory') -> None:
                       
        self.__items   = ItemsList()
        self.__catalog = Catalog()
        self.__parsing = True
        self.__status  = True
        self.__tag     = _tag

    def __req(self, txt  : str, res     : int, 
                    skip : int, api_key : str) -> Dict:
        req = requests.get(
            f'{SEARCH_URL}?text={txt}&type=biz&lang=ru_RU'
            f'&results={res}&skip={skip}&apikey={api_key}'
        ).json()
        return False if 'features' not in req.keys() else req['features']
    
    def __str__(self) -> str:
        return (f'!{self.__tag}\n'
                f'|> Added: {len(self.__items)}\n')

    def __proc_req(self, category : str, 
                         api_key  : str, 
                         passes   : Tuple[int] = (0, 500, 1000), 
                         result   : int = RESULT_LIM) -> List[Item]:
        added = []
        self.__parsing = True
        for skip in passes:
            data = self.__req(category, result, skip, api_key)

            if data:
                added += self.add_items(data)
            elif data == []:
                break
            else:
                self.__parsing = False
                break
           
            if len(data) < skip//1.2:
                break
            
        return added

    def update(self, api_key : str = API_KEY) -> List[Item]:
        added = []
        for elem in self.__catalog:
            added += self.__proc_req(elem, api_key)
        return added

    def set_items(self, elem : str, api_key = API_KEY) -> List[Item]:
        self.__catalog += elem
        return self.__proc_req(elem, api_key)

    def add_items(self, _its : ItemsList) -> List[Item]:
        added = []
        buffer_len = len(self.__items)
        for _it in _its:
            self.__items += Item(_it)
            if len(self.__items) > buffer_len:
                added.append(self.__items[-1])
                buffer_len += 1
        return added

    def add_item(self, _item : Item) -> Item:
        if _item.id in self.__items.ids:
            return False
        self.__items += _item
        return _item

    def set_directory(self, catalog : Catalog, 
                            api_key : str = API_KEY) -> List[Item]:
        added = []
        for item in catalog:
            added += self.set_items(item, api_key)
            if not self.__parsing: 
                break
        return added

    def clear(self) -> None:
        self.__items  .clear()
        self.__catalog.clear()

    @property
    def items(self) -> ItemsList:
        return self.__items
    
    @property
    def catalog(self) -> Catalog:
        return self.__catalog
    
    @property
    def parsing(self) -> bool:
        return self.__parsing

    @property
    def status(self) -> bool:
        return self.__status
    
    @status.setter
    def status(self, turn : bool) -> None:
        if isinstance(turn, bool):
            self.__status = turn
    
#\==================================================================/#

#\==================================================================/#
def UnitTest() -> None:

    def __catalogTest() -> None:
        """
        UnitTest for Catalog
        """
        ct, ct2, ct3 = (Catalog(), 
                        Catalog([f'cat{i + 1}' for i in range(20)]), 
                        Catalog(['sp_cat1']))

        print(ct2, ct3, ct)

        ct3 += ct2

        print(ct2, ct3, ct)

        ct2.clear()

        ct2 += 'sp_cat2'

        print(ct2, ct3[22], ct3[-1])

        if 'cat8' in ct3:
            for i in ct3:
                print(i) 
        
        del ct3['cat5'], ct3['cat4'], ct3['cat8']

        del ct2['sp_cat2']

        print(ct3, f'len ct3 {len(ct3)}')
        print(ct2, f'len ct2 {len(ct2)}')

        b = 0
        for i in range(10000):
            if b == 1000:
                print(f'> {(10000 - i) // 1000}')
                b = 0
            ct += f'mem{i}'
            b += 1

        print(
            f'Size of Catalog object after pushing elements: {ct.__sizeof__()} Mb\n'
            f'With len: {len(ct)} and average size: {sys.getsizeof(ct[-1])} byte'
        )

        ct.clear()

        print(f'Size of Catalog object after clear(): {ct.__sizeof__()} byte\n')

        del ct, ct2, ct3

    def __createItem(_id = 812, _cat = 'Cat') -> Item:
        return Item({
            'properties' : {
                'CompanyMetaData' : {
                    'id'         : _id,
                    'address'    : 'Address',
                    'Categories' : [_cat]
                },
                'name'        : 'Name',
                'description' : 'Info'
            }
        })

    def __itemTest() -> None:
        """
        UnitTest for Item
        """
        it = __createItem() 

        print(it)

        del it

    def __itemsListTest() -> None:
        """
        UnitTest for ItemsList
        """
        its = ItemsList([__createItem(), __createItem(), __createItem(92)])

        its2 = ItemsList()

        print(its, '\n')

        print(its2, '\n')

        its2 += __createItem()

        print(its2, '\n')

        its2 += its

        its2 += __createItem(911)

        print(its2, '\n')

        if __createItem() in its:
            for it in its2:
                print(it)

        del its

    def __directoryTest() -> None:
        """
        UnitTest for Directory
        """
        dr = Directory('dr')

        print(dr)

        dr.set_directory(Catalog(['cat1', 'cat2', 'cat3']))

        print(dr, dr.catalog)

        dr.update()

        print(dr)

        dr2 = Directory()

        dr2.set_items('sp_cat') ### ???

        print(dr2, dr2.catalog)

#1
    __catalogTest()
#2
    __itemTest()
#3
    __itemsListTest()
#4
    __directoryTest()
#\=================================================================/#

#\==================================================================/#
if __name__ == '__main__':
    UnitTest()
#\==================================================================/#
