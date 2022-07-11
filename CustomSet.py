"""
MIT License

Copyright (c) 2022 Mtvy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
#\=============================================================================/#
from typing import Iterator, List, Any
import sys
#\=============================================================================/#

#\=============================================================================/#
class CustomSet:
    """
    Special Set for unique elements
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    >>> Use operators below to control this object
             +-------------------------+
    >>>      | 1. +=         4. clear()|
    >>>      | 2. +          5. del    |
    >>>      | 3. len()      6. iter() |
             +-------------------------+
    
    :note: If you are using a custom object, 
           you need to make sure that the 
           __contains__ method is implemented.
    """

    def __init__(self, _elems : List = []) -> None:
        self.__elems = _elems
        self.__len = len(_elems)
    
    def __str__(self, out : str = '# CustomSet\n') -> str:
        buffer = out
        for ind, elem in zip(range(self.__len), self.__elems):
            out += f'|{ind + 1}. {elem}\n'
        return out if out != buffer else f'{out}|0.\n'

    def __len__(self) -> int:
        return self.__len

    def __iter__(self) -> Iterator:
        return iter(self.__elems)

    def __contains__(self, elem) -> bool:
        return True if elem in self.__elems else False

    def __getitem__(self, index : int) -> Any:
        if ((self.__len > index and index >= 0) or 
            (self.__len >= -index and index < 0)):
            return self.__elems[index]
        else:
            return False
    
    def __sizeof__(self) -> int:
        elem_size = sum([sys.getsizeof(elem) for elem in self.__elems])
        return (elem_size + sys.getsizeof(self.__elems) 
                          + sys.getsizeof( self.__len )) / (1024**2)

    def __add(self, elem) -> List:
        if isinstance(elem, CustomSet):
            self.__len += len(elem)
            return self.__elems + list(filter(
                lambda el: el not in self.__elems, 
                elem.__elems
            ))
        else:
            return self.__elems + (
                [elem] if elem not in self.__elems else []
            )

    def __add__(self, elem) -> object:
        self.__elems = self.__add(elem)
        self.__len = len(self.__elems)
        return self

    def __iadd__(self, elem) -> object:
        self.__elems = self.__add(elem)
        self.__len = len(self.__elems)
        return self
    
    def clear(self) -> object:
        self.__elems.clear()
        self.__len = 0
        return self
    
    def __delitem__(self, elem : Any) -> bool:
        if elem in self.__elems: 
            self.__elems.remove(elem)
            self.__len -= 1
            return True
        return False
    
    def __del__(self) -> None:
        del self.__elems, self.__len

    @property
    def elems(self) -> List:
        return self.__elems
    
    @property
    def len(self) -> List:
        return self.__len
    
    @elems.setter
    def elems(self, _elems : List) -> None:
        self.__elems = _elems
    
    @len.setter
    def len(self, _len : int) -> None:
        self.__len = _len
#\=============================================================================/#

#\=============================================================================/#
def __UnitTest() -> None:
    """UnitTest for CustomSet"""
    ct, ct2, ct3 = (CustomSet(), 
                    CustomSet([f'cat{i + 1}' for i in range(20)]), 
                    CustomSet(['sp_cat1']))

    print(ct2, ct3, ct, '\n')

    ct3 += ct2

    print(ct2, ct3, ct, '\n')

    ct2.clear()

    ct2 += 'sp_cat2'

    print(ct2, ct3[22], ct3[-1], '\n')

    if 'cat8' in ct3:
        for i in ct3:
            print(i) 
    
    del ct3['cat5'], ct3['cat4'], ct3['cat8']

    del ct2['sp_cat2']

    print(ct3, f'len ct3 {len(ct3)}', '\n')
    print(ct2, f'len ct2 {len(ct2)}', '\n')

    b = 0
    for i in range(10000):
        if b == 1000:
            print(f'> {(10000 - i) // 1000}')
            b = 0
        ct += f'mem{i}'
        b += 1

    print(
        f'Size of CustomSet object after pushing elements: {ct.__sizeof__()} Mb\n'
        f'With len: {len(ct)} and average size: {sys.getsizeof(ct[-1])} byte'
    )

    ct.clear()

    print(f'Size of CustomSet object after clear(): {ct.__sizeof__()} byte\n')

    del ct, ct2, ct3
#\==================================================================/#

#\==================================================================/#
if __name__ == '__main__':
    __UnitTest()
#\==================================================================/#
