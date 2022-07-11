import utility, datetime, path

def saveLogs(text : str, file : str = path.log_file) -> int:
    return utility.saveText(f'\nDate: {datetime.datetime.now()}\n\n{text}', file, 'a')