#/==================================================================\#
#                                                                    #
#\==================================================================/#

#\==================================================================/#
#/========================/ installed libs \========================\#

import telebot, traceback, time, schedule

from telebot         import types
from multiprocessing import Process

#--------------------------\ project files /-------------------------#
import parsing, debug, path

from variables import * 
from emj       import *

#\==================================================================/#

TOKEN = '5394154180:AAFqG4zOj5ayVjDLn5Yeib4rGeh-p1TEo28'

bot = telebot.TeleBot(TOKEN)

#\==================================================================/#

#\==================================================================/#
directory = parsing.Directory()
"""

### Directory

\# Search: [<catalog>]   

> Added: Number    
> BoundedBy: [[<coordinates>]]

"""

catalog = parsing.Catalog([
    'автомойка Центральный административный округ',
    'автомойка Северный административный округ'
])

status = f'{EMJ_RAISING_HAND} Начать'

handling_process = None
#\==================================================================/#

#\==================================================================/#
@bot.message_handler(commands=['start'])
def start(msg):
    try:
        keyboard = set_keyboard([status, f'{EMJ_NOTE} Категории', f'{EMJ_DISK} Каталог'])
        bot.send_message(msg.chat.id, f'{EMJ_HOUSE} Вы в главном меню!', reply_markup=keyboard)

    except:
        debug.saveLogs(
            f"[start]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#
def init_handling(_id : int):
    global directory, handling_process

    handling_process = Process(target = handle_updates, args=(_id, directory))
    handling_process.start()

def kill_handling():
    global handling_process

    if handling_process:
        handling_process.kill()

def send_directory(msg):
    global directory
    bot.send_message(msg.chat.id, directory)

def config_directory(msg):
    global status, directory, handling_process

    if len(catalog):
        bot.send_message(msg.chat.id, f'Получение данных по {catalog}', reply_markup=types.ReplyKeyboardRemove())
        directory.set_directory(catalog)
        if directory.parsing:
            status = f'{EMJ_CROSS} Остановить'
            keyboard = set_keyboard([status, f'{EMJ_NOTE} Категории', f'{EMJ_DISK} Каталог'])
            bot.send_message(msg.chat.id, f'Запросы получены!', reply_markup=keyboard)
        else:
            status = f'{EMJ_RAISING_HAND} Начать'
            directory.clear()
            bot.send_message(msg.chat.id, f'Парсинг не доступен! Количество запросов превысило 500 за день.')
            start(msg)
    
    else:
        bot.send_message(msg.chat.id, 'Для запуска добавьте категории в каталог. Категории -> Добавить.')

    init_handling(msg.chat.id)

def show_categories_keyboard(msg):
    keyboard = set_keyboard([f'{EMJ_BACK_ARROW} Назад', f'{EMJ_MAGNIFIER} Показать', f'{EMJ_PLUS} Добавить', f'{EMJ_BASKET} Удалить'])
    bot.send_message(msg.chat.id, f'{EMJ_FILE_BOX} Вы в разделе "Категории"', reply_markup=keyboard)

def show_categories(msg):
    global directory

    bot.send_message(msg.chat.id, f'Загруженный: \n{directory.catalog}')
    bot.send_message(msg.chat.id, f'Полный:      \n{catalog}')

def stop_handling(msg):
    global status, handling_process

    status = f'{EMJ_RAISING_HAND} Начать'

    directory.clear()

    kill_handling()

    keyboard = set_keyboard([status, f'{EMJ_NOTE} Категории', f'{EMJ_DISK} Каталог'])
    bot.send_message(msg.chat.id, f'{EMJ_CROSS} Мониторинг запросов отключен!', reply_markup=keyboard)

def _add_category(msg):
    global status, directory, catalog

    catalog += msg.text
    bot.send_message(msg.chat.id, f'{EMJ_DONE} Категория: "{msg.text}" добавлена в каталог!')
    if status == f'{EMJ_CROSS} Остановить':

        kill_handling()

        bot.send_message(msg.chat.id, f'Получение данных по {msg.text}', reply_markup=types.ReplyKeyboardRemove())
        directory.set_items(msg.text)
        if directory.parsing:
            keyboard = set_keyboard([status, f'{EMJ_NOTE} Категории', f'{EMJ_DISK} Каталог'])
            bot.send_message(msg.chat.id, f'Запросы получены!', reply_markup=keyboard)
            init_handling(msg.chat.id)
        else:
            status = f'{EMJ_RAISING_HAND} Начать'
            bot.send_message(msg.chat.id, f'Парсинг не доступен! Количество запросов превысило 500 за день.')
            start(msg)


def add_category(msg):
    waiter = bot.send_message(msg.chat.id, 'Введите категорию для добавления в каталог поиска:')
    bot.register_next_step_handler(waiter, _add_category)

def _del_category(msg):
    global status, directory, catalog
    
    if msg.text in catalog: 
        del catalog[msg.text]
        bot.send_message(msg.chat.id, f'{EMJ_BASKET} Категория: "{msg.text}" удалена из каталога!')

    else: bot.send_message(msg.chat.id, f'{EMJ_CROSS} Категория: "{msg.text}" нет в каталоге!')

    if msg.text in directory.catalog:
        del directory.catalog[msg.text]

        if status == f'{EMJ_CROSS} Остановить': 
            kill_handling()

            directory.clear()

            config_directory(msg)

def del_category(msg):
    waiter = bot.send_message(msg.chat.id, 'Введите категорию для удаления из каталога поиска:')
    bot.register_next_step_handler(waiter, _del_category)

KEYBOARD_FUNC = {
    f'{EMJ_DISK} Каталог'        : send_directory,
    f'{EMJ_RAISING_HAND} Начать' : config_directory,
    f'{EMJ_CROSS} Остановить'    : stop_handling,
    f'{EMJ_NOTE} Категории'      : show_categories_keyboard,
    f'{EMJ_MAGNIFIER} Показать'  : show_categories,
    f'{EMJ_BACK_ARROW} Назад'    : start,
    f'{EMJ_PLUS} Добавить'       : add_category,
    f'{EMJ_BASKET} Удалить'      : del_category
}

@bot.message_handler(content_types=['text'])
def input_keyboard(msg):

    try:
        if msg.text in KEYBOARD_FUNC: KEYBOARD_FUNC[msg.text](msg)

    except:
        debug.saveLogs(
            f"[input_keyboard]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        pass

    except:
        debug.saveLogs(
            f"[call]-->{traceback.format_exc()}",
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#       

def handle_updates(_id : int, _directory : parsing.Directory):

    schedule.every(
        UPDATE_DELAY
    ).seconds.do(send_request, _id, _directory)

    while True:
        schedule.run_pending()
        time.sleep(1)

def send_request(_id : int, _directory : parsing.Directory):

    try:

        items = _directory.update()
        if _directory.parsing:
            txt = f'За последнии 20 мин добавленно: {len(items)} новых организаций\n'
            for ind, item in zip(range(len(items)), items):
                txt += f'{ind + 1}. {item}\n'
        else:
            txt = f'Парсинг не доступен! Количество запросов превысило 500 за день.'
        bot.send_message(_id, txt)
    
    except:
        debug.saveLogs(
            f"[UpdateHandler]-->{traceback.format_exc()}",
            path.log_file
        )
#\==================================================================/#


#\==================================================================/#

def get_keyboard(resize = True):
    return types.ReplyKeyboardMarkup(resize_keyboard = resize)

def get_btn(text):
    return types.KeyboardButton(text)

def gen_btns(btns):
    return (get_btn(txt) for txt in btns)

def set_keyboard(btns):
    key = get_keyboard()
    key.add(*gen_btns(btns))
    return key
#\==================================================================/#


#\==================================================================/#
if __name__ == '__main__':
    try: 
        bot.polling(none_stop=True)
    except:
        debug.saveLogs(
            f"[error]-->{traceback.format_exc()}", 
            path.log_file
        )
#\==================================================================/#
