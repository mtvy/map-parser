import io, base64

from typing import Any, Dict


def toBytes(text):
    return bytes(text.encode('utf-8'))

def decodeBase64(text):
    return base64.b64decode(toBytes(text)).decode('utf-8')

def saveText(text, file, mode, encoding = 'utf-8') -> int:
    return open(file = file, mode = mode, encoding = encoding).write(text)

def takeFilled(*args) -> Any or None:
    return [var for var in args if var]

def takeClassDict(inst, attr : str, var : Dict = {}) -> Dict:
    return var | dict.fromkeys(getattr(inst, attr), inst)

def openfileforRead(file = None, text = '') -> str:
    return text.join([i for i in io.open(file, encoding='utf-8')])


if __name__ == '__main__':
    print(decodeBase64(
        'AAAAANGF0YPQuQ==\n'
    ))