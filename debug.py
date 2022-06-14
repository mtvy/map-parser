import utility, datetime

def saveLogs(text, file) -> int:
    return utility.saveText(f'\nDate: {datetime.datetime.now()}\n\n{text}', file, 'a')